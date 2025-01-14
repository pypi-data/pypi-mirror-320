from typing import List, Optional, Dict, Any
from wildcard_core.auth.auth_helper import AuthRequiredError
from wildcard_core.auth.auth_status import OAuthStatus
from wildcard_core.auth.oauth_helper import OAuthCredentialsRequiredException, OAuthCredentialsRequiredInfo
from wildcard_core.models.IdRegistry import IdRegistry
from wildcard_core.tool_search import ToolSearchClient
from wildcard_core.logging.types import NoOpLogger, WildcardLogger
from .Executor import Executor
from .Retriever import Retriever
from openai.types.chat import ChatCompletion
from wildcard_core.models.Action import Action
from typing import Dict
from wildcard_core.tool_registry.tools.rest_api.types import APISchema
from pydantic import PrivateAttr
import os

__all__ = ["Action", "ToolClient"]

class ToolClient(ToolSearchClient):
    _outside_context_tools: Dict[str, dict] = PrivateAttr()
    _inside_context_tools: Dict[str, dict] = PrivateAttr()
    _tool_schemas: Dict[str, APISchema] = PrivateAttr()
    _executor: Executor = PrivateAttr()
    _retriever: Retriever = PrivateAttr()
    _logger: WildcardLogger = PrivateAttr()
    
    def __init__(self, api_key: str, index_name: str, webhook_url: str = None, logger: WildcardLogger = NoOpLogger()):
        if api_key is None:
            api_key = os.getenv("WILDCARD_API_KEY")
        super().__init__(
            api_key=api_key,
            index_name=index_name,
            webhook_url=webhook_url,
            logger=logger
        )
        self._outside_context_tools = {}
        self._inside_context_tools = {}
        self._tool_schemas = {}
        self._executor = Executor(tool_search_client=self)
        self._retriever = Retriever(tool_search_client=self)
        self._logger = logger

    async def add_tool_by_id(self, tool_id: str) -> List[dict]:
        """
        Add a tool by its ID
        """
        tool = IdRegistry.get_tool(tool_id)
        return await self.add(tool)
        
    
    async def add(self, tool: str) -> List[dict]:
        """
        Add a tool and create both inside and outside context versions
        """
        tool_schema = await self._retriever.get_tool_details(tool)
        self._outside_context_tools[tool] = await self._retriever.get_outside_context_tool(tool, tool_schema)
        self._inside_context_tools[tool] = await self._retriever.get_inside_context_tool(tool, tool_schema)
        self._tool_schemas[tool] = tool_schema
        return list(self._outside_context_tools.values())

    def get_tool(self, tool_name: str, format: str = "outside") -> dict:
        """
        Get a tool in the specified format
        Args:
            tool_name: The name of the tool e.g. gmail_send_email
            format: Either "outside" (for OpenAI function calling) or "inside" (for LLM context)
        """
        if format in ["outside", "openai"]:
            return self._outside_context_tools[tool_name]
        elif format in ["inside", "wildcard"]:
            return self._inside_context_tools[tool_name]
        else:
            raise ValueError(f"Invalid format: {format}")
    
    def get_tools(self, format: str = "outside") -> List[dict]:
        """
        Get tools in the specified format
        Args:
            format: Either "outside" (for OpenAI function calling) or "inside" (for LLM context)
        """
        if format in ["outside", "openai"]:
            self._logger.log("outside_tool_def", self._outside_context_tools)
            return list(self._outside_context_tools.values())
        elif format in ["inside", "wildcard"]:
            self._logger.log("inside_tool_def", self._inside_context_tools)
            return list(self._inside_context_tools.values())
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
                print("OAuth credentials required, refreshing...")
                await self.refresh_token(e.info.api_service, self.webhook_url)
                
                # Retry the tool call
                return await self.run_tools(response, fixed_args)
            else:
                # Fatal error, raise the exception
                print("Fatal error, OAuth credentials required and are missing")
                raise e
        except ValueError as e:
            print(e)
            raise e

    def remove(self, tool: str):
        """
        Remove a tool from the set.
        """
        self._outside_context_tools.pop(tool)
        self._inside_context_tools.pop(tool)
        self._tool_schemas.pop(tool)

    def remove(self, tools: List[str]):
        """
        Remove multiple tools from the set.
        """
        for tool in tools:
            self._outside_context_tools.pop(tool)
            self._inside_context_tools.pop(tool)
            self._tool_schemas.pop(tool)
