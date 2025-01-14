from typing import Any

from pydantic.v1 import Field
from typing_extensions import Literal

from ark.component.llm.base import BaseChatLanguageModel, BaseChatPromptTemplate
from ark.component.prompts.custom_prompt import CustomPromptTemplate
from ark.component.prompts.rag_prompt import DEFAULT_SUMMARY_PROMPT
from ark.core.idl.maas_protocol import MaasChatResponse
from ark.core.task import task


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

    @task()
    async def arun(self, *args: Any, **kwargs: Any) -> MaasChatResponse:
        return await super().arun(*args, **kwargs)

    @task()
    def run(self, *args: Any, **kwargs: Any) -> MaasChatResponse:
        return super().run(*args, **kwargs)
