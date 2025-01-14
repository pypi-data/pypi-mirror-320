from wildcard_core.client import WildcardBaseClient
from wildcard_core.models import Action
from wildcard_core.tool_registry.tools.rest_api.types import APISchema
from .OpenAITool import OpenAITool
from wildcard_core.models.IdRegistry import IdRegistry
from pydantic import BaseModel
from typing import Tuple

class Retriever(BaseModel):
    wildcard_client: WildcardBaseClient
    
    def __init__(self, wildcard_client: WildcardBaseClient):
        super().__init__(wildcard_client=wildcard_client)

    async def get_tool_details_by_id(self, uuid: str) -> APISchema:
        tool_schema = await self.wildcard_client.get_action_schema(uuid)
        self.wildcard_client.logger.log("wildcard_spec", tool_schema.model_dump(mode="json"))
        return tool_schema
    
    async def get_tool_details(self, toolEnum: str) -> APISchema:
        """
        Get the details of a tool from wildcard search given tool enum
        """
        tool_id = IdRegistry.get_id(tool=toolEnum)
        tool_schema = await self.wildcard_client.get_action_schema(tool_id)
        self.wildcard_client.logger.log("wildcard_spec", tool_schema.model_dump(mode="json"))
        return tool_schema

    async def get_outside_context_tool(self, tool_enum: Action, tool_schema: APISchema) -> dict:
        """Return a simplified OpenAI tool object for function calling"""
        openai_tool = OpenAITool.from_api_schema(tool_enum, tool_schema, strict=False, openai_mode=True)
        self.wildcard_client.logger.log("outside_context_tool", openai_tool.model_dump(mode="json"))
        return openai_tool.to_json()

    async def get_inside_context_tool(self, tool_enum: Action, tool_schema: APISchema) -> dict:
        """Return a detailed tool object for LLM interpretation"""
        inside_tool = OpenAITool.from_api_schema(tool_enum, tool_schema, strict=False, openai_mode=False)
        self.wildcard_client.logger.log("inside_context_tool", inside_tool.model_dump(mode="json"))
        return inside_tool.to_json()
