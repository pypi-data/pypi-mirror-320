from typing import Any, List

from langchain_core.output_parsers import BaseTransformOutputParser
from pydantic.v1 import Field
from typing_extensions import Literal

from ark.component.llm.base import BaseChatLanguageModel, BaseChatPromptTemplate
from ark.component.output_parser.rag_output import RagRewriteMessageChunkOutputParser
from ark.component.prompts.rag_prompt import (
    CONDENSE_QUESTION_PROMPT_TEMPLATE,
    HYPO_ANSWER_PROMPT_TEMPLATE,
    QueryRewritePromptTemplate,
)
from ark.core._api.deprecation import deprecated
from ark.core.task import task


def _get_query_rewrite_prompt_template() -> BaseChatPromptTemplate:
    return QueryRewritePromptTemplate(template=CONDENSE_QUESTION_PROMPT_TEMPLATE)


def _get_hypo_answer_rewrite_prompt_template() -> BaseChatPromptTemplate:
    return QueryRewritePromptTemplate(template=HYPO_ANSWER_PROMPT_TEMPLATE)


def _get_default_output_parser() -> BaseTransformOutputParser:
    return RagRewriteMessageChunkOutputParser()


@deprecated(
    since="0.1.11",
    removal="0.2.0",
    alternative_import="ark.component.v3.llm.rag_rewrite.RewriteGenerator",
)
class RewriteGenerator(BaseChatLanguageModel):
    name: Literal["Rewrite", "QueryRewrite", "HypoAnswer"] = "Rewrite"
    template: BaseChatPromptTemplate
    output_parser: BaseTransformOutputParser[List[str]] = Field(
        default_factory=_get_default_output_parser
    )

    def _get_prompt_template(self) -> BaseChatPromptTemplate:
        return self.template

    def _get_output_parser(self) -> BaseTransformOutputParser:
        return self.output_parser

    @task()
    async def arun(self, *args: Any, **kwargs: Any) -> bool:
        resp = await super().arun(*args, **kwargs)
        return await self.aparse_output(resp.choices[0].message.content)

    @task()
    def run(self, *args: Any, **kwargs: Any) -> bool:
        resp = super().run(*args, **kwargs)
        return self.parse_output(resp.choices[0].message.content)


class QueryRewriteGenerator(RewriteGenerator):
    name: Literal["QueryRewrite"] = "QueryRewrite"
    template: BaseChatPromptTemplate = Field(
        default_factory=_get_query_rewrite_prompt_template
    )


class HypoAnswerGenerator(RewriteGenerator):
    name: Literal["HypoAnswer"] = "HypoAnswer"
    template: BaseChatPromptTemplate = Field(
        default_factory=_get_hypo_answer_rewrite_prompt_template
    )
