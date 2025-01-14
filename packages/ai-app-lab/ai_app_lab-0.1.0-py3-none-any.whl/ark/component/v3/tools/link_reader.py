from typing import Any, Dict, Tuple, Type, Union

from pydantic import Field

from ark.core.action import Action
from ark.core.idl.ark_protocol import (
    ArkLinkReaderRequest,
    ArkLinkReaderResponse,
    FunctionDefinition,
)
from ark.core.idl.common_protocol import ActionDetails
from ark.core.task.task import task
from ark.core.utils.errorsv3 import InvalidParameter


def get_link_reader_schema() -> FunctionDefinition:
    return FunctionDefinition(
        name="LinkReader",
        description="当你需要获取网页、pdf、抖音视频内容时，使用此工具。可以获取url链接下的标题和内容。"
        '\n\nexamples: [{"url_list": ["abc.com", "xyz.com"]}]',
        parameters={
            "type": "object",
            "properties": {
                "url_list": {"type": "array", "items": {"type": "string"}},
                "description": "需要解析网页链接,最多3个,以列表返回",
            },
            "required": ["url_list"],
        },
    )


class LinkReader(Action[ArkLinkReaderRequest, ArkLinkReaderResponse]):
    name: str = "LinkReader"
    function_definition: FunctionDefinition = Field(
        default_factory=get_link_reader_schema
    )
    response_cls: Type[ArkLinkReaderResponse] = ArkLinkReaderResponse

    @task()
    async def arun(
        self, request: ArkLinkReaderRequest, **kwargs: Any
    ) -> Union[ArkLinkReaderResponse, Tuple[ArkLinkReaderResponse, ActionDetails]]:
        return await super().arun(request, **kwargs)

    @task()
    def _fallback_dict_param(self, dict_param: Dict[str, Any]) -> ArkLinkReaderRequest:
        if "url_list" in dict_param:
            return ArkLinkReaderRequest(url_list=dict_param["url_list"])

        if len(dict_param) != 1:
            raise InvalidParameter(parameter="url_list")

        item = list(dict_param.values())[0]
        if isinstance(item, list):
            return ArkLinkReaderRequest(url_list=item)
        else:
            return ArkLinkReaderRequest(url_list=[str(item)])

    @task()
    async def acall(
        self, request: Dict[str, Any], **kwargs: Any
    ) -> Union[ArkLinkReaderResponse, Tuple[ArkLinkReaderResponse, ActionDetails]]:
        """
        for function call format
        """
        req = self._fallback_dict_param(request)
        return await super().arun(req, **kwargs)
