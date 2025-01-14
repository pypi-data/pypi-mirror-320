from pydantic.v1 import Field
from typing_extensions import Literal

from ark.component.prompts.custom_prompt import CustomPromptTemplate
from ark.component.prompts.rag_prompt import DEFAULT_SUMMARY_PROMPT
from ark.component.v3.llm.base import BaseChatLanguageModel, BaseChatPromptTemplate


def _default_summary_prompt() -> CustomPromptTemplate:
    return CustomPromptTemplate(
        template=DEFAULT_SUMMARY_PROMPT,
        keep_history_systems=True,
        keep_history_questions=True,
    )


class RagSummary(BaseChatLanguageModel):
    name: Literal["RagSummary"] = "RagSummary"
    template: CustomPromptTemplate = Field(default_factory=_default_summary_prompt)

    def _get_prompt_template(self) -> BaseChatPromptTemplate:
        return self.template
