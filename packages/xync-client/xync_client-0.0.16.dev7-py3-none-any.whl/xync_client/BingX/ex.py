from asyncio import run

from x_model import init_db
from xync_client.Abc.Base import DictOfDicts, FlatDict
from xync_schema import models
from xync_schema.models import Ex

from xync_client.Abc.Ex import BaseExClient
from xync_client.BingX.base import BaseBingXClient
from xync_client.loader import PG_DSN


class ExClient(BaseExClient, BaseBingXClient):
    headers: dict[str, str] = {
        "app_version": "9.0.5",
        "device_id": "ccfb6d50-b63b-11ef-b31f-ef1f76f67c4e",
        "lang": "ru-RU",
        "platformid": "30",
    }

    # 19: Список всех платежных методов на бирже
    async def pms(self) -> DictOfDicts:  # {pm.exid: pm}
        curs = await self.curs()
        pp = {}
        for _id, cur in curs.items():
            pms = await self._get("/api/c2c/v1/advert/payment/list", params={"fiat": cur})
            [pp.update({p["id"]: {"name": p["name"], "logo": p["icon"]}}) for p in pms["data"]["paymentMethodList"]]
        return pp

    # 20: Список поддерживаемых валют на BingX
    async def curs(self) -> FlatDict:  # {cur.exid: cur.ticker}
        params = {
            "type": "1",
            "asset": "USDT",
            "coinType": "2",
        }
        curs = await self._get("/api/c2c/v1/common/supportCoins", params=params)
        return {cur["id"]: cur["name"] for cur in curs["data"]["coins"]}

    # 21: cur_pms_map на BingX
    async def cur_pms_map(self):
        coins = await self.coins()
        curs = await self.curs()
        return {}

    # 22: Монеты на BingX
    async def coins(self) -> FlatDict:
        return {1 : "USDT"}

    # 23: Список пар валюта/монет
    async def pairs(self) -> FlatDict:
        coins = await self.coins()
        curs = await self.curs()
        result = {cur: set(coins) for cur in curs.values()}
        return result

    # 24: ads
    async def ads(self, coin_exid: str, cur_exid: str, is_sell: bool, pm_exids: list[str | int] = None) -> FlatDict:
        params = {
            "type": "1",
            "fiat": self.cur_exid,
            "asset": self.coin_exid,
            "amount": "",
            "hidePaymentInfo": "",
            "payMethodId": self.pm_exids,
            "isUserMatchCondition": self.is_sell,
        }

        ads = await self._get(
            "/api/c2c/v1/advert/list",
            params=params,
        )

        return ads


async def main():
    _ = await init_db(PG_DSN, models, True)
    bg = await Ex.get(name="BingX")
    cl = ExClient(bg)
    await cl.curs()
    # pms = await cl.pms()
    await cl.close()


if __name__ == "__main__":
    run(main())
