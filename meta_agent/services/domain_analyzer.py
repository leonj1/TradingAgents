"""
DomainAnalyzer: Analyzes domains to determine optimal agent compositions and workflows.
"""

import logging
from typing import List, Dict, Any, Optional

from pydantic import BaseModel, Field

from .base import BaseAIService
from ..schemas.domain import DomainAnalysis, DebateStructure
from ..utils.prompts import DomainPrompts

logger = logging.getLogger(__name__)


class DomainInsights(BaseModel):
    """Detailed insights about a domain"""
    core_concepts: List[str] = Field(..., description="Core concepts in the domain")
    key_challenges: List[str] = Field(..., description="Main challenges to address")
    success_factors: List[str] = Field(..., description="Factors that determine success")
    common_pitfalls: List[str] = Field(..., description="Common mistakes to avoid")
    best_practices: List[str] = Field(..., description="Domain best practices")


class DomainAnalyzer(BaseAIService[DomainAnalysis]):
    """
    Analyzes domains to determine required specialists, debate structures,
    and optimal workflows for agent teams.
    """
    
    def __init__(self, api_key: str):
        """Initialize the domain analyzer"""
        super().__init__(api_key)
        self.domain_cache: Dict[str, DomainAnalysis] = {}
        
    def get_system_prompt(self) -> str:
        """System prompt for domain analysis"""
        return """You are an expert domain analyzer specializing in understanding complex 
domains and determining optimal multi-agent team compositions. Your expertise spans:

1. Domain decomposition and analysis
2. Identifying key specialist roles needed
3. Determining productive debate structures
4. Mapping domain-specific tools and data sources
5. Establishing success metrics and quality criteria

You understand that effective multi-agent systems require:
- Diverse perspectives from specialized agents
- Structured debates between opposing viewpoints
- Clear role definitions and responsibilities
- Domain-appropriate tools and resources
- Measurable success criteria

When analyzing a domain, you consider:
- The complexity and nuances of the domain
- Types of expertise required
- Natural tensions that create productive debates
- Information sources and tools needed
- How to measure quality and success

Your analyses are comprehensive, insightful, and actionable, providing clear 
specifications for building effective agent teams."""
    
    def get_response_model(self) -> type[BaseModel]:
        """Return the response model for structured outputs"""
        return DomainAnalysis
    
    async def analyze_domain(
        self, 
        domain: str, 
        task_context: str,
        constraints: Optional[Dict[str, Any]] = None
    ) -> DomainAnalysis:
        """
        Analyze a domain to determine optimal agent composition.
        
        Args:
            domain: The domain to analyze
            task_context: Context about what tasks will be performed
            constraints: Any constraints to consider
            
        Returns:
            Comprehensive domain analysis
        """
        # Check cache first
        cache_key = f"{domain}:{task_context}"
        if cache_key in self.domain_cache:
            logger.info(f"Returning cached analysis for {domain}")
            return self.domain_cache[cache_key]
        
        # Get domain-specific enhancements
        enhancements = DomainPrompts.get_domain_enhancements(domain)
        
        prompt = f"""Analyze the {domain} domain for the following context:

Task Context: {task_context}
Constraints: {constraints or 'None specified'}

Domain-Specific Knowledge:
- Focus Areas: {', '.join(enhancements['explorers']['focus_areas'])}
- Key Concepts: {', '.join(enhancements['explorers']['key_concepts'])}
- Quality Focus: {enhancements['explorers']['quality_focus']}

Create a comprehensive domain analysis that includes:

1. REQUIRED SPECIALISTS (4-6 explorer agents):
   - Name each specialist clearly
   - Define their specific expertise area
   - Explain why they're essential for this domain

2. DEBATE STRUCTURE:
   - Identify 2-3 debaters with naturally opposing perspectives
   - Define the core tensions/tradeoffs they'll debate
   - Specify debate format and synthesis approach

3. RISK ASSESSORS (optional but recommended):
   - If applicable, define 2-3 risk assessment perspectives
   - Focus on different dimensions of quality/safety/efficiency

4. DATA SOURCES:
   - List specific data sources needed
   - Include both real-time and historical data needs
   - Consider domain-specific databases or APIs

5. TOOLS NEEDED:
   - Analytical tools required by agents
   - Domain-specific software or APIs
   - Validation and testing tools

6. SUCCESS METRICS:
   - How to measure task completion
   - Quality indicators specific to the domain
   - Both quantitative and qualitative metrics

7. CONSTRAINTS AND CONSIDERATIONS:
   - Ethical considerations
   - Regulatory requirements
   - Resource limitations
   - Time constraints

Ensure your analysis is practical and actionable for building an agent team."""

        logger.info(f"Analyzing domain: {domain}")
        
        result = await self.invoke_agent(prompt)
        
        # Cache the result
        self.domain_cache[cache_key] = result
        
        return result
    
    async def identify_specialists(
        self, 
        domain: str,
        focus_areas: List[str]
    ) -> List[Dict[str, str]]:
        """
        Identify specific specialists needed for focus areas.
        
        Args:
            domain: The domain being analyzed
            focus_areas: Specific areas that need coverage
            
        Returns:
            List of specialist specifications
        """
        prompt = f"""For the {domain} domain, identify specialists for these focus areas:
{', '.join(focus_areas)}

For each specialist, provide:
1. Name (e.g., "Nutrition Analyst", "Risk Evaluator")
2. Expertise description
3. Key responsibilities
4. Information they need access to
5. How they contribute to the overall analysis

Ensure specialists have complementary skills and minimal overlap."""

        result = await self.invoke_agent(prompt)
        
        # Parse the response into structured format
        specialists = []
        # In a full implementation, we'd parse the structured response
        # For now, return a placeholder
        for i, area in enumerate(focus_areas):
            specialists.append({
                "name": f"{area.title()} Specialist",
                "expertise": f"Expert in {area} within {domain}",
                "focus_area": area
            })
        
        return specialists
    
    async def determine_debate_structure(
        self, 
        domain: str,
        key_decisions: List[str]
    ) -> DebateStructure:
        """
        Determine optimal debate structure for the domain.
        
        Args:
            domain: The domain being analyzed
            key_decisions: Key decisions that need to be made
            
        Returns:
            Recommended debate structure
        """
        prompt = f"""Design a debate structure for the {domain} domain that addresses 
these key decisions: {', '.join(key_decisions)}

Consider:
1. What opposing perspectives create productive tension?
2. How many debate rounds are optimal?
3. Should there be a moderator?
4. How to synthesize different viewpoints?
5. What rules ensure constructive debate?

Provide a specific debate structure that will lead to well-reasoned decisions."""

        # For now, return a default structure
        # In full implementation, this would be parsed from the AI response
        return DebateStructure(
            participants=[f"{domain} Optimist", f"{domain} Skeptic"],
            rounds=3,
            moderator_required=True,
            synthesis_method="weighted_consensus",
            rules=[
                "Address arguments directly with evidence",
                "Acknowledge valid points from opponents",
                "Focus on domain-specific criteria",
                "Work towards actionable conclusions"
            ]
        )
    
    async def get_domain_insights(self, domain: str) -> DomainInsights:
        """
        Get deep insights about a domain.
        
        Args:
            domain: The domain to analyze
            
        Returns:
            Detailed domain insights
        """
        prompt = f"""Provide deep insights about the {domain} domain:

1. Core Concepts: What are the fundamental concepts everyone must understand?
2. Key Challenges: What makes this domain difficult or complex?
3. Success Factors: What determines success in this domain?
4. Common Pitfalls: What mistakes do people commonly make?
5. Best Practices: What are proven approaches that work well?

Be specific and practical in your insights."""

        # Simplified response for now
        return DomainInsights(
            core_concepts=[f"Core concept {i+1} for {domain}" for i in range(5)],
            key_challenges=[f"Challenge {i+1} in {domain}" for i in range(4)],
            success_factors=[f"Success factor {i+1}" for i in range(4)],
            common_pitfalls=[f"Common pitfall {i+1}" for i in range(3)],
            best_practices=[f"Best practice {i+1}" for i in range(5)]
        )
    
    def get_cached_domains(self) -> List[str]:
        """Get list of domains that have been analyzed and cached"""
        return list(set(key.split(':')[0] for key in self.domain_cache.keys()))
    
    def clear_cache(self, domain: Optional[str] = None):
        """Clear analysis cache, optionally for a specific domain"""
        if domain:
            keys_to_remove = [k for k in self.domain_cache.keys() if k.startswith(f"{domain}:")]
            for key in keys_to_remove:
                del self.domain_cache[key]
            logger.info(f"Cleared cache for domain: {domain}")
        else:
            self.domain_cache.clear()
            logger.info("Cleared entire domain cache")