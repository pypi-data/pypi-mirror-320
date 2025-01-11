import logging

import pytest
from xync_schema.enums import ExStatus, ExAction
from xync_schema.models import Ex, TestEx, Fiat
from xync_schema.pydantic import FiatNew

from xync_client.Abc.BaseTest import BaseTest
from xync_client.Abc.Agent import BaseAgentClient
from xync_client.Abc.Base import BaseClient, DictOfDicts, ListOfDicts
from xync_client.TgWallet.ex import ExClient


@pytest.mark.asyncio(loop_scope="session")
class TestAgent(BaseTest):
    @pytest.fixture(scope="class", autouse=True)
    async def clients(self) -> tuple[BaseClient, BaseClient]:
        exs = await Ex.filter(status__gt=ExStatus.plan).prefetch_related("agents__ex")
        agents = [[ag for ag in ex.agents if ag.auth][:2] for ex in exs]
        clients: list[tuple[BaseClient, BaseClient]] = [(t.client(), m.client()) for t, m in agents]
        yield clients
        [(await taker.close(), await maker.close()) for taker, maker in clients]

    # 0
    async def test_get_orders(self, clients: list[BaseAgentClient]):
        for taker, maker in clients:
            get_orders: ListOfDicts = await taker.get_orders()
            ok = self.is_list_of_dicts(get_orders, False)
            t, _ = await TestEx.update_or_create({"ok": ok}, ex_id=taker.agent.ex_id, action=ExAction.get_orders)
            assert t.ok, "No get orders"
            logging.info(f"{taker.agent.ex_id}:{ExAction.get_orders.name} - ok")

    # 1
    async def test_order_request(self, clients: list[BaseAgentClient]):
        for taker, maker in clients:
            await taker.agent.fetch_related("ex", "ex__agents")
            ex_client: ExClient = taker.agent.ex.client()
            ads = await ex_client.ads("NOT", "RUB", False)
            for ad in ads:
                order_request: dict | bool = await taker.order_request(ad["id"], ad["orderAmountLimits"]["min"])
                if order_request:
                    break
            ok = order_request["status"] == "SUCCESS"
            t, _ = await TestEx.update_or_create({"ok": ok}, ex_id=taker.agent.ex_id, action=ExAction.order_request)
            assert t.ok, "No get orders"
            logging.info(f"{taker.agent.ex_id}:{ExAction.order_request.name} - ok")

    # 25
    async def test_my_fiats(self, clients: list[BaseAgentClient]):
        for taker, maker in clients:
            my_fiats: DictOfDicts = await taker.my_fiats()
            ok = self.is_dict_of_dicts(my_fiats)
            t, _ = await TestEx.update_or_create({"ok": ok}, ex_id=taker.agent.ex_id, action=ExAction.my_fiats)
            assert t.ok, "No my fiats"
            logging.info(f"{taker.agent.ex_id}:{ExAction.my_fiats.name} - ok")

    # 26
    async def test_fiat_new(self, clients: list[BaseAgentClient]):
        for taker, maker in clients:
            fn = FiatNew(cur_id=11, pm_id=22, detail="123456789")
            fiat_new: Fiat.pyd() = await taker.fiat_new(fn)
            ok = fiat_new["status"] == "SUCCESS"
            t, _ = await TestEx.update_or_create({"ok": ok}, ex_id=taker.agent.ex_id, action=ExAction.fiat_new)
            assert t.ok, "No add fiat"
            logging.info(f"{taker.agent.ex_id}:{ExAction.fiat_new.name} - ok")

    # 27
    async def test_fiat_upd(self, clients: list[BaseAgentClient]):
        for taker, maker in clients:
            my_fiats = await taker.my_fiats()
            fiats = [fiat for fiat in my_fiats.values()]
            fiat_upd: Fiat.pyd() = await taker.fiat_upd(fiat_id=fiats[-1]["id"], detail="347890789")
            ok = fiat_upd["status"] == "SUCCESS"
            t, _ = await TestEx.update_or_create({"ok": ok}, ex_id=taker.agent.ex_id, action=ExAction.fiat_upd)
            assert t.ok, "No upd fiat"
            logging.info(f"{taker.agent.ex_id}:{ExAction.fiat_upd.name} - ok")
