from typing import Any, List

from langchain_core.output_parsers import BaseTransformOutputParser
from pydantic.v1 import Field
from typing_extensions import Literal

from ark.component.output_parser.rag_output import RagIntentMessageChunkOutputParser
from ark.component.prompts.rag_prompt import (
    ABSTRACT_INTENTION_TEMPLATE,
    KNOWLEDGE_INTENTION_TEMPLATE,
    IntentionPromptTemplate,
)
from ark.component.v3.llm.base import BaseChatLanguageModel, BaseChatPromptTemplate
from ark.core.task import task


def _knowledge_intention_prompt() -> IntentionPromptTemplate:
    return IntentionPromptTemplate(template=KNOWLEDGE_INTENTION_TEMPLATE)


def _abstract_intention_prompt() -> IntentionPromptTemplate:
    return IntentionPromptTemplate(template=ABSTRACT_INTENTION_TEMPLATE)


def _default_intention_parser() -> RagIntentMessageChunkOutputParser:
    return RagIntentMessageChunkOutputParser()


class RagIntention(BaseChatLanguageModel):
    name: Literal[
        "RagIntention", "KnowledgeIntention", "AbstractIntention"
    ] = "RagIntention"
    template: BaseChatPromptTemplate
    output_parser: BaseTransformOutputParser[List[bool]] = Field(
        default_factory=_default_intention_parser
    )

    def _get_prompt_template(self) -> BaseChatPromptTemplate:
        return self.template

    def _get_output_parser(self) -> BaseTransformOutputParser:
        return self.output_parser

    @task()
    async def arun(self, *args: Any, **kwargs: Any) -> bool:
        resp = await super().arun(*args, **kwargs)
        return await self.aparse_output(resp.choices[0].message.content)


class KnowledgeIntention(RagIntention):
    name: Literal["KnowledgeIntention"] = "KnowledgeIntention"
    template: BaseChatPromptTemplate = Field(
        default_factory=_knowledge_intention_prompt
    )


class AbstractIntention(RagIntention):
    name: Literal["AbstractIntention"] = "AbstractIntention"
    template: BaseChatPromptTemplate = Field(default_factory=_abstract_intention_prompt)
