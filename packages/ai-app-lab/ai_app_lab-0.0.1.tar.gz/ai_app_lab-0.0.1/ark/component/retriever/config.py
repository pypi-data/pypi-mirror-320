from typing import Any, Dict, Optional

from ark.core.config import ActionConfig


class RagConfig(ActionConfig):
    # rag
    collection_name: str
    project: str = "default"
    retrieve_count: int = 5
    rerank_retrieve_count: Optional[int] = None
    rerank_switch: bool = False
    dense_weight: Optional[float] = 0.5
    show_reference: bool = True
    query_param: Optional[Dict[str, Any]] = None
