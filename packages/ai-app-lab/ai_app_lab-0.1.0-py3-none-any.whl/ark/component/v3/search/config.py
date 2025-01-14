from typing import Dict, List, Optional

from pydantic import Field

from ark.core.config import ActionConfig
from ark.core.idl.ark_protocol import SourceType


class SearchConfig(ActionConfig):
    # browsing
    result_mapping: Optional[Dict[str, bool]] = None
    keywords: Optional[List[str]] = None
    source_type: Optional[List[SourceType]] = None
    utm_source: Optional[str] = Field(default="")
    summary_top_k: int = 10
