"""
PersonalityGenerator: Creates coherent, domain-appropriate agent personalities.
"""

import logging
from typing import List, Dict, Any
import random

from pydantic import BaseModel, Field

from .base import BaseAIService
from ..schemas.domain import AgentPersonality, PersonalityTrait

logger = logging.getLogger(__name__)


class PersonalityRequest(BaseModel):
    """Request for personality generation"""
    role: str = Field(..., description="Agent's role")
    domain: str = Field(..., description="Domain of operation")
    required_traits: List[str] = Field(
        default_factory=list, description="Required personality traits"
    )
    avoid_traits: List[str] = Field(
        default_factory=list, description="Traits to avoid"
    )
    team_context: List[str] = Field(
        default_factory=list, description="Existing team member traits"
    )


class PersonalityGenerator(BaseAIService[AgentPersonality]):
    """
    Generates coherent, domain-appropriate personalities for agents.
    """
    
    def __init__(self, api_key: str):
        """Initialize the personality generator"""
        super().__init__(api_key)
        
    def get_system_prompt(self) -> str:
        """System prompt for personality generation"""
        return """You are an expert in personality design for AI agents, specializing in 
creating coherent, effective, and domain-appropriate personalities. You understand:

1. How personality traits influence agent behavior and effectiveness
2. The importance of trait balance and coherence
3. Domain-specific personality requirements
4. Team dynamics and complementary personalities
5. Communication and decision-making style alignment

When creating personalities, you ensure:
- Traits are internally consistent and realistic
- Communication style matches personality traits
- Decision-making approach aligns with role and traits
- Domain expertise is reflected in personality
- Team compatibility is considered

Your personalities are nuanced, practical, and enhance agent effectiveness."""
    
    def get_response_model(self) -> type[BaseModel]:
        """Return the response model"""
        return AgentPersonality
    
    async def generate_personality(
        self,
        request: PersonalityRequest
    ) -> AgentPersonality:
        """Generate a complete personality profile"""
        prompt = f"""Create a coherent personality profile for an agent with these requirements:

Role: {request.role}
Domain: {request.domain}
Required Traits: {', '.join(request.required_traits) if request.required_traits else 'None specified'}
Avoid Traits: {', '.join(request.avoid_traits) if request.avoid_traits else 'None specified'}
Team Context: {', '.join(request.team_context) if request.team_context else 'Working independently'}

Create a personality that includes:
1. 3-5 personality traits with:
   - Clear names and descriptions
   - Strength values (0-1) indicating trait prominence
   - Domain-specific manifestations

2. Communication style that:
   - Reflects the personality traits
   - Is appropriate for the domain
   - Enhances effectiveness in the role

3. Decision-making style that:
   - Aligns with personality traits
   - Suits the agent's role
   - Is effective in the domain

4. Domain expertise areas that complement the personality

Ensure the personality is coherent, distinctive, and effective for the intended role."""

        logger.info(f"Generating personality for {request.role} in {request.domain}")
        
        return await self.invoke_agent(prompt)
    
    async def ensure_diversity(
        self,
        existing_personalities: List[AgentPersonality],
        new_personality: AgentPersonality
    ) -> Dict[str, Any]:
        """Ensure personality diversity in a team"""
        diversity_score = self._calculate_diversity_score(
            existing_personalities,
            new_personality
        )
        
        return {
            "diversity_score": diversity_score,
            "is_diverse": diversity_score > 0.6,
            "recommendations": await self._get_diversity_recommendations(
                existing_personalities,
                new_personality,
                diversity_score
            )
        }
    
    async def map_to_domain(
        self,
        personality: AgentPersonality,
        domain: str
    ) -> AgentPersonality:
        """Map generic personality traits to domain-specific behaviors"""
        prompt = f"""Adapt this personality profile to the {domain} domain:

Current Traits:
{self._format_personality_traits(personality.traits)}

Communication Style: {personality.communication_style}
Decision Style: {personality.decision_style}

Adapt the personality by:
1. Adding domain-specific manifestations to each trait
2. Adjusting communication style for domain appropriateness
3. Refining decision-making approach for domain requirements
4. Adding relevant domain expertise areas

Maintain the core personality while making it domain-appropriate."""

        adapted = await self.invoke_agent(prompt)
        
        # Update domain mappings
        for i, trait in enumerate(adapted.traits):
            if i < len(personality.traits):
                trait.domain_mapping[domain] = f"In {domain}: {trait.description}"
        
        return adapted
    
    def _calculate_diversity_score(
        self,
        existing: List[AgentPersonality],
        new: AgentPersonality
    ) -> float:
        """Calculate diversity score between personalities"""
        if not existing:
            return 1.0
        
        new_traits = set(t.name.lower() for t in new.traits)
        
        diversity_scores = []
        for personality in existing:
            existing_traits = set(t.name.lower() for t in personality.traits)
            overlap = len(new_traits & existing_traits)
            diversity = 1.0 - (overlap / max(len(new_traits), len(existing_traits)))
            diversity_scores.append(diversity)
        
        return sum(diversity_scores) / len(diversity_scores)
    
    async def _get_diversity_recommendations(
        self,
        existing: List[AgentPersonality],
        new: AgentPersonality,
        score: float
    ) -> List[str]:
        """Get recommendations for improving diversity"""
        if score > 0.7:
            return ["Good personality diversity maintained"]
        elif score > 0.4:
            return [
                "Consider emphasizing unique traits",
                "Differentiate communication style further"
            ]
        else:
            return [
                "Personality too similar to existing team members",
                "Add contrasting traits for better team dynamics",
                "Consider different decision-making style"
            ]
    
    def _format_personality_traits(self, traits: List[PersonalityTrait]) -> str:
        """Format traits for prompt"""
        formatted = []
        for trait in traits:
            formatted.append(
                f"- {trait.name} (strength: {trait.strength}): {trait.description}"
            )
        return "\n".join(formatted)