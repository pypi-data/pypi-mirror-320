from typing import List, Optional, Dict, Any
from wildcard_core.auth.auth_helper import AuthRequiredError
from wildcard_core.auth.auth_status import OAuthStatus
from wildcard_core.auth.oauth_helper import OAuthCredentialsRequiredException, OAuthCredentialsRequiredInfo
from wildcard_core.models import APIService
from wildcard_core.models.IdRegistry import IdRegistry
from wildcard_core.client import WildcardBaseClient
from wildcard_core.logging.types import NoOpLogger, WildcardLogger
from wildcard_openai.Prompt import Prompt
from .Executor import Executor
from .Retriever import Retriever
from openai.types.chat import ChatCompletion
from wildcard_core.models.Action import Action
from typing import Dict
from wildcard_core.tool_registry.tools.rest_api.types import APISchema
from pydantic import PrivateAttr
import os
from enum import Enum
import asyncio

__all__ = ["Action", "WildcardClient"]

class ToolFormat(str, Enum):
    OPENAI = "openai"
    WILDCARD = "wildcard"

class WildcardClient(WildcardBaseClient):
    _function_tools: Dict[str, dict] = PrivateAttr() # OpenAI function calling tools
    _context_tools: Dict[str, dict] = PrivateAttr() # LLM context tools
    _tool_schemas: Dict[str, APISchema] = PrivateAttr() # Tool API schemas
    _executor: Executor = PrivateAttr()
    _retriever: Retriever = PrivateAttr()
    _logger: WildcardLogger = PrivateAttr()
    
    def __init__(self, api_key: str, index_name: str, webhook_url: Optional[str] = None, logger: Optional[WildcardLogger] = NoOpLogger()):
        if api_key is None:
            api_key = os.getenv("WILDCARD_API_KEY")
        super().__init__(
            api_key=api_key,
            index_name=index_name,
            webhook_url=webhook_url,
            logger=logger
        )
        self._function_tools = {}
        self._context_tools = {}
        self._tool_schemas = {}
        self._executor = Executor(wildcard_client=self)
        self._retriever = Retriever(wildcard_client=self)
        self._logger = logger

    async def add_tool_by_id(self, tool_id: str) -> List[dict]:
        """
        Add a tool by its ID
        """
        tool = IdRegistry.get_tool(tool_id)
        return await self.add_tool(tool)
        
    async def add_tools_by_api(self, api_service: APIService) -> List[dict]:
        """
        Add all tools for a given API service. 
        Pre-load tools for a given API service for faster tool calling.
        """
        actions = Action.from_api_service(api_service)
        await asyncio.gather(*[self.add_tool(action) for action in actions])
    
    async def add_tool(self, tool: Action) -> List[dict]:
        """
        Add a tool and create both inside and outside context versions
        """
        tool_schema = await self._retriever.get_tool_details(tool)
        self._function_tools[tool] = await self._retriever.get_outside_context_tool(tool, tool_schema)
        self._context_tools[tool] = await self._retriever.get_inside_context_tool(tool, tool_schema)
        self._tool_schemas[tool] = tool_schema
        return list(self._function_tools.values())

    def get_tool(self, tool_name: Action, format: ToolFormat = ToolFormat.OPENAI) -> dict:
        """
        Get a tool in the specified format
        Args:
            tool_name: The name of the tool e.g. gmail_send_email
            format: Either ToolFormat.OPENAI (for OpenAI function calling) or ToolFormat.WILDCARD (for LLM context)
        """
        if format == ToolFormat.OPENAI:
            return self._function_tools[tool_name]
        elif format == ToolFormat.WILDCARD:
            return self._context_tools[tool_name]
        else:
            raise ValueError(f"Invalid format: {format}")
    
    def get_tools(self, format: ToolFormat = ToolFormat.OPENAI) -> List[dict]:
        """
        Get tools in the specified format
        Args:
            format: Either ToolFormat.OPENAI (for OpenAI function calling) or ToolFormat.WILDCARD (for LLM context)
        """
        if format == ToolFormat.OPENAI:
            self._logger.log("openai_tool_def", self._function_tools)
            return list(self._function_tools.values())
        elif format == ToolFormat.WILDCARD:
            self._logger.log("wildcard_tool_def", self._context_tools)
            return list(self._context_tools.values())
        else:
            raise ValueError(f"Invalid format: {format}")

    async def run_tools(self, response: ChatCompletion, fixed_args: Optional[Dict[str, Any]] = None):
        """
        Run the tools in the response.
        """
        try:
            tools_args = []
            response_tools = getattr(response.choices[0].message, 'tool_calls', []) if response and response.choices else []
            for tool_call in response_tools:
                name = tool_call.function.name
                tool_call = (
                    name,
                    tool_call.function.arguments,
                    self._tool_schemas[name]
                )
                tools_args.append(tool_call)
            if tools_args:
                return await self._executor.run_tools(tools_args, fixed_args)
            else:
                raise ValueError("No tools found in the response")
        except OAuthCredentialsRequiredException as e:
            if e.info.refresh_only:
                # print("OAuth credentials required, refreshing...")
                await self.refresh_token(e.info.api_service, self.webhook_url)
                
                # Retry the tool call
                return await self.run_tools(response, fixed_args)
            else:
                # Fatal error, raise the exception
                # print("Fatal error, OAuth credentials required and are missing")
                raise e
        except ValueError as e:
            # print(e)
            raise e
        
    def get_tool_prompt(self, tool_name: Action) -> str:
        """
        Get the system prompt for a tool
        """
        return Prompt.fixed_tool_prompt([self.get_tool(tool_name, format=ToolFormat.OPENAI)])

    def remove(self, tool: str):
        """
        Remove a tool from the set.
        """
        self._function_tools.pop(tool)
        self._context_tools.pop(tool)
        self._tool_schemas.pop(tool)

    def remove(self, tools: List[str]):
        """
        Remove multiple tools from the set.
        """
        for tool in tools:
            self._function_tools.pop(tool)
            self._context_tools.pop(tool)
            self._tool_schemas.pop(tool)
