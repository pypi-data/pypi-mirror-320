from typing import Any, Dict, List, Optional, Union

from pydantic import Field, field_validator

from ark.component.plugins.plugin import Plugin, convert_messages_to_keywords
from ark.core._api.deprecation import deprecated
from ark.core.client import ArkClient
from ark.core.idl.common_protocol import Parameters, Tool
from ark.core.idl.maas_protocol import (
    MaasChatMessage,
)


@deprecated(
    since="0.1.11",
    removal="0.2.0",
    alternative_import="ark.component.v3.search.SearchSummary",
)
class SearchSummary(Plugin):
    _tools: Optional[List[Tool]] = None

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
            name="SearchSummary",
            endpoint_id=endpoint_id,
            messages=messages,
            options=options,
            parameters=parameters,
            **kwargs,
        )
        if client:
            self.client = client

        if options:
            keywords = options.get("keywords", [])

            if len(keywords) == 0:
                options["keywords"] = [convert_messages_to_keywords(messages)[-1]]

        self._tools = [Tool(type=self.name, options=options)]

    @field_validator("options")
    @classmethod
    def validate_options(cls, v: Optional[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
        if not v or "keywords" not in v:
            return v

        keywords = v.get("keywords", [])

        assert isinstance(keywords, list) and all(
            isinstance(item, str) for item in keywords
        ), "keywords should be list of str"

        return v
