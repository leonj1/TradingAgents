"""
TopicAnalyzer: Analyzes user topics to determine domain and requirements.
"""

import logging
from typing import Dict, Any, List, Optional, Tuple

from pydantic import BaseModel, Field

from .base import BaseAIService
from ..schemas.domain import TaskRequest

logger = logging.getLogger(__name__)


class TopicAnalysis(BaseModel):
    """Result of topic analysis"""
    topic: str = Field(..., description="Original topic")
    domain: str = Field(..., description="Identified domain")
    domain_confidence: float = Field(
        ..., ge=0.0, le=1.0, description="Confidence in domain identification"
    )
    task_type: str = Field(..., description="Type of task (analysis, creation, decision, etc.)")
    key_concepts: List[str] = Field(..., description="Key concepts identified")
    requirements: List[str] = Field(..., description="Extracted requirements")
    constraints: Dict[str, Any] = Field(
        default_factory=dict, description="Identified constraints"
    )
    specialist_needs: List[str] = Field(
        ..., description="Types of specialists needed"
    )
    debate_topics: List[str] = Field(
        ..., description="Potential debate topics"
    )
    expected_output_type: str = Field(
        ..., description="Type of output expected"
    )
    complexity_level: str = Field(
        ..., description="Estimated complexity (simple, moderate, complex)"
    )


