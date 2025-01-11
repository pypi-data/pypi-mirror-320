import copy
from enum import Enum
from typing import Any, Dict, List, Optional, Union

from pydantic import BaseModel, Field

from ark.core.idl.ark_protocol import (
    ArkChatParameters,
    ArkMessage,
)
from ark.core.idl.common_protocol import ModelDesc

RAG_SOURCE = ["rag"]
RAG_TAG = {"rag": "知识库"}

RAG_DESC = {"rag": ""}

SOURCE_PRIPORITY = [
    "weather",
    "douyin_baike",
    "toutiao_article",
    "douyin_short_video",
    "search_engine",
    "xigua_feed_video",
    "toutiao_short_content",
]


class Prompt(BaseModel):
    template: str = ""


class PhaseMode(str, Enum):
    SKIP = "Skip"
    CUSTOM = "Custom"
    STRICT = "Strict"
    PARTIAL = "Partial"


class EndpointConfig(BaseModel):
    model_desc: ModelDesc = Field(default_factory=ModelDesc)
    parameters: Optional[ArkChatParameters] = Field(default_factory=ArkChatParameters)
    """
    pre-defined parameters
    """
    system_prompts: Optional[List[str]] = None
    """
    pre-defined sp
    """
    mode: PhaseMode = PhaseMode.CUSTOM
    """
    model calling mode
    """
    prompt: Optional[Prompt] = None
    """
    prompt template for model
    """
    custom_variables: Dict[str, Any] = Field(default_factory=dict)
    """
    custom_variables for prompt template variables, 
    keys & values stand for variable name & value
    """
    max_history_length: int = 1500
    max_reference_token: int = 3300
    min_reference_token: int = 200
    max_keywords_length: int = 3

    additional_configs: Dict[str, "EndpointConfig"] = Field(default_factory=dict)

    def get_model_ep(self) -> str:
        return self.model_desc.endpoint_id or ""

    def merge_messages(self, messages: List[ArkMessage]) -> Optional[List[ArkMessage]]:
        if not self.system_prompts:
            return messages
        else:
            prompts = [
                ArkMessage(role="system", content=system_prompt)
                for system_prompt in self.system_prompts
            ]
            prompts.extend(messages)
            return prompts

    def merge_parameters(
        self, parameters: Optional[Union[ArkChatParameters, Dict[str, Any]]]
    ) -> Optional[Union[ArkChatParameters, Dict[str, Any]]]:
        if not parameters:
            return self.parameters
        elif not self.parameters:
            return parameters
        else:
            return self.parameters.merge_from(parameters)

    # merge endpoint config
    def merge_from(self, other: Optional["EndpointConfig"] = None) -> "EndpointConfig":
        other_dict = other.__dict__ if other else {}
        merged_dict = copy.deepcopy(self.__dict__)

        for key in merged_dict.keys():
            value = other_dict.get(key, None)
            if value is not None:
                if isinstance(value, ModelDesc):
                    merged_dict[key] = ModelDesc(
                        name=value.name or merged_dict[key].name,
                        version=value.version or merged_dict[key].version,
                        endpoint_id=value.endpoint_id or merged_dict[key].endpoint_id,
                        authorization_token=value.authorization_token
                        or merged_dict[key].authorization_token,
                    )
                elif value:
                    merged_dict[key] = value

        return self.__class__(**merged_dict)


def default_endpoint_config(endpoint_id: str) -> EndpointConfig:
    return EndpointConfig(model_desc=ModelDesc(endpoint_id=endpoint_id))
