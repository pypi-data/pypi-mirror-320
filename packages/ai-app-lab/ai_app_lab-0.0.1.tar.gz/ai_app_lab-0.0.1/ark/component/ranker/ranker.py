from typing import Any, Dict, List

from langchain.load import dumps, loads
from langchain_core.documents import Document

from ark.core.task import task


@task(distributed=False)
def reciprocal_rank_fusion(
    results: List[Dict[str, Any]], k: float = 60
) -> List[Document]:
    fused_scores = {}
    for docs in results:
        # Assumes the docs are returned in sorted order of relevance
        for rank, doc in enumerate(docs):
            doc_str = dumps(doc)
            if doc_str not in fused_scores:
                fused_scores[doc_str] = 0.0
            fused_scores[doc_str] += 1.0 / (rank + k)

    reranked_results = [
        (loads(doc), score)
        for doc, score in sorted(fused_scores.items(), key=lambda x: x[1], reverse=True)
    ]
    context_docs = "\n".join([doc[0].page_content for doc in reranked_results])
    return [Document(page_content=context_docs)]
