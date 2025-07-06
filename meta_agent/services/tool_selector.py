"""
ToolSelector: Selects and configures appropriate tools for domain agents.
"""

import logging
from typing import List, Dict, Any

from pydantic import BaseModel, Field

from .base import BaseAIService

logger = logging.getLogger(__name__)


class ToolSelectionRequest(BaseModel):
    """Request for tool selection"""
    domain: str = Field(..., description="Domain requiring tools")
    agent_roles: List[str] = Field(..., description="Roles of agents needing tools")
    task_requirements: List[str] = Field(..., description="Task requirements")
    available_tools: List[str] = Field(..., description="Available tools to select from")


class ToolConfiguration(BaseModel):
    """Tool configuration for agents"""
    agent_tools: Dict[str, List[str]] = Field(
        ..., description="Tools assigned to each agent"
    )
    shared_tools: List[str] = Field(
        ..., description="Tools shared by all agents"
    )
    tool_parameters: Dict[str, Dict[str, Any]] = Field(
        default_factory=dict, description="Tool-specific parameters"
    )
    integration_notes: str = Field(
        ..., description="Notes on tool integration"
    )


class ToolSelector(BaseAIService[ToolConfiguration]):
    """
    Selects and configures appropriate tools for domain-specific agents.
    """
    
    def __init__(self, api_key: str):
        """Initialize the tool selector"""
        super().__init__(api_key)
        
    def get_system_prompt(self) -> str:
        """System prompt for tool selection"""
        return """You are an expert in tool selection and configuration for AI agents. 
You understand:

1. Domain-specific tool requirements
2. Agent role and tool compatibility
3. Tool integration and orchestration
4. Resource optimization
5. Tool parameter configuration

When selecting tools, you consider:
- Domain-specific needs and constraints
- Agent capabilities and roles
- Tool compatibility and integration
- Performance and resource requirements
- Redundancy and backup options

Your tool configurations are practical, efficient, and optimized for the domain."""
    
    def get_response_model(self) -> type[BaseModel]:
        """Return the response model"""
        return ToolConfiguration
    
    async def select_tools(
        self,
        request: ToolSelectionRequest
    ) -> ToolConfiguration:
        """Select and configure tools for agents"""
        prompt = f"""Select and configure tools for these agents:

Domain: {request.domain}
Agent Roles: {', '.join(request.agent_roles)}
Task Requirements: {', '.join(request.task_requirements)}
Available Tools: {', '.join(request.available_tools)}

Create a tool configuration that:
1. Assigns appropriate tools to each agent role
2. Identifies tools that should be shared
3. Specifies tool parameters where needed
4. Provides integration guidance

Consider:
- Each agent's specific needs
- Avoiding tool redundancy
- Ensuring complete task coverage
- Integration complexity
- Performance implications"""

        logger.info(f"Selecting tools for {request.domain} domain")
        
        return await self.invoke_agent(prompt)