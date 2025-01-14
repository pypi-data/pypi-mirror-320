import json
import logging
from typing import List

from ark.component.reader._reader import Reader
from ark.core.rag import KnowledgeChunk, KnowledgeDoc
from ark.core.task import task

logging.basicConfig(
    level=logging.INFO, format="[%(asctime)s][%(levelname)s] %(message)s"
)
LOGGER = logging.getLogger(__name__)


class FeishuReader(Reader):
    """
    FeishuReader for knowledge base
    """

    def _rechunk(
        self,
        lark_chunks: List[str],
        full_text_chunk: KnowledgeChunk,
        chunk_merge_separator: str = "\n",
        need_encode_title: bool = False,
        custom_prefix: str = "",
    ) -> List[KnowledgeChunk]:
        encode_text_prefix = custom_prefix
        title = full_text_chunk.scalars["title"]
        doc_id = full_text_chunk.scalars["doc_id"]
        tos_url = full_text_chunk.scalars["tos_url"]
        file_name = full_text_chunk.scalars["file_name"]
        full_text_len = full_text_chunk.scalars["full_text_len"]
        primary_key = self.config.primary_key.get("name", "")
        vector_key = self.config.vector.get("name", "")

        if need_encode_title:
            encode_text_prefix = f"{custom_prefix}标题:{title}\n"
        new_chunk_list = []
        new_encode_text = encode_text_prefix
        new_origin_text = ""
        new_chunk_page_num = []
        new_chunk_id = 0

        chunk_type = "raw_chunk"
        for chunk_id, chunk in enumerate(lark_chunks):
            chunk_root = json.loads(chunk)
            if chunk_root["type"] not in [
                "section-text",
                "section-title",
                "footnote",
            ]:
                continue
                # title：全文大标题, section-title：章节标题, section-text：章节内容
                # image：图片, table：表格, header：页眉, footer：页脚
                # footnote：脚注, caption：图/表描述, toc：目录, others：其他
            cur_text = chunk_root.get("text")
            cur_encode_text_len = len(new_encode_text + cur_text)

            if (
                new_encode_text == encode_text_prefix
                or cur_encode_text_len <= self.split_size
            ):
                # Case1: new_encode_text == chunk_prefix, len(cur_text) exceed limit
                # Case2: cur_encode_text_len < limit
                new_encode_text = new_encode_text + cur_text + chunk_merge_separator
                new_origin_text = new_origin_text + cur_text + chunk_merge_separator
                if isinstance(chunk_root.get("positions"), dict) and chunk_root.get(
                    "positions"
                ).get("page_no"):
                    page_no_list = chunk_root["positions"]["page_no"]
                    if isinstance(page_no_list, list):
                        new_chunk_page_num.extend(page_no_list)
                    elif isinstance(page_no_list, int):
                        new_chunk_page_num.append(page_no_list)
                if chunk_id + 1 < len(lark_chunks):
                    # Case: not last chunk, continue
                    continue

            # cur_encode_text_len exceed limit or last chunk process
            page_num_str = ",".join(sorted([str(x) for x in set(new_chunk_page_num)]))
            new_chunk = KnowledgeChunk(
                primary_key=(
                    primary_key,
                    "#".join([doc_id, chunk_type, str(chunk_id)]),
                ),
                vector=(
                    vector_key,
                    new_encode_text[: self.config.vector_text_len_limit],
                ),
                scalars={
                    "doc_id": doc_id,
                    "chunk_id": new_chunk_id,
                    "chunk_type": chunk_type,
                    "text": new_origin_text,
                    "tos_url": tos_url,
                    "file_name": file_name,
                    "chunk_len": len(new_origin_text),
                    "full_text_len": full_text_len,
                    "title": title,
                    "page_nums": page_num_str,
                },
                knowledge_schema=self.config,
            )
            new_chunk_list.append(new_chunk)
            new_encode_text = encode_text_prefix
            new_origin_text = ""
            new_chunk_page_num = []
            new_chunk_id += 1

        return new_chunk_list

    @task()
    def load(self, doc: KnowledgeDoc) -> List[KnowledgeChunk]:
        LOGGER.info("FeishuReader load started")
        if not doc.remote_path:
            raise ValueError("doc.remote_path is empty")
        file_name = str(doc.remote_path).split("/")[-1]
        lark_chunks = self._parse_doc(doc)
        title = ""
        chunk_text = []
        for chunk in lark_chunks:
            chunk_root = json.loads(chunk)
            chunk_text.append(chunk_root["text"])
            if title == "" and chunk_root["type"] == "title":
                title = chunk_root.get("text", "")
        full_text = "\n".join(chunk_text)

        primary_key = self.config.primary_key.get("name", "")
        vector_key = self.config.vector.get("name", "")
        chunk_type = "full_text"
        chunk_id = -1
        full_text_chunk = KnowledgeChunk(
            primary_key=(
                primary_key,
                "#".join([doc.doc_id, chunk_type, str(chunk_id)]),
            ),
            vector=(
                vector_key,
                file_name + "\n" + full_text[: self.split_size - len(file_name) - 1],
            ),
            scalars={
                "doc_id": doc.doc_id,
                "chunk_id": -1,
                "chunk_type": chunk_type,
                "text": full_text,
                "tos_url": doc.remote_path,
                "file_name": file_name,
                "chunk_len": len(full_text),
                "full_text_len": len(full_text),
                "title": title,
                "page_nums": "all",
            },
            knowledge_schema=self.config,
        )
        chunks = self._rechunk(lark_chunks, full_text_chunk)
        LOGGER.info("load finished, splitted to %d chunks", len(chunks))
        LOGGER.info("FeishuReader load finished")
        return [full_text_chunk] + chunks
