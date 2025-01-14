from typing import Optional

from ark.core.client import ArkClient


def get_maas_client_v2(
    host: str = "maas-api.ml-platform-cn-beijing.volces.com",
    region: str = "cn-beijing",
    ak: Optional[str] = None,
    sk: Optional[str] = None,
) -> ArkClient:
    return ArkClient.get_instance_sync(host=host, region=region, ak=ak, sk=sk)
