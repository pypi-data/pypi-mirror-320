from typing import Optional

from pydantic import BaseModel, Field

from ark.core._api.deprecation import deprecated
from ark.core.client import Client, get_client_pool
from ark.core.client.maas import ArkClient
from ark.core.idl.maas_protocol import SearchRequest, SearchResponse


def _get_ark_client() -> Optional[Client]:
    client_pool = get_client_pool()
    client = client_pool.get_client("chat")
    if not client:
        client = ArkClient()
    return client


@deprecated(
    since="0.1.11", removal="0.2.0", alternative_import="ark.component.v3.search.Search"
)
class Search(BaseModel):
    endpoint_id: str
    client: ArkClient = Field(default_factory=_get_ark_client)

    class Config:
        arbitrary_types_allowed = True

    async def arun(self, request: SearchRequest) -> SearchResponse:
        return await self.client.async_search(self.endpoint_id, request)
