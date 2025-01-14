from typing import Any, Dict, Literal

from pydantic import Field

from ark.component.prompts.group_chat_prompt import GroupChatPromptTemplate
from ark.component.v3.llm.base import BaseChatLanguageModel, BaseChatPromptTemplate
from ark.core.idl.ark_protocol import ArkCharacterConfig, ArkGroupChatConfig
from ark.core.utils.errorsv3 import InvalidParameter, MissingParameter


class GroupChat(BaseChatLanguageModel):
    name: Literal["GroupChat"] = "GroupChat"
    group_chat_config: ArkGroupChatConfig
    template: BaseChatPromptTemplate = Field(default_factory=GroupChatPromptTemplate)
    character_config_map: Dict[str, ArkCharacterConfig]

    def __init__(self, group_chat_config: ArkGroupChatConfig, **kwargs: Any):
        super().__init__(
            group_chat_config=group_chat_config,  # type: ignore
            character_config_map={c.name: c for c in group_chat_config.characters},  # type: ignore
            template=GroupChatPromptTemplate(group_chat_config=group_chat_config),
            **kwargs,
        )

    def get_request_model(self, **kwargs: Any) -> str:
        if "target_character_name" not in kwargs:
            raise MissingParameter(parameter="target_character_name")

        character_config = self.character_config_map.get(
            kwargs.get("target_character_name", "")
        )

        if not character_config:
            raise InvalidParameter(
                parameter="target_character_name",
                cause="specific character config not found",
            )

        if (
            not character_config.model_desc
            or not character_config.model_desc.endpoint_id
        ):
            return self.endpoint_id

        return character_config.model_desc.endpoint_id
