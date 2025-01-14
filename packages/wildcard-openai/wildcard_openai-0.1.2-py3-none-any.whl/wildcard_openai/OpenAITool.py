from wildcard_core.tool_registry.tools.rest_api.types import APISchema, EndpointSchema, ParameterSchemaType
from wildcard_core.client.utils.helpers import generate_readable_args_schema, generate_readable_request_body_schema
from pydantic import BaseModel
import json
from typing import Optional, Dict, Any
from wildcard_core.models import Action

class OpenAIParameters(BaseModel):
    type: str = "object"
    properties: Dict[str, Any]
    required: Optional[list[str]] = None
    additionalProperties: bool = False

class OpenAIFunction(BaseModel):
    name: str
    description: str
    parameters: Optional[OpenAIParameters] = None
    strict: bool = False

class OpenAITool(BaseModel):
    type: str = "function"
    function: OpenAIFunction

    @classmethod
    def from_api_schema(cls, tool_enum: Action, tool_details: APISchema, strict: bool = False, openai_mode: bool = False):
        if not tool_details.endpoints:
            return None
        
        tools = []
        for endpoint in tool_details.endpoints:
            # Generate parameter schemas
            parameters = {}
            required = []
            
            def _add_to_parameters(parameters_dict, key, value):
                if key in parameters_dict:
                    if isinstance(parameters_dict[key], list):
                        parameters_dict[key].append(value)
                    else:
                        parameters_dict[key] = [parameters_dict[key], value]
                else:
                    parameters_dict[key] = value
            
            # Process path and query parameters
            if endpoint.parameters:
                param_schema = generate_readable_args_schema(endpoint.parameters, openai_mode=openai_mode)
                for param_name, param_details in param_schema.items():
                    # Handle allOf, anyOf, oneOf by replacing with object and setting additionalProperties=True
                    if param_details["allowed_schemas"][0]["type"] in ["allOf", "anyOf", "oneOf"]:
                        value = {
                            "type": "object",
                            "description": param_details["description"] or "", # TODO: this might cause issues. Check later
                            "additionalProperties": True
                        }
                        _add_to_parameters(parameters, param_name, value)
                    else:
                        value = {
                            "type": param_details["allowed_schemas"][0]["type"],
                            "description": param_details["description"] or "", # TODO: this might cause issues. Check later
                            **{k: v for k, v in param_details["allowed_schemas"][0].items() if k not in ["type", "description", "required"]}
                        }
                        if param_details["required"] == "Required":
                            required.append(param_name)
                        _add_to_parameters(parameters, param_name, value)
            
            # Process request body if present
            if endpoint.requestBody:
                body_schema = generate_readable_request_body_schema(endpoint.requestBody, openai_mode=openai_mode)
                for param in body_schema:
                    value = {
                        "type": param["allowed_schemas"][0]["type"],
                        "description": param["description"] or "", # TODO: this might cause issues. Check later
                        **{k: v for k, v in param["allowed_schemas"][0].items() if k not in ["type", "description", "required"]}
                    }
                    if param["required"] == "Required":
                        required.append(param["name"])
                    _add_to_parameters(parameters, param["name"], value)
            
            function = OpenAIFunction(
                name=tool_enum,
                description=endpoint.description or "No description provided",
                strict=strict,
                parameters=OpenAIParameters(
                    properties=parameters,
                    required=required if required else []
                ) if parameters else None
            )
            
            tools.append(cls(function=function))
        return tools[0]

    def __init__(self, function: OpenAIFunction):
        super().__init__(function=function)
    
    def to_json(self):
        return self.model_dump(include={"type", "function"}, mode="json")

    def to_dict(self):
        return self.model_dump(include={"type", "function"}, mode="python")
