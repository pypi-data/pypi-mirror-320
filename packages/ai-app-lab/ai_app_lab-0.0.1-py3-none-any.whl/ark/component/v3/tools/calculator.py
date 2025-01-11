from typing import Any, Dict, Tuple, Type, Union

from pydantic import Field

from ark.core.action import Action
from ark.core.idl.ark_protocol import (
    ArkCalculatorRequest,
    ArkCalculatorResponse,
    FunctionDefinition,
)
from ark.core.idl.common_protocol import ActionDetails
from ark.core.task.task import task


def _get_calculator_schema() -> FunctionDefinition:
    return FunctionDefinition(
        name="calculator",
        description="Evaluate a given mathematical expression",
        parameters={
            "type": "object",
            "properties": {
                "input": {
                    "type": "string",
                    "description": "The mathematical expression "
                    "in Wolfram Language InputForm",
                },
            },
            "required": ["input"],
        },
    )


class Calculator(Action[ArkCalculatorRequest, ArkCalculatorResponse]):
    name: str = "Calculator"
    function_definition: FunctionDefinition = Field(
        default_factory=_get_calculator_schema
    )
    response_cls: Type[ArkCalculatorResponse] = ArkCalculatorResponse

    @task()
    async def arun(
        self, request: ArkCalculatorRequest, **kwargs: Any
    ) -> Union[ArkCalculatorResponse, Tuple[ArkCalculatorResponse, ActionDetails]]:
        return await super().arun(request, **kwargs)

    @task()
    async def acall(
        self, request: Dict[str, Any], **kwargs: Any
    ) -> Union[ArkCalculatorResponse, Tuple[ArkCalculatorResponse, ActionDetails]]:
        """
        for function call format
        """
        req = ArkCalculatorRequest.model_validate(request)
        return await super().arun(req, **kwargs)
