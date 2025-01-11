import json
import logging
from typing import Callable, Dict, List, Optional

from volcengine.Credentials import Credentials

from ark.component.reader.base_reader import BaseReader
from ark.core.rag import DocType, KnowledgeChunk, KnowledgeDoc, KnowledgeSchema
from ark.core.task import task
from ark.core.utils.tos import download_tos_file

logging.basicConfig(
    level=logging.INFO, format="[%(asctime)s][%(levelname)s] %(message)s"
)
LOGGER = logging.getLogger(__name__)


def read_csv(file_path: str, encoding: str = "utf-8") -> List[Dict]:
    import pandas as pd

    df = pd.read_csv(file_path, encoding=encoding)
    return df.to_dict(orient="records")


def read_jsonl(file_path: str, encoding: str = "utf-8") -> List[Dict]:
    records: List[dict] = []
    err_cnt = 0
    with open(file_path, "r", encoding=encoding) as f:
        for line in f.readlines():
            try:
                r: dict = json.loads(line)
            except Exception:
                err_cnt += 1
            records.append(r)
        if err_cnt > 0:
            LOGGER.warning("json decode error_cnt: %d", err_cnt)
    return records


class StructReader(BaseReader):
    def __init__(
        self,
        config: KnowledgeSchema,
        credentials: Credentials,
        region: str = "cn-beijing",
    ):
        self.config = config
        self.credentials = credentials
        self.region = region

    @task()
    def load(
        self,
        doc: KnowledgeDoc,
        encode_fields: List[str],
        field_map: Optional[Dict[str, str]] = None,
        field_parser: Optional[Dict[str, Callable[[str], str]]] = None,
        cache_path: str = "/tmp/",
        only_save_saclar_fields: bool = True,
    ) -> List[KnowledgeChunk]:
        LOGGER.info("StructReader load started")
        if not doc.local_path:
            doc.local_path = download_tos_file(
                url=str(doc.remote_path),
                credentials=self.credentials,
                cache_path=cache_path,
                region=self.region,
            )
        file_name = doc.local_path.split("/")[-1]
        if doc.type == DocType.CSV:
            records = read_csv(doc.local_path, encoding=doc.encoding)
        elif doc.type == DocType.JSONL:
            records = read_jsonl(doc.local_path, encoding=doc.encoding)
        else:
            raise ValueError(f"Invalid doc type {doc.type}")

        if field_parser:
            for rec in records:
                for k in rec:
                    if k not in field_parser:
                        continue
                    try:
                        parser = field_parser[k]
                        rec[k] = parser(rec[k])
                    except Exception:
                        LOGGER.error("field:%s parse error")

        if field_map:
            new_records = []
            for rec in records:
                new_records.append(
                    {field_map.get(key, key): value for key, value in rec.items()}
                )
            records = new_records

        chunk_type = "raw_chunk"
        chunks = []
        primary_key = self.config.primary_key.get("name", "")
        vector_key = self.config.vector.get("name", "")
        valid_keys = set([data.get("name") for data in self.config.scalars])
        for i, record in enumerate(records):
            valid_dict = {
                "doc_id": doc.doc_id,
                "chunk_id": i,
                "chunk_type": chunk_type,
                "tos_url": doc.remote_path,
                "file_name": file_name,
            }
            if only_save_saclar_fields:
                valid_dict.update({k: v for k, v in record.items() if k in valid_keys})
            else:
                valid_dict.update(record)

            encode_text = ""
            for encode_field in encode_fields:
                if encode_field in valid_dict:
                    encode_text += f"{encode_field}:{valid_dict[encode_field]}\n"

            chunks.append(
                KnowledgeChunk(
                    primary_key=(
                        primary_key,
                        "#".join([doc.doc_id, chunk_type, str(i)]),
                    ),
                    vector=(
                        vector_key,
                        encode_text[: self.config.vector_text_len_limit],
                    ),
                    scalars=valid_dict,
                    knowledge_schema=self.config,
                )
            )
        LOGGER.info("load finished, splitted to %d chunks", len(chunks))
        LOGGER.info("StructReader load finished")
        return chunks
