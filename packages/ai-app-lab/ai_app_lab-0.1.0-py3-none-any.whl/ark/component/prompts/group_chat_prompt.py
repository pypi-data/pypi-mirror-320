from typing import Any, List

from pydantic import Field
from ark.component.v3.llm.base import BaseChatPromptTemplate
from ark.core.idl.ark_protocol import ArkGroupChatConfig
from langchain_core.messages import (BaseMessage, AIMessage, HumanMessage, SystemMessage)


class GroupChatPromptTemplate(BaseChatPromptTemplate):
    group_chat_config: ArkGroupChatConfig = Field(default_factory=ArkGroupChatConfig)
    """ History QA Messages """
    input_variables: List[str] = ["messages", "target_character_name", ""]

    def format_messages(self, **kwargs: Any) -> List[BaseMessage]:
        """Format original messages into a list of messages.

        Args:
            messages: list of original messages.
            target_character_name: chat target character name.

        Returns:
            Formatted message
        """
        if "messages" not in kwargs:
            raise ValueError("messages")
        if "target_character_name" not in kwargs:
            raise ValueError("target_character_name")

        messages = kwargs.pop("messages")
        input_messages: List[BaseMessage] = [
            msg.copy(deep=True) for msg in messages if msg.type in {"human", "ai"}
        ]

        # cast message with character name
        target_character_name = kwargs.pop("target_character_name")

        formatted_messages: List[BaseMessage] = []
        for msg in input_messages:
            if isinstance(msg, HumanMessage):
                formatted_messages.append(
                    HumanMessage(content=f"{self.group_chat_config.user_name or '用户'}：{msg.content}"))
            elif isinstance(msg, AIMessage):
                if msg.name == target_character_name:
                    """ character self """
                    formatted_messages.append(AIMessage(content=msg.content))
                else:
                    """ other character would be translated into human message"""
                    formatted_messages.append(HumanMessage(content=f"{msg.name}：{msg.content}"))

        target_character_config = None
        for character in self.group_chat_config.characters:
            if character.name == target_character_name:
                target_character_config = character
                break

        if not target_character_config:
            raise ValueError(f"target_character_name: {target_character_name} not found in group_chat_config")

        character_names = [c.name for c in self.group_chat_config.characters if c.name != target_character_name]
        if self.group_chat_config.user_name:
            character_names.append(self.group_chat_config.user_name)

        # inject system prompt
        sp = f"""你是{target_character_name}，{target_character_config.system_prompt}
        >>>>>>>>>>
        你现在正处于一个群聊环境，"""
        if self.group_chat_config.description:
            sp += f"群聊的背景信息如下：\n{self.group_chat_config.description}\n"
        sp += f"""以下是参与群聊的人员：
        【{character_names}】"""

        formatted_messages.insert(0, SystemMessage(content=sp))

        if isinstance(formatted_messages[-1], AIMessage):
            formatted_messages.append(AIMessage(content=""))

        return formatted_messages
