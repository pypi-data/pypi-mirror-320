from typing import Any, AsyncIterable, Dict, List, Tuple, Type, Union

from pydantic import Field, field_validator

from ark.component.v3.search.config import SearchConfig
from ark.core.action import Action
from ark.core.idl.ark_protocol import (
    ArkChatCompletionChunk,
    ArkChatRequest,
    ArkChatResponse,
    ArkSearchIntentionMetadata,
    ArkSearchRequest,
    ArkSearchResponse,
    ArkSearchSourceType,
    ArkSearchSummaryMetadata,
    SourceType,
)
from ark.core.idl.common_protocol import ActionDetails
from ark.core.task.task import task
from ark.core.utils.errorsv3 import InvalidParameter


class Search(Action[ArkSearchRequest, ArkSearchResponse]):
    name: str = "Search"
    response_cls: Type[ArkSearchResponse] = ArkSearchResponse

    @classmethod
    @field_validator("meta_info")
    def validate_meta_info(cls, v: Dict[str, Any]) -> Dict[str, Any]:
        if v.get("action_name") not in [
            "WebBrowsingPlus",
            "WebBrowsingPro",
            "content_plugin",
        ]:
            raise InvalidParameter("action_name")
        return v

    @task()
    async def arun(
        self, request: ArkSearchRequest, **kwargs: Any
    ) -> Union[ArkSearchResponse, Tuple[ArkSearchResponse, ActionDetails]]:
        if self.meta_info.action_name:
            request.action_name = self.meta_info.action_name  # type: ignore

        return await super().arun(request, **kwargs)


class SearchIntention(Action[ArkChatRequest, ArkChatResponse]):
    name: str = "SearchIntention"
    meta_info: ArkSearchIntentionMetadata = Field(
        default_factory=ArkSearchIntentionMetadata
    )
    response_cls: Type[ArkChatResponse] = ArkChatResponse

    @classmethod
    @field_validator("meta_info")
    def validate_meta_info(cls, v: Dict[str, Any]) -> Dict[str, Any]:
        if v.get("action_name") not in [
            "WebBrowsing",
            "WebBrowsingPlus",
            "WebBrowsingPro",
            "content_plugin",
        ]:
            raise InvalidParameter("action_name")
        return v

    @task()
    async def arun(self, request: ArkChatRequest, **kwargs: Any) -> ArkChatResponse:
        request.metadata = self.meta_info.model_dump(exclude_none=True)
        if not self.meta_info.model:
            self.meta_info.model = request.model
        return await super().arun(request, **kwargs)

    @staticmethod
    def _default_result_mappings() -> Dict[str, bool]:
        return {"需要": True, "不需要": False}

    @task()
    async def aparse_output(self, text: str) -> bool:
        _result_mappings = (
            self.meta_info.result_mapping or self._default_result_mappings()
        )
        # default false
        return _result_mappings.get(text, False)


class SearchSummary(Action[ArkChatRequest, ArkChatResponse]):
    name: str = "SearchSummary"
    meta_info: ArkSearchSummaryMetadata = Field(
        default_factory=ArkSearchIntentionMetadata
    )
    response_cls: Type[ArkChatResponse] = ArkChatResponse

    @classmethod
    @field_validator("meta_info")
    def validate_meta_info(cls, v: Dict[str, Any]) -> Dict[str, Any]:
        if v.get("action_name") not in [
            "WebBrowsing",
            "WebBrowsingPlus",
            "WebBrowsingPro",
            "content_plugin",
        ]:
            raise InvalidParameter("action_name")
        return v

    @task()
    async def arun(self, request: ArkChatRequest, **kwargs: Any) -> ArkChatResponse:
        request.metadata = self.meta_info.model_dump(exclude_none=True)

        if not self.meta_info.model:
            self.meta_info.model = request.model

        return await super().arun(request, **kwargs)

    @task()
    async def astream(
        self, request: ArkChatRequest, **kwargs: Any
    ) -> AsyncIterable[ArkChatCompletionChunk]:
        request.metadata = self.meta_info.model_dump(exclude_none=True)
        self.meta_info.model = request.model

        responses = self.client.astream_request(
            api=self.name,
            meta_info=self.meta_info,
            request=request,
            response_cls=ArkChatCompletionChunk,
            **kwargs,
        )
        async for response in responses:
            yield response


@task()
def get_extended_source_types(search_config: SearchConfig) -> List[SourceType]:
    source_type_list: List[SourceType] = []
    if not search_config.source_type:
        return source_type_list

    for source_type in search_config.source_type:
        if source_type == ArkSearchSourceType.DEFAULT_SEARCH:
            continue
        source_type_list.append(source_type)
    return source_type_list
