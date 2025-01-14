import os
from typing import Optional

from tos.clientv2 import TosClientV2
from tos.enum import HttpMethodType
from tos.exceptions import TosClientError

from ark.core.utils.errors import OperationDenied


class TosSDKDownloader(TosClientV2):
    def __init__(
        self,
        ak: str = "",
        sk: str = "",
        endpoint: str = "https://tos-cn-beijing.volces.com",
        region: str = "cn-beijing",
        bucket_name: Optional[str] = "ark-sdk-cn-beijing",
        sdk_prefix: Optional[str] = "python_sdk",
    ):
        ak = ak or os.getenv("VOLC_ACCESSKEY") or ""
        sk = sk or os.getenv("VOLC_SECRETKEY") or ""

        super(TosSDKDownloader, self).__init__(ak, sk, endpoint, region)

        self.bucket_name = bucket_name or "ark-sdk-cn-beijing"
        self.sdk_prefix = sdk_prefix or "python_sdk"

    def get_sdk_presign_url(self, sdk_wheel: str) -> str:
        res = self.pre_signed_url(
            http_method=HttpMethodType.Http_Method_Get,
            bucket=self.bucket_name,
            key=os.path.join(self.sdk_prefix, sdk_wheel),
        )
        return res.signed_url

    def get_latest_sdk_wheel(self) -> str:
        try:
            result = self.list_objects(
                bucket=self.bucket_name, prefix=self.sdk_prefix, max_keys=1000
            )

            latest_sdk = max(result.contents, key=lambda item: item.last_modified)
            latest_sdk_wheel = latest_sdk.key.lstrip(self.sdk_prefix + "/")
            return latest_sdk_wheel
        except TosClientError as e:
            raise OperationDenied(f"List sdks from tos failed: {e}")
        except Exception:
            raise

    def download_sdk(self, sdk_version: Optional[str] = None) -> bytes:
        try:
            sdk_version = sdk_version or self.get_latest_sdk_wheel()
            object_stream = self.get_object(bucket=self.bucket_name, key=sdk_version)
            sdk_wheel = object_stream.read()
            return sdk_wheel
        except TosClientError as e:
            raise OperationDenied(f"Download sdk from tos failed: {e}")
        except Exception:
            raise