class TopicAnalyzer(BaseAIService[TopicAnalysis]):
    """
    Analyzes user-submitted topics to determine the appropriate domain,
    requirements, and agent team composition.
    """
    
    def __init__(self, api_key: str):
        """Initialize the topic analyzer"""
        super().__init__(api_key)
        self.domain_keywords = self._initialize_domain_keywords()
        
    def get_system_prompt(self) -> str:
        """System prompt for topic analysis"""
        return """You are an expert topic analyzer specializing in understanding user 
requests and mapping them to appropriate domains and requirements. You excel at:

1. Identifying the core domain from natural language topics
2. Extracting implicit requirements and constraints
3. Determining what types of specialists would be needed
4. Identifying potential areas of debate or tradeoffs
5. Understanding the expected output format

You can analyze topics across all domains including but not limited to:
- Cooking and culinary arts
- Healthcare and medicine
- Technology and programming
- Finance and investing
- Education and learning
- Science and research
- Business and entrepreneurship
- Arts and creativity
- Environmental and sustainability
- Legal and regulatory
- Engineering and construction
- Entertainment and media

When analyzing a topic, you:
- Look for both explicit and implicit requirements
- Consider the user's likely intent and goals
- Identify constraints (time, budget, resources, etc.)
- Determine the complexity level
- Suggest appropriate specialist perspectives
- Identify natural debate points

Your analysis is thorough, insightful, and actionable for building agent teams."""
    
    def get_response_model(self) -> type[BaseModel]:
        """Return the response model"""
        return TopicAnalysis
    
    def _initialize_domain_keywords(self) -> Dict[str, List[str]]:
        """Initialize domain keyword mappings"""
        return {
            "cooking": ["recipe", "cook", "food", "meal", "ingredient", "cuisine", 
                       "bake", "chef", "kitchen", "dish", "menu", "nutrition"],
            "healthcare": ["health", "medical", "symptom", "treatment", "diagnosis",
                          "medicine", "patient", "doctor", "wellness", "therapy"],
            "technology": ["code", "program", "software", "app", "system", "tech",
                          "development", "api", "database", "algorithm"],
            "finance": ["invest", "money", "stock", "trading", "budget", "financial",
                       "portfolio", "market", "economy", "crypto"],
            "education": ["learn", "teach", "course", "study", "education", "training",
                         "curriculum", "student", "knowledge", "skill"],
            "environment": ["sustainable", "eco", "green", "carbon", "climate",
                           "renewable", "conservation", "pollution", "waste"],
            "business": ["business", "startup", "company", "strategy", "marketing",
                        "sales", "entrepreneur", "management", "growth"],
            "science": ["research", "experiment", "hypothesis", "data", "analysis",
                       "scientific", "study", "theory", "evidence"],
            "creative": ["design", "art", "creative", "music", "write", "compose",
                        "artistic", "aesthetic", "style", "expression"],
            "legal": ["law", "legal", "contract", "regulation", "compliance",
                     "rights", "policy", "litigation", "attorney"]
        }
    
    async def analyze_topic(self, topic: str) -> TopicAnalysis:
        """
        Analyze a user-submitted topic to determine domain and requirements.
        
        Args:
            topic: The user's topic or question
            
        Returns:
            Comprehensive topic analysis
        """
        # First, try quick domain detection
        quick_domain = self._quick_domain_detection(topic.lower())
        
        prompt = f"""Analyze this user topic in detail:

TOPIC: {topic}

Quick domain hint: {quick_domain or 'No clear domain detected'}

Provide a comprehensive analysis including:

1. DOMAIN IDENTIFICATION:
   - Primary domain (single word like: cooking, healthcare, technology, etc.)
   - Confidence level (0-1) in this identification
   - Why this domain was chosen

2. TASK TYPE:
   - What type of task is this? (analysis, creation, decision, optimization, 
     comparison, troubleshooting, planning, evaluation)

3. KEY CONCEPTS:
   - 3-5 main concepts central to this topic
   - Technical terms or specialized knowledge areas

4. REQUIREMENTS:
   - What the user is trying to achieve
   - Implicit needs not directly stated
   - Success criteria

5. CONSTRAINTS:
   - Time constraints (if any mentioned or implied)
   - Resource constraints (budget, materials, etc.)
   - Other limitations

6. SPECIALIST NEEDS:
   - 4-6 types of specialists that would be valuable
   - Why each specialist is needed
   - Focus on diverse, complementary perspectives

7. DEBATE TOPICS:
   - 2-3 natural areas of debate or tradeoffs
   - Opposing viewpoints that would be productive
   - Key decisions that need to be made

8. EXPECTED OUTPUT:
   - What type of result the user expects
   - Format (plan, recommendation, analysis, etc.)

9. COMPLEXITY:
   - Rate as simple, moderate, or complex
   - Factors contributing to complexity

Be thorough and insightful in your analysis."""

        logger.info(f"Analyzing topic: {topic[:100]}...")
        
        result = await self.invoke_agent(prompt)
        
        return result
    
    def _quick_domain_detection(self, topic_lower: str) -> Optional[str]:
        """Quick keyword-based domain detection"""
        domain_scores = {}
        
        for domain, keywords in self.domain_keywords.items():
            score = sum(1 for keyword in keywords if keyword in topic_lower)
            if score > 0:
                domain_scores[domain] = score
        
        if domain_scores:
            return max(domain_scores, key=domain_scores.get)
        return None
    
    async def extract_requirements(
        self, 
        topic: str,
        analysis: TopicAnalysis
    ) -> TaskRequest:
        """
        Convert topic analysis into a formal task request.
        
        Args:
            topic: Original topic
            analysis: Topic analysis results
            
        Returns:
            Formal task request for the orchestrator
        """
        task_request = TaskRequest(
            domain=analysis.domain,
            task_description=topic,
            constraints=analysis.constraints,
            expected_output=analysis.expected_output_type,
            priority=self._determine_priority(analysis.complexity_level)
        )
        
        return task_request
    
    def _determine_priority(self, complexity: str) -> str:
        """Determine task priority based on complexity"""
        priority_map = {
            "simple": "low",
            "moderate": "medium",
            "complex": "high"
        }
        return priority_map.get(complexity, "medium")
    
    async def suggest_team_composition(
        self,
        analysis: TopicAnalysis
    ) -> Dict[str, Any]:
        """
        Suggest optimal team composition based on analysis.
        
        Args:
            analysis: Topic analysis results
            
        Returns:
            Team composition suggestions
        """
        prompt = f"""Based on this topic analysis, suggest optimal agent team composition:

Domain: {analysis.domain}
Task Type: {analysis.task_type}
Specialists Needed: {', '.join(analysis.specialist_needs)}
Debate Topics: {', '.join(analysis.debate_topics)}

Suggest:
1. Specific agent roles and names
2. Key personality traits for each agent
3. Debate pairings
4. Workflow structure
5. Success metrics

Focus on creating a balanced, effective team."""

        # For now, return structured suggestions
        return {
            "explorers": analysis.specialist_needs[:4],
            "debaters": self._extract_debaters(analysis.debate_topics),
            "workflow_type": "standard" if analysis.complexity_level != "complex" else "extended",
            "estimated_agents": len(analysis.specialist_needs) + 2  # specialists + debaters
        }
    
    def _extract_debaters(self, debate_topics: List[str]) -> List[str]:
        """Extract debater roles from debate topics"""
        if not debate_topics:
            return ["Optimist", "Realist"]
        
        # Simple extraction - in full implementation, use AI
        debaters = []
        for topic in debate_topics[:2]:
            if "vs" in topic or "versus" in topic:
                parts = topic.replace("versus", "vs").split("vs")
                if len(parts) == 2:
                    debaters.extend([p.strip() for p in parts])
            else:
                # Generic opposing views
                debaters.extend(["Progressive View", "Traditional View"])
                break
        
        return debaters[:2]  # Maximum 2 debaters
    
    async def refine_for_domain(
        self,
        topic: str,
        suggested_domain: str
    ) -> TopicAnalysis:
        """
        Refine analysis with a specific domain focus.
        
        Args:
            topic: Original topic
            suggested_domain: User-suggested domain
            
        Returns:
            Refined topic analysis
        """
        prompt = f"""Analyze this topic specifically within the {suggested_domain} domain:

TOPIC: {topic}
SPECIFIED DOMAIN: {suggested_domain}

Provide analysis tailored to this domain, including domain-specific:
- Specialists
- Constraints
- Debate topics
- Success metrics

Ensure all suggestions are highly relevant to {suggested_domain}."""

        return await self.invoke_agent(prompt)