from typing import Any, Dict, List, Literal, Optional, Union

from pydantic import BaseModel, Field

from ark.core.idl.ark_protocol import (
    ArkMessage,
    ArkSearchSourceType,
    FunctionDefinition,
    SourceType,
    UserInfoExtra,
)
from ark.core.idl.maas_protocol import MaasChatMessage
from ark.core.task.task import task


class AtomActionConfig(BaseModel):
    action_name: str
    function_definition: FunctionDefinition


class ActionConfig(BaseModel):
    action_name: str = Field(default="")

    @classmethod
    def convert_messages_to_strs(
        cls, messages: Optional[List[Union[ArkMessage, MaasChatMessage, str]]]
    ) -> Optional[List[str]]:
        if not messages:
            return None
        content = []
        for message in messages:
            if isinstance(message, str):
                content.append(message)
            elif isinstance(message.content, str):
                content.append(message.content)

        return content

    def merge_dict(self, other: Dict[str, Any]) -> Dict[str, Any]:
        merged_dict = self.dict()

        for key in merged_dict.keys():
            value = other.get(key, None)
            if value is not None:
                merged_dict[key] = value

        return merged_dict


class SearchIntentionConfig(ActionConfig):
    keywords: Optional[List[str]] = None
    result_mapping: Optional[Dict[str, bool]] = None


class MultiIntentionConfig(SearchIntentionConfig):
    source_type: Optional[List[SourceType]] = None


class SearchSummaryConfig(ActionConfig):
    summary_top_k: Optional[int] = None
    keywords: Optional[List[str]] = None
    user_info: Optional[UserInfoExtra] = None
    biz_id: Literal["seed", "volc"] = "seed"
    extra_params: Optional[Dict[str, Any]] = None
    ab_params: Optional[Dict[str, Any]] = None
    summary_max_total_len: Optional[int] = None
    browsing_doc_list: str = ""
    summary_with_system_prompt: bool = False
    site: str = ""
    allow_host: Optional[List[str]] = None
    block_host: Optional[List[str]] = None
    publish_time: Dict[str, str] = Field(default_factory=dict)


@task()
def get_extended_source_types(search_config: MultiIntentionConfig) -> List[SourceType]:
    source_type_list: List[SourceType] = []
    if not search_config.source_type:
        return source_type_list

    for source_type in search_config.source_type:
        if source_type == ArkSearchSourceType.DEFAULT_SEARCH:
            continue
        source_type_list.append(source_type)
    return source_type_list
