import logging
from urllib.parse import urlparse

import tos
from volcengine.Credentials import Credentials

logging.basicConfig(
    level=logging.INFO, format="[%(asctime)s][%(levelname)s] %(message)s"
)
LOGGER = logging.getLogger(__name__)


def download_tos_file(
    url: str,
    credentials: Credentials,
    cache_path: str = "/tmp/",
    region: str = "cn-beijing",
) -> str:
    result = urlparse(url)
    if result.scheme == "tos":
        endpoint = "tos-cn-beijing.volces.com"
        bucket_name = result.netloc
        object_key = result.path[1:]
        file_name = object_key.split("/")[-1]
        local_path = cache_path + file_name
    elif result.scheme == "http":
        endpoint = ".".join(result.netloc.split(".")[1:])
        bucket_name = result.netloc.split(".")[0]
        object_key = result.path[1:]
        file_name = object_key.split("/")[-1]
        local_path = cache_path + file_name
    else:
        raise ValueError("url is not tos or http")
    try:
        # 创建 TosClientV2 对象，对桶和对象的操作都通过 TosClientV2 实现
        client = tos.TosClientV2(credentials.ak, credentials.sk, endpoint, region)
        # 若 file_name 为目录则将对象下载到此目录下, 文件名为对象名
        client.get_object_to_file(bucket_name, object_key, local_path)
    except tos.exceptions.TosClientError as e:
        # 操作失败，捕获客户端异常，一般情况为非法请求参数或网络异常
        LOGGER.error(
            "fail with client error, message:%s, cause: %s", e.message, e.cause
        )
    except tos.exceptions.TosServerError as e:
        # 操作失败，捕获服务端异常，可从返回信息中获取详细错误信息
        LOGGER.error("fail with server error, code: %s", e.code)
        # request id 可定位具体问题，强烈建议日志中保存
        LOGGER.error("error with request id: %s", e.request_id)
        LOGGER.error("error with message: %s", e.message)
        LOGGER.error("error with http code: %s", e.status_code)
        LOGGER.error("error with ec: %s", e.ec)
        LOGGER.error("error with request url: %s", e.request_url)
    except Exception as e:
        LOGGER.error("fail with unknown error: %s", e)
    return local_path


def pre_sign_tos_url(
    url: str, credentials: Credentials, region: str = "cn-beijing"
) -> str:
    # tos开始的做个签名,http 开始的默认已经做过签名
    result = urlparse(url)
    if result.scheme == "tos":
        try:
            # 创建 TosClientV2 对象，对桶和对象的操作都通过 TosClientV2 实现
            client = tos.TosClientV2(
                credentials.ak,
                credentials.sk,
                security_token=credentials.session_token,
                endpoint="tos-cn-beijing.volces.com",
                region=region,
            )
            # 生成上传文件的签名url，有效时间为3600s
            out = client.pre_signed_url(
                tos.HttpMethodType.Http_Method_Get,
                bucket=result.netloc,
                key=result.path[1:],
                expires=3600,
            )
            signed_url = out.signed_url
            # LOGGER.info("signed_url: %s", signed_url)
            return signed_url

        except tos.exceptions.TosClientError as e:
            # 操作失败，捕获客户端异常，一般情况为非法请求参数或网络异常
            LOGGER.error(
                "fail with client error, message:%s, cause: %s", e.message, e.cause
            )
        except tos.exceptions.TosServerError as e:
            # 操作失败，捕获服务端异常，可从返回信息中获取详细错误信息
            LOGGER.error("fail with server error, code: %s", e.code)
            # request id 可定位具体问题，强烈建议日志中保存
            LOGGER.error("error with request id: %s", e.request_id)
            LOGGER.error("error with message: %s", e.message)
            LOGGER.error("error with http code: %s", e.status_code)
            LOGGER.error("error with ec: %s", e.ec)
            LOGGER.error("error with request url: %s", e.request_url)
        except Exception as e:
            LOGGER.error("fail with unknown error: %s", e)

    return ""
