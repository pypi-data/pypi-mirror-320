import json
import logging
import sys
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple

import requests
from volcengine.auth.SignerV4 import SignerV4
from volcengine.base.Request import Request
from volcengine.Credentials import Credentials

from ark.component.reader.base_reader import BaseReader
from ark.core.rag import DocType, KnowledgeDoc, KnowledgeSchema
from ark.core.utils.errors import FeishuParseException
from ark.core.utils.tos import pre_sign_tos_url

logging.basicConfig(
    level=logging.INFO, format="[%(asctime)s][%(levelname)s] %(message)s"
)
LOGGER = logging.getLogger(__name__)


class ChunkingStrategy(Enum):
    PLAIN_TEXT = 0
    PARAGRAPH = 1
    DOC_TREE = 2
    SEMANTIC = 3


class Reader(BaseReader):
    """
    Reader for knowledge base
    Need encryption
    """

    def __init__(
        self,
        config: KnowledgeSchema,
        credentials: Credentials,
        split_size: Optional[int] = None,
        region: str = "cn-beijing",
    ):
        self.config = config
        self.credentials = credentials
        self.region = region
        self.split_size = config.vector_text_len_limit
        if split_size:
            self.split_size = split_size
        if self.split_size > config.vector_text_len_limit:
            LOGGER.warning(
                "split_size:%d, > vector_text_len_limit:%d",
                split_size,
                config.vector_text_len_limit,
            )

    def _parse_res(self, response_str: str) -> Tuple[list, str]:
        # 返回的一个chunk示例：
        # {"id": 0, "type": "title", "label": "", "level": -1, "parent": -1,
        # "children": [1, 1125, 1130, 1135, 1140], "text": "xxx",
        # "positions": {"page_no": [0], "bbox": [[0.37, 0.18, 0.62, 0.21]]},
        # "table_detail": {}}
        response: dict = json.loads(response_str)
        chunking_results = response["data"]["DocChunkingResults"]
        if len(chunking_results) < 1:
            return [], ""
        chunk = chunking_results[0]
        status_string = chunk["Status"]
        status_map = json.loads(status_string)
        ret_code = status_map["code"]
        if ret_code != 0:
            LOGGER.error(
                "check response failed, ret_code: %s, Status: %s",
                ret_code,
                status_string,
            )
            raise FeishuParseException(status_string)
        return chunk["DocChunks"], ""

    def _prepare_request(
        self,
        method: str,
        path: str,
        params: Optional[Dict[str, Any]] = None,
        data: Optional[Dict[str, Any]] = None,
        doseq: int = 0,
    ) -> Request:
        if params:
            for key in params:
                if (
                    isinstance(type(params[key]), int)
                    or isinstance(type(params[key]), float)
                    or isinstance(type(params[key]), bool)
                ):
                    params[key] = str(params[key])
                elif sys.version_info[0] != 3:
                    if isinstance(type(params[key]), str):
                        params[key] = params[key].encode("utf-8")
                elif isinstance(type(params[key]), list):
                    if not doseq:
                        params[key] = ",".join(params[key])
        r = Request()
        r.set_shema("http")
        r.set_method(method)
        r.set_connection_timeout(10)
        r.set_socket_timeout(10)
        if params:
            r.set_query(params)
        r.set_path(path)
        if data is not None:
            r.set_body(json.dumps(data))
        # 生成签名
        credentials = Credentials(
            self.credentials.ak,
            self.credentials.sk,
            "air",
            "cn-north-1",
            session_token=self.credentials.session_token,
        )
        SignerV4.sign(r, credentials)
        return r

    def _get_chunking_result(
        self,
        url: str,
        doc_type: str,
        chunk_size: int = 500,
        strategy: ChunkingStrategy = ChunkingStrategy.SEMANTIC,
        parse_table_for_pdf: bool = False,
        verberos: bool = False,
    ) -> Tuple[list, str]:
        request_params = {
            "doc_infos": [
                {
                    "doc_type": doc_type,
                    "url": url,
                    "strategy": strategy.value,
                    "chunk_size": chunk_size,
                },
            ],
            "parse_table_for_pdf": parse_table_for_pdf,
        }
        method = "POST"
        path = "/api/doc_chunking"
        DOMAIN = "viking-knowledge-demo.byte-test.com"
        info_req = self._prepare_request(method, path, data=request_params)
        res = requests.request(
            method=method,
            url="https://{}{}".format(DOMAIN, path),
            headers=info_req.headers,
            data=info_req.body,
        )
        if verberos:
            LOGGER.info("res.text:%s", res.text)
        if res.status_code == 200:
            chunks, msg = self._parse_res(res.text)
            if msg:
                if verberos:
                    LOGGER.info("parse_res failed: %s", res.text)
                return [], msg
            return chunks, ""
        else:
            msg = "fetch url:{} error, res_code:{}, res_msg:{}".format(
                url, res.status_code, res.text
            )
            LOGGER.error(msg)
            return [], msg

    def _parse_doc(self, doc: KnowledgeDoc) -> List[str]:
        if doc.type == DocType.PDF:
            doc_type = "pdf"
        elif doc.type == DocType.TXT or doc.type == DocType.MARKDOWN:
            doc_type = "markdown"
        elif doc.type == DocType.DOC:
            doc_type = "doc"
        elif doc.type == DocType.DOCX:
            doc_type = "docx"
        else:
            raise ValueError(f"Invalid doc type {doc.type}")
        signed_url = pre_sign_tos_url(
            str(doc.remote_path), credentials=self.credentials, region=self.region
        )
        assert len(signed_url) > 0, "pre sign tos url failed"
        lark_chunks, _ = self._get_chunking_result(
            signed_url,
            doc_type,
            chunk_size=self.split_size,
            strategy=ChunkingStrategy.SEMANTIC,
        )
        return lark_chunks
