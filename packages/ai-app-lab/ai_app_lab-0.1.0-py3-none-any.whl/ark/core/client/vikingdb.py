import os
from typing import Any, Optional

from volcengine.viking_db import VikingDBService

from ark.core.client import Client


class VikingDBClient(Client, VikingDBService):
    def __init__(
        self,
        host: str = "api-vikingdb.volces.com",
        region: str = "cn-north-1",
        ak: Optional[str] = None,
        sk: Optional[str] = None,
        **kwargs: Any,
    ):
        super().__init__(
            host=host,
            region=region,
            **kwargs,
        )
        self.set_ak(ak or os.getenv("VOLC_ACCESSKEY"))
        self.set_sk(sk or os.getenv("VOLC_SECRETKEY"))
