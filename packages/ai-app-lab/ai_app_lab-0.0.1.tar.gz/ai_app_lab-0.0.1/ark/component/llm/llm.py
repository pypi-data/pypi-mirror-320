from typing import AsyncIterator, Optional

from ark.component.llm.utils import get_maas_client_v2
from ark.core._api.deprecation import deprecated
from ark.core.idl.maas_protocol import (
    MaasChatRequest,
    MaasChatResponse,
    MaasClassificationRequest,
    MaasClassificationResponse,
    MaasEmbeddingsRequest,
    MaasEmbeddingsResponse,
    MaasTokenizeRequest,
    MaasTokenizeResponse,
)
from ark.core.task import task
from ark.core.utils.types import dump_json


@deprecated(
    since="0.1.11",
    removal="0.2.0",
    alternative_import="ark.component.v3.llm.BaseEmbeddingLanguageModel",
)
@task()
async def embeddings(
    endpoint_id: str,
    request: MaasEmbeddingsRequest,
    host: str = "maas-api.ml-platform-cn-beijing.volces.com",
    region: str = "cn-beijing",
    ak: Optional[str] = None,
    sk: Optional[str] = None,
) -> MaasEmbeddingsResponse:
    maas = get_maas_client_v2(host, region, ak, sk)
    return await maas.async_embeddings(endpoint_id, dump_json(request))


@deprecated(
    since="0.1.11",
    removal="0.2.0",
    alternative_import="ark.component.v3.llm.BaseChatLanguageModel",
)
@task()
async def chat(
    endpoint_id: str,
    request: MaasChatRequest,
    host: str = "maas-api.ml-platform-cn-beijing.volces.com",
    region: str = "cn-beijing",
    ak: Optional[str] = None,
    sk: Optional[str] = None,
) -> MaasChatResponse:
    maas = get_maas_client_v2(host, region, ak, sk)
    req = dump_json(request)
    return await maas.async_chat(endpoint_id, req)


@deprecated(
    since="0.1.11",
    removal="0.2.0",
    alternative_import="ark.component.v3.llm.BaseChatLanguageModel",
)
@task()
async def streaming_chat(
    endpoint_id: str,
    request: MaasChatRequest,
    host: str = "maas-api.ml-platform-cn-beijing.volces.com",
    region: str = "cn-beijing",
    ak: Optional[str] = None,
    sk: Optional[str] = None,
) -> AsyncIterator[MaasChatResponse]:
    maas = get_maas_client_v2(host, region, ak, sk)
    return await maas.async_stream_chat(endpoint_id, dump_json(request))


@deprecated(
    since="0.1.11",
    removal="0.2.0",
    alternative_import="ark.component.v3.llm.BaseTokenizeLanguageModel",
)
@task()
async def tokenize(
    endpoint_id: str,
    request: MaasTokenizeRequest,
    host: str = "maas-api.ml-platform-cn-beijing.volces.com",
    region: str = "cn-beijing",
    ak: Optional[str] = None,
    sk: Optional[str] = None,
) -> MaasTokenizeResponse:
    maas = get_maas_client_v2(host, region, ak, sk)
    return await maas.async_tokenize(endpoint_id, dump_json(request))


@deprecated(
    since="0.1.11",
    removal="0.2.0",
    alternative_import="ark.component.v3.llm.BaseClassificationLanguageModel",
)
@task()
async def classification(
    endpoint_id: str,
    request: MaasClassificationRequest,
    host: str = "maas-api.ml-platform-cn-beijing.volces.com",
    region: str = "cn-beijing",
    ak: Optional[str] = None,
    sk: Optional[str] = None,
) -> MaasClassificationResponse:
    maas = get_maas_client_v2(host, region, ak, sk)
    return await maas.async_classification(endpoint_id, dump_json(request))
