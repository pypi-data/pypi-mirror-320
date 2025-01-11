from typing import Any, Dict, List, Optional, Union

from pydantic import Field, PrivateAttr, field_validator

from ark.component.plugins.plugin import Plugin, convert_messages_to_keywords
from ark.core._api.deprecation import deprecated
from ark.core.client import ArkClient
from ark.core.idl.common_protocol import Parameters, Tool
from ark.core.idl.maas_protocol import (
    MaasChatChoice,
    MaasChatMessage,
)
from ark.core.utils.errors import InvalidParameter, MissingParameter


def _default_result_mappings() -> Dict[str, bool]:
    return {"需要": True, "不需要": False}


@deprecated(
    since="0.1.11",
    removal="0.2.0",
    alternative_import="ark.component.v3.search.SearchIntention",
)
class SearchIntention(Plugin):
    _tools: Optional[List[Tool]] = None
    _result_mappings: Optional[Dict[str, bool]] = PrivateAttr(
        default_factory=_default_result_mappings
    )

    class Config:
        """Configuration for this pydantic object."""

        arbitrary_types_allowed = True

    def __init__(
        self,
        endpoint_id: str,
        messages: List[MaasChatMessage] = Field(default_factory=list),
        options: Optional[Dict[str, Any]] = None,
        parameters: Optional[Union[Parameters, Dict[str, Any]]] = None,
        client: Optional[ArkClient] = None,
        **kwargs: Any,
    ):
        super().__init__(
            name="SearchIntention",
            endpoint_id=endpoint_id,
            messages=messages,
            options=options,
            parameters=parameters,
            **kwargs,
        )
        if client:
            self.client = client

        if options:
            if "result_mapping" in options and isinstance(
                options["result_mapping"], dict
            ):
                self._result_mappings = (
                    options["result_mapping"] or _default_result_mappings()
                )

            keywords = options.get("keywords", [])

            if len(keywords) > 0 and all(
                isinstance(item, MaasChatMessage) for item in keywords
            ):
                options["keywords"] = convert_messages_to_keywords(keywords)

        self._tools = [Tool(type=self.name, options=options)]

    async def aparse_output(self, output: Union[str, List[MaasChatChoice]]) -> bool:
        _result_mappings = self._result_mappings or _default_result_mappings()
        text = output if isinstance(output, str) else ""
        if isinstance(output, list):
            if len(output) == 0:
                return False
            text = (
                output[0].message.content
                if isinstance(output[0].message.content, str)
                else ""
            )

        # default false
        return _result_mappings.get(text, False)

    @field_validator("options")
    @classmethod
    def validate_options(cls, v: Optional[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
        if not v or "keywords" not in v:
            return v

        keywords = v.get("keywords", [])

        if keywords and not isinstance(keywords, list):
            raise InvalidParameter("keywords should be list")

        # no keywords, simply return, result would be parsed by
        if len(keywords) == 0:
            return v

        if any(
            not isinstance(item, str) and not isinstance(item, MaasChatMessage)
            for item in keywords
        ):
            raise InvalidParameter(
                "keywords should be list of either str or MaasChatMessage"
            )

        if "result_mapping" not in v or not isinstance(v["result_mapping"], dict):
            raise MissingParameter(
                "options should contain result_mapping when keywords exist"
            )

        return v
