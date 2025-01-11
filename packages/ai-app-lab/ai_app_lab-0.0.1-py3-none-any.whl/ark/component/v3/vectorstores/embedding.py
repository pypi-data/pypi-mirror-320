import asyncio
import logging
from typing import List

import numpy as np
from volcenginesdkarkruntime._exceptions import ArkAPIError

from ark.component.v3.llm.base import BaseEmbeddingLanguageModel
from ark.core.rag import KnowledgeChunk
from ark.core.task import task

logging.basicConfig(
    level=logging.INFO, format="[%(asctime)s][%(levelname)s] %(message)s"
)
LOGGER = logging.getLogger(__name__)


def norm_l2(vec: List[float]) -> List[float]:
    norm = float(np.linalg.norm(vec))
    return [v / norm for v in vec]


@task()
async def inplace_batch_update_chunk_embeddings(
    chunks: List[KnowledgeChunk],
    endpoint_id: str,
    bs: int = 20,
    retry: int = 3,
    norm: str = "none",
    vector_dim: int = 0,
    instruct: str = "",
) -> List[KnowledgeChunk]:
    """
    批量更新知识库 chunk 的 embedding
    """

    async def batch_update(chunk_batch: List[KnowledgeChunk]) -> List[KnowledgeChunk]:
        text_batch = [instruct + str(chunk.vector[1]) for chunk in chunk_batch]
        for r in range(retry):
            try:
                embeddings = await BaseEmbeddingLanguageModel(
                    endpoint_id=endpoint_id, input=text_batch
                ).abatch()
                assert len(embeddings) == len(chunk_batch), "get embeeding failed"
                for chunk, embedding in zip(chunk_batch, embeddings):
                    sliced_emb = embedding
                    if vector_dim > 0 and len(embedding) != vector_dim:
                        # need vector slice & norm
                        sliced_emb = embedding[:vector_dim]
                    if norm == "l2":
                        chunk.vector = (chunk.vector[0], norm_l2(sliced_emb))
                    else:
                        chunk.vector = (chunk.vector[0], sliced_emb)
                return chunk_batch
            except ArkAPIError as e:
                LOGGER.error("embeddings failed, retry: %s, err: %s", r, e)
        raise Exception("retry embeddings failed after retry")
        # FIXME: raise proper Exception

    # inplace update chunk.vector[1]
    # only process chunks with string type chunk.vector[1]
    unprocessed_chunks = [chunk for chunk in chunks if isinstance(chunk.vector[1], str)]
    LOGGER.info(
        "total %d chunks, %d chunks need embedding",
        len(chunks),
        len(unprocessed_chunks),
    )
    tasks = [
        batch_update(unprocessed_chunks[i : i + bs])
        for i in range(0, len(unprocessed_chunks), bs)
    ]
    await asyncio.gather(*tasks)
    return chunks
