from typing import Any, List, Tuple, Union

from langchain.schema.output_parser import BaseTransformOutputParser
from pydantic.v1 import Field
from typing_extensions import Literal
from volcenginesdkarkruntime.types.completion_usage import CompletionUsage

from ark.component.output_parser.browsing_output import (
    BrowsingGenerationMessageChunkOutputParser,
)
from ark.component.prompts import BrowsingGenerationChatPromptTemplate
from ark.component.v3.llm.base import BaseChatLanguageModel, BaseChatPromptTemplate
from ark.core.task.task import task


class BrowsingQueryRewrite(BaseChatLanguageModel):
    name: Literal["BrowsingQueryRewrite"] = "BrowsingQueryRewrite"
    template: BaseChatPromptTemplate = Field(
        default_factory=BrowsingGenerationChatPromptTemplate
    )
    output_parser: BaseTransformOutputParser[List[str]] = Field(
        default_factory=BrowsingGenerationMessageChunkOutputParser
    )

    class Config:
        """Configuration for this pydantic object."""

        arbitrary_types_allowed = True

    @task()
    async def arun(
        self, include_usage: bool = False, *args: Any, **kwargs: Any
    ) -> Union[Tuple[List[str], CompletionUsage], List[str]]:
        resp = await super().arun(*args, **kwargs)
        parsed_content = await self.aparse_output(resp.choices[0].message.content)
        if include_usage:
            return parsed_content, resp.usage
        else:
            return parsed_content
