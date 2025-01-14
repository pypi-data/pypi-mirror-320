from wildcard_core.auth.auth_helper import AuthRequiredError
from wildcard_core.auth.auth_status import OAuthStatus
from wildcard_core.auth.oauth_helper import OAuthCredentialsRequiredInfo, OAuthCredentialsRequiredException
from wildcard_core.events.types import ResumeToolExecutionInfo
from wildcard_core.models import Action
from wildcard_core.client import WildcardBaseClient
from wildcard_core.tool_registry.tools.rest_api.RestAPIHandler import RestAPIHandler
from openai.types.chat import ChatCompletionMessageToolCall
from wildcard_core.tool_registry.RegistryDirectory import RegistryDirectory
from typing import List, Optional, Dict, Any
from wildcard_core.tool_registry.tools.rest_api.types import APISchema
from wildcard_core.auth.auth_helper import AuthHelper
import json
from pydantic import BaseModel

class Executor(BaseModel):
    wildcard_client: WildcardBaseClient
    
    def __init__(self, wildcard_client: WildcardBaseClient):
        super().__init__(wildcard_client=wildcard_client)

    async def run_tools(self, tool_calls: List[tuple[str, str, APISchema]], fixed_args: Optional[Dict[str, Any]] = None):
        """
        Run the tools in the response.
        Given a list of tuples (tool_name, tool_args, tool_details)
        """
        
        for tool_call in tool_calls:
            tool_name = tool_call[0]
            tool_args = tool_call[1]
            tool_schema = tool_call[2]
            
            self.wildcard_client = WildcardBaseClient.patch_from_dict(self.wildcard_client)
            
            # print(f"Tool name: {tool_name}")
            # print(f"Tool args: {tool_args}")
            parsed_tool_args: Dict[str, Any] = json.loads(tool_args)
            self.wildcard_client.logger.log("tool_args", parsed_tool_args)
            if fixed_args is not None:
                for key, value in fixed_args.items():
                    # Convert lists to comma-separated strings
                    if isinstance(value, list):
                        parsed_tool_args[key] = ','.join(value)
                    else:
                        parsed_tool_args[key] = value
        
                
            tool_name = Action.from_string(tool_name)
            return await self.wildcard_client.run_tool_with_args(tool_name, schema=tool_schema, **parsed_tool_args)
