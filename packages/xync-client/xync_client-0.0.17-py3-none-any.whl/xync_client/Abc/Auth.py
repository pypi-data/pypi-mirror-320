import logging
from abc import abstractmethod

from aiohttp import ClientResponse
from aiohttp.http_exceptions import HttpProcessingError
from xync_schema.models import Agent, Ex

from xync_client.Abc.Base import BaseClient


class BaseAuthClient(BaseClient):
    def __init__(self, agent: Agent | Ex):
        # dirty hack for multi-inheritance
        self.agent = agent if isinstance(agent, Agent) else agent.agents[0]
        ex = agent if isinstance(agent, Ex) else agent.ex
        self.headers.update(self.agent.auth)
        self.meth = {
            "GET": self._get,
            "POST": self._post,
            "DELETE": self._delete,
        }
        super().__init__(ex)

    @abstractmethod
    async def _get_auth_hdrs(self) -> dict[str, str]: ...

    async def login(self) -> None:
        auth_hdrs: dict[str, str] = await self._get_auth_hdrs()
        self.session.headers.update(auth_hdrs)

    async def _post(self, url: str, data: dict = None, data_key: str = None):
        dt = {"json" if isinstance(data, dict) else "data": data}
        resp = await self.session.post(url, **dt, headers=self._prehook(data))
        return await self._proc(resp, data_key, data)

    async def _proc(self, resp: ClientResponse, data_key: str = None, body: dict | str = None) -> dict | str:
        try:
            return await super()._proc(resp, data_key)
        except HttpProcessingError as e:
            if e.code == 401:
                logging.warning(e)
                await self.login()
                res = await self.meth[resp.method](resp.url.path, body, data_key=data_key)
                return res
