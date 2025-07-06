"""
AgentFactory: Creates individual agents with specific personalities and capabilities.
"""

import logging
from typing import Dict, Any, List, Optional
from string import Template

from pydantic import BaseModel, Field

from .base import BaseAIService
from ..schemas.domain import (
    AgentSpecification, AgentPersonality, PersonalityTrait, AgentRole
)
from ..utils.prompts import PromptTemplates, PromptBuilder

logger = logging.getLogger(__name__)


class AgentCreationRequest(BaseModel):
    """Request to create a new agent"""
    name: str = Field(..., description="Agent name")
    role: AgentRole = Field(..., description="Agent role")
    domain: str = Field(..., description="Domain of expertise")
    specialization: str = Field(..., description="Specific area of focus")
    personality_keywords: List[str] = Field(
        default_factory=list, description="Keywords describing personality"
    )
    capabilities_needed: List[str] = Field(
        ..., description="Required capabilities"
    )


class AgentFactory(BaseAIService[AgentSpecification]):
    """
    Factory for creating individual agents with specific personalities,
    capabilities, and domain expertise.
    """
    
    def __init__(self, api_key: str):
        """Initialize the agent factory"""
        super().__init__(api_key)
        self.created_agents: Dict[str, AgentSpecification] = {}
        self.personality_templates = self._initialize_personality_templates()
        
    def get_system_prompt(self) -> str:
        """System prompt for agent creation"""
        return """You are an expert agent designer specializing in creating AI agents with 
distinct personalities, capabilities, and domain expertise. Your expertise includes:

1. Personality design that creates engaging, effective agents
2. Capability mapping to ensure agents can fulfill their roles
3. Domain-specific knowledge integration
4. Communication style development
5. Tool and resource allocation

You understand that effective agents need:
- Clear, consistent personalities that enhance their effectiveness
- Domain-appropriate communication styles
- Complementary traits when working in teams
- The right tools and capabilities for their tasks
- Well-crafted system prompts that guide behavior

When creating agents, you consider:
- How personality traits affect decision-making
- The balance between expertise and approachability
- Team dynamics and personality compatibility
- Domain-specific behavioral patterns
- Communication effectiveness

Your agent designs are nuanced, practical, and optimized for their intended roles."""
    
    def get_response_model(self) -> type[BaseModel]:
        """Return the response model for structured outputs"""
        return AgentSpecification
    
    def _initialize_personality_templates(self) -> Dict[str, List[str]]:
        """Initialize personality trait templates"""
        return {
            "analytical": ["methodical", "detail-oriented", "logical", "systematic"],
            "creative": ["innovative", "imaginative", "unconventional", "visionary"],
            "pragmatic": ["practical", "results-focused", "efficient", "realistic"],
            "collaborative": ["cooperative", "inclusive", "diplomatic", "team-oriented"],
            "assertive": ["confident", "decisive", "direct", "authoritative"],
            "cautious": ["careful", "risk-aware", "thorough", "prudent"],
            "optimistic": ["positive", "enthusiastic", "hopeful", "encouraging"],
            "critical": ["skeptical", "questioning", "analytical", "discerning"]
        }
    
    async def create_agent(
        self, 
        request: AgentCreationRequest
    ) -> AgentSpecification:
        """
        Create a new agent based on specifications.
        
        Args:
            request: Agent creation request
            
        Returns:
            Complete agent specification
        """
        # Build personality context
        personality_context = self._build_personality_context(request.personality_keywords)
        
        prompt = f"""Create a specialized agent with these specifications:

Name: {request.name}
Role: {request.role.value}
Domain: {request.domain}
Specialization: {request.specialization}
Personality Keywords: {', '.join(request.personality_keywords)}
Required Capabilities: {', '.join(request.capabilities_needed)}

Design a complete agent that includes:

1. PERSONALITY PROFILE:
   - 3-5 personality traits with descriptions and strengths (0-1)
   - Communication style that fits the personality
   - Decision-making style aligned with role and personality
   - Domain expertise areas

2. SYSTEM PROMPT:
   - Clear role definition
   - Personality integration
   - Domain-specific instructions
   - Behavioral guidelines
   - Task approach methodology

3. TOOLS AND CAPABILITIES:
   - Specific tools needed for the role
   - Capabilities that enable task completion
   - Integration with domain requirements

4. BEHAVIORAL PATTERNS:
   - How the agent approaches problems
   - Interaction style with other agents
   - Response patterns to challenges
   - Quality focus areas

Ensure the agent is:
- Distinct and memorable
- Effective in their role
- Compatible with team dynamics
- Domain-appropriate
- Practically implementable

Personality Context: {personality_context}"""

        logger.info(f"Creating agent: {request.name} ({request.role.value})")
        
        result = await self.invoke_agent(prompt)
        
        # Store the created agent
        self.created_agents[request.name] = result
        
        return result
    
    async def generate_system_prompt(
        self,
        agent_spec: AgentSpecification
    ) -> str:
        """
        Generate a complete system prompt for an agent.
        
        Args:
            agent_spec: Agent specification
            
        Returns:
            Complete system prompt
        """
        # Select appropriate template based on role
        template = self._select_prompt_template(agent_spec.role)
        
        # Build prompt components
        personality_traits = PromptBuilder.build_personality_description([
            {"name": trait.name, "description": trait.description, "strength": trait.strength}
            for trait in agent_spec.personality.traits
        ])
        
        personality_adjectives = " and ".join([
            trait.name for trait in agent_spec.personality.traits[:2]
        ])
        
        # Format the prompt
        system_prompt = PromptBuilder.format_agent_prompt(
            template,
            name=agent_spec.name,
            domain=agent_spec.personality.domain_expertise[0] if agent_spec.personality.domain_expertise else "general",
            personality_traits=personality_traits,
            personality_adjectives=personality_adjectives,
            communication_style=agent_spec.personality.communication_style,
            decision_style=agent_spec.personality.decision_style
        )
        
        return system_prompt
    
    async def configure_agent_tools(
        self,
        agent_spec: AgentSpecification,
        available_tools: List[str]
    ) -> List[str]:
        """
        Configure tools for an agent based on their role and domain.
        
        Args:
            agent_spec: Agent specification
            available_tools: List of available tools
            
        Returns:
            List of tools assigned to the agent
        """
        prompt = f"""Select appropriate tools for this agent:

Agent: {agent_spec.name}
Role: {agent_spec.role.value}
Capabilities: {', '.join(agent_spec.capabilities)}
Available Tools: {', '.join(available_tools)}

Select tools that:
1. Enable the agent to fulfill their role
2. Match their capabilities
3. Are appropriate for their domain
4. Don't create unnecessary complexity

Return a list of tool names that should be assigned to this agent."""

        # For now, return a subset of available tools
        # In full implementation, this would use AI selection
        if agent_spec.role == AgentRole.EXPLORER:
            return [t for t in available_tools if "search" in t or "analyze" in t]
        elif agent_spec.role == AgentRole.DEBATER:
            return [t for t in available_tools if "compare" in t or "evaluate" in t]
        else:
            return available_tools[:3]  # Default selection
    
    async def ensure_personality_diversity(
        self,
        existing_agents: List[AgentSpecification],
        new_agent: AgentSpecification
    ) -> Dict[str, Any]:
        """
        Ensure personality diversity in a team.
        
        Args:
            existing_agents: Already created agents
            new_agent: Newly created agent
            
        Returns:
            Diversity analysis and recommendations
        """
        prompt = f"""Analyze personality diversity in this agent team:

Existing Agents:
{self._format_agent_summaries(existing_agents)}

New Agent: {new_agent.name}
- Personality: {', '.join([t.name for t in new_agent.personality.traits])}
- Communication: {new_agent.personality.communication_style}

Evaluate:
1. Is there sufficient personality diversity?
2. Are there any problematic overlaps?
3. Will team dynamics be productive?
4. Are there missing personality types?
5. Recommendations for adjustments?

Provide specific insights and recommendations."""

        # Simplified analysis for now
        trait_overlap = self._calculate_trait_overlap(existing_agents, new_agent)
        
        return {
            "diversity_score": 1.0 - trait_overlap,
            "has_good_diversity": trait_overlap < 0.3,
            "recommendations": [
                "Consider adding more contrasting viewpoints" if trait_overlap > 0.5 else "Good diversity",
                f"Team has {len(existing_agents) + 1} members with varied perspectives"
            ]
        }
    
    def _build_personality_context(self, keywords: List[str]) -> str:
        """Build personality context from keywords"""
        contexts = []
        for keyword in keywords:
            if keyword in self.personality_templates:
                contexts.append(f"{keyword}: {', '.join(self.personality_templates[keyword])}")
        return "; ".join(contexts)
    
    def _select_prompt_template(self, role: AgentRole) -> Template:
        """Select appropriate prompt template based on role"""
        template_map = {
            AgentRole.EXPLORER: PromptTemplates.EXPLORER_BASE,
            AgentRole.DEBATER: PromptTemplates.DEBATER_BASE,
            AgentRole.RISK_ASSESSOR: PromptTemplates.RISK_ASSESSOR_BASE,
            AgentRole.DECISION_MAKER: PromptTemplates.DECISION_MAKER_BASE,
        }
        return template_map.get(role, PromptTemplates.EXPLORER_BASE)
    
    def _format_agent_summaries(self, agents: List[AgentSpecification]) -> str:
        """Format agent summaries for prompt"""
        summaries = []
        for agent in agents:
            traits = ", ".join([t.name for t in agent.personality.traits[:3]])
            summaries.append(f"- {agent.name} ({agent.role.value}): {traits}")
        return "\n".join(summaries)
    
    def _calculate_trait_overlap(
        self, 
        existing_agents: List[AgentSpecification],
        new_agent: AgentSpecification
    ) -> float:
        """Calculate trait overlap between agents"""
        if not existing_agents:
            return 0.0
        
        new_traits = set(t.name for t in new_agent.personality.traits)
        
        overlaps = []
        for agent in existing_agents:
            agent_traits = set(t.name for t in agent.personality.traits)
            overlap = len(new_traits & agent_traits) / max(len(new_traits), len(agent_traits))
            overlaps.append(overlap)
        
        return sum(overlaps) / len(overlaps)
    
    def get_created_agents(self) -> Dict[str, AgentSpecification]:
        """Get all created agents"""
        return self.created_agents.copy()
    
    def clear_agents(self):
        """Clear created agents cache"""
        self.created_agents.clear()
        logger.info("Cleared agent cache")