from abc import abstractmethod

from aiohttp import ClientSession
from xync_schema.models import Agent, Ex

from xync_client.Abc.Base import FlatDict

from xync_client.Abc.Auth import BaseAuthClient


class BaseAssetClient(BaseAuthClient):
    def __init__(self, agent: Agent):
        self.agent: Agent = agent
        ex: Ex = agent.ex
        self.headers.update(self.agent.auth)
        self.meth = {
            "GET": self._get,
            "POST": self._post,
            "DELETE": self._delete,
        }
        self.session = ClientSession("https://" + ex.host, headers=self.headers, cookies=self.cookies)

    # 39: Балансы моих монет
    @abstractmethod
    async def assets(self) -> FlatDict: ...
