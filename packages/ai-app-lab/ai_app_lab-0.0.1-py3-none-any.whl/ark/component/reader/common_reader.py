import logging
from typing import Any, List, Optional, Tuple

from langchain.text_splitter import RecursiveCharacterTextSplitter
from volcengine.Credentials import Credentials

from ark.component.reader.base_reader import BaseReader
from ark.core.rag import DocType, KnowledgeChunk, KnowledgeDoc, KnowledgeSchema
from ark.core.task import task
from ark.core.utils.tos import download_tos_file

logging.basicConfig(
    level=logging.INFO, format="[%(asctime)s][%(levelname)s] %(message)s"
)
LOGGER = logging.getLogger(__name__)


def read_pdf(file_path: str) -> Tuple[str, List[str]]:
    try:
        from pypdf import PdfReader
    except ImportError:
        raise ImportError(
            "Could not import pypdf python package. "
            "Please install it with `pip install pypdf`."
        )

    reader = PdfReader(file_path)
    full_text = ""
    pages = []
    for page in reader.pages:
        full_text += page.extract_text()
        pages.append(page.extract_text())
    return full_text, pages


def read_docx(file_path: str) -> Tuple[str, List[Any]]:
    try:
        from docx import Document
    except ImportError:
        raise ImportError(
            "Could not import docx python package. "
            "Please install it with `pip install python-docx`."
        )
    document = Document(file_path)
    full_text = ""
    paragraphs = []
    for paragraph in document.paragraphs:
        full_text += paragraph.text + "\n"
        paragraphs.append(paragraph)
    return full_text, paragraphs


def read_txt(file_path: str, encoding: str = "utf-8") -> Tuple[str, List[str]]:
    lines = []
    with open(file_path, "r", encoding=encoding) as fp:
        lines = [line for line in fp.readlines()]
    full_text = "\n".join(lines)
    return full_text, lines


def read_html(file_path: str, encoding: str = "utf-8") -> Tuple[str, List[str]]:
    import re

    from bs4 import BeautifulSoup

    with open(file_path, "r", encoding=encoding) as fp:
        soup = BeautifulSoup(fp, "html.parser")

    parsed_text = soup.get_text()
    # 处理 html 常见的一些 case
    parsed_text = re.sub(r"[\u3000\u00A0\u2000-\u200B]", " ", parsed_text)
    parsed_text = parsed_text.replace("\r\n", "\n")
    parsed_text = parsed_text.replace(" \n", "\n")
    parsed_text = re.sub(r"\n{3,}", "\n\n", parsed_text)
    return parsed_text, parsed_text.split("\n\n")


class CommonReader(BaseReader):
    """
    Reader for knowledge base
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

    def _simple_split(self, full_text: str, split_size: int) -> List[str]:
        text_pieces = []
        for i in range(0, len(full_text), split_size):
            text_piece = full_text[i : i + split_size]
            text_pieces.append(text_piece)
        return text_pieces

    def _recursive_split(self, full_text: str, split_size: int) -> List[str]:
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=split_size, chunk_overlap=0
        )
        lc_splited = text_splitter.create_documents([full_text])
        text_pieces = []
        for lc_doc in lc_splited:
            text_pieces.append(lc_doc.page_content)
        return text_pieces

    @task()
    def load(
        self,
        doc: KnowledgeDoc,
        split_method: str = "recursive",
        cache_path: str = "/tmp/",
    ) -> List[KnowledgeChunk]:
        LOGGER.info("CommonReader load started")
        if not doc.local_path:
            doc.local_path = download_tos_file(
                url=str(doc.remote_path),
                credentials=self.credentials,
                cache_path=cache_path,
                region=self.region,
            )
        file_name = doc.local_path.split("/")[-1]
        if doc.type == DocType.PDF:
            full_text, _ = read_pdf(doc.local_path)
        elif doc.type == DocType.TXT or doc.type == DocType.MARKDOWN:
            full_text, _ = read_txt(doc.local_path, encoding="utf-8")
        elif doc.type == DocType.DOC or doc.type == DocType.DOCX:
            full_text, _ = read_docx(doc.local_path)
        elif doc.type == DocType.HTML:
            full_text, _ = read_html(doc.local_path)
        else:
            raise ValueError(f"Invalid doc type {doc.type}")
        primary_key = self.config.primary_key.get("name", "")
        vector_key = self.config.vector.get("name", "")
        full_text_chunk = KnowledgeChunk(
            primary_key=(primary_key, "#".join([doc.doc_id, "full_text", str(-1)])),
            vector=(
                vector_key,
                file_name + "\n" + full_text[: self.split_size - len(file_name) - 1],
            ),
            scalars={
                "doc_id": doc.doc_id,
                "chunk_id": -1,
                "chunk_type": "full_text",
                "text": full_text,
                "tos_url": doc.remote_path,
                "file_name": file_name,
                "chunk_len": len(full_text),
                "full_text_len": len(full_text),
            },
            knowledge_schema=self.config,
        )
        if split_method == "simple":
            text_pieces = self._simple_split(full_text, self.split_size)
        elif split_method == "recursive":
            text_pieces = self._recursive_split(full_text, self.split_size)
        chunk_type = "raw_chunk"
        chunks = [
            KnowledgeChunk(
                primary_key=(primary_key, "#".join([doc.doc_id, chunk_type, str(i)])),
                vector=(vector_key, text_piece[: self.split_size]),
                scalars={
                    "doc_id": doc.doc_id,
                    "chunk_id": i,
                    "chunk_type": chunk_type,
                    "text": text_piece,
                    "tos_url": doc.remote_path,
                    "file_name": file_name,
                    "chunk_len": len(text_piece),
                    "full_text_len": len(full_text),
                },
                knowledge_schema=self.config,
            )
            for i, text_piece in enumerate(text_pieces)
        ]
        LOGGER.info("load finished, splitted to %d chunks", len(chunks))
        LOGGER.info("CommonReader load finished")
        return [full_text_chunk] + chunks
