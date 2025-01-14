import json
import logging
from typing import Any, Dict, List, Tuple

from ark.core.client import ArkClient, get_client_pool
from ark.core.idl.common_protocol import Action, Function, Server
from ark.core.idl.maas_protocol import Tool
from ark.core.utils.errors import InvalidParameter

ToolTypeFunction = "function"


def get_example_values(examples: Dict[str, Any]) -> Dict[str, Any]:
    values_list = list(examples.values())
    json_examples = {}
    for value_dict in values_list:
        if "value" in value_dict:
            json_examples.update(value_dict["value"])
    return json_examples


def merge_parameters(
    params_schema: Dict[str, Any],
    examples: Dict[str, Any],
    parameters_list: List[Dict[str, Any]],
) -> None:
    for parameter_info in parameters_list:
        name = parameter_info.get("name", "")
        schema_info = parameter_info.get("schema", {})
        property_schema = {
            "type": schema_info.get("type", ""),
            "description": parameter_info.get("description", ""),
        }
        params_schema.get("properties", {})[name] = property_schema

        if parameter_info.get("required", False):
            required_list = params_schema.get("required", [])
            if name not in required_list:
                required_list.append(name)
            params_schema["required"] = required_list

        if "example" in schema_info:
            examples[name] = get_example_values(schema_info.get("example", {}))


def resolve_ref(ref: str, components: Dict[str, Any]) -> Dict[str, Any]:
    if not ref.startswith("#/components/schemas/"):
        logging.error(f"Unsupported reference: {ref}")
        raise InvalidParameter(f"Unsupported reference: {ref}")

    schema_name = ref[len("#/components/schemas/") :]
    if schema_name in components:
        return components[schema_name]
    else:
        logging.error(f"Schema not found in components: {schema_name}")
        raise InvalidParameter(f"Schema not found in components: {schema_name}")


def resolve_refs_in_request_body(
    request_body: Dict[str, Any], components: Dict[str, Any]
) -> Tuple[Dict[str, Any], Dict[str, Any]]:
    content = request_body.get("content", {})
    for media_type, media_info in content.items():
        schema_ref = media_info.get("schema", {}).get("$ref", None)
        if not schema_ref:
            continue

        resolved_schema = resolve_ref(schema_ref, components)
        if not resolved_schema:
            continue

        properties = resolved_schema.get("properties", {})
        for name, property in properties.items():
            if isinstance(property, dict):
                properties[name].pop("required", None)

            media_info["schema"] = resolved_schema

    json_content = content.get("application/json")
    return json_content.get("schema", {}), get_example_values(
        json_content.get("examples", {})
    )


def convert_actions(
    actions: List[Dict[str, Any]],
) -> Dict[str, Action]:
    actions_map: Dict[str, Action] = {}
    for raw_action in actions:
        servers = raw_action.get("servers", [])
        paths = raw_action.get("paths", [])

        try:
            assert len(servers) > 0, "servers are required"
            assert len(paths) > 0, "paths are required"
        except AssertionError as e:
            raise InvalidParameter(f"Invalid browsing_options: {e}")

        components = raw_action.get("components", {}).get("schemas", {})
        for path, methods in paths.items():
            for method, details in methods.items():
                request_body = details.get("requestBody", {})
                ref_parameters, ref_examples = resolve_refs_in_request_body(
                    request_body, components
                )
                merge_parameters(
                    ref_parameters, ref_examples, details.get("parameters", [])
                )
                function = Function(
                    name=details.get("operationId", ""),
                    description=details.get("summary", ""),
                    parameters=ref_parameters,
                    examples=[json.dumps(ref_examples)],
                )

                for server_info in servers:
                    action = Action(
                        server=Server(
                            url=server_info.get("url", None),
                            description=server_info.get("description", None),
                        ),
                        http_method=method,
                        path=path,
                        tool=Tool(
                            type=ToolTypeFunction,
                            function=function,
                        ),
                    )
                    actions_map[function.name] = action

    return actions_map


def get_ark_client() -> ArkClient:
    client_pool = get_client_pool()
    client: ArkClient = client_pool.get_client("chat")  # type: ignore
    if not client:
        client = ArkClient()
    return client
