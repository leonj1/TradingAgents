"""
Prompt templates and utilities for the meta-agent system.
"""

from typing import Dict, List, Any
from string import Template


class PromptTemplates:
    """Collection of prompt templates for various agent types"""
    
    # Base templates for different agent roles
    EXPLORER_BASE = Template("""
You are a $domain specialist agent named $name with expertise in $specialty.
Your role is to explore and analyze $focus_area to provide comprehensive insights.

Personality traits:
$personality_traits

Communication style: $communication_style

Your task is to:
1. Thoroughly analyze the available information
2. Identify key patterns and insights
3. Provide detailed, nuanced observations
4. Highlight both opportunities and challenges
5. Support your analysis with evidence

Domain-specific context:
$domain_context

Remember to be $personality_adjectives in your analysis while maintaining professional rigor.
""")
    
    DEBATER_BASE = Template("""
You are a $position debater named $name participating in a structured debate about $topic.
Your stance is: $stance

Personality traits:
$personality_traits

Debate style: $debate_style

Your objectives:
1. Present compelling arguments for your position
2. Engage constructively with opposing viewpoints
3. Use evidence and logic to support your claims
4. Acknowledge valid counterpoints while defending your stance
5. Work towards a productive synthesis of ideas

Debate context:
$debate_context

Maintain a $tone tone while being $personality_adjectives in your argumentation.
""")
    
    RISK_ASSESSOR_BASE = Template("""
You are a risk assessment specialist named $name with a $risk_philosophy approach.
Your role is to evaluate proposals from a $perspective perspective.

Personality traits:
$personality_traits

Assessment style: $assessment_style

Your responsibilities:
1. Identify and analyze potential risks
2. Evaluate risk-reward tradeoffs
3. Propose mitigation strategies
4. Challenge assumptions appropriately
5. Provide balanced recommendations

Risk framework:
$risk_framework

Be $personality_adjectives while maintaining objectivity in your assessments.
""")
    
    DECISION_MAKER_BASE = Template("""
You are a decision-making agent named $name responsible for $decision_scope.
Your role is to synthesize inputs and make well-reasoned decisions.

Personality traits:
$personality_traits

Decision-making style: $decision_style

Your process:
1. Review all available information and arguments
2. Weigh different perspectives fairly
3. Apply domain-specific criteria
4. Make clear, actionable decisions
5. Provide thorough rationale

Decision criteria:
$decision_criteria

Approach decisions with a $personality_adjectives mindset while ensuring $quality_focus.
""")


class PromptBuilder:
    """Utility class for building prompts"""
    
    @staticmethod
    def build_personality_description(traits: List[Dict[str, Any]]) -> str:
        """Build a personality description from traits"""
        descriptions = []
        for trait in traits:
            strength = trait.get('strength', 0.5)
            if strength > 0.7:
                modifier = "strongly"
            elif strength > 0.4:
                modifier = "moderately"
            else:
                modifier = "slightly"
            
            descriptions.append(f"- {modifier} {trait['name']}: {trait['description']}")
        
        return "\n".join(descriptions)
    
    @staticmethod
    def build_domain_context(domain: str, specifics: Dict[str, Any]) -> str:
        """Build domain-specific context"""
        context_parts = [f"Domain: {domain}"]
        
        if "key_concepts" in specifics:
            context_parts.append(f"Key concepts: {', '.join(specifics['key_concepts'])}")
        
        if "constraints" in specifics:
            context_parts.append("Constraints:")
            for constraint, value in specifics['constraints'].items():
                context_parts.append(f"- {constraint}: {value}")
        
        if "success_metrics" in specifics:
            context_parts.append(f"Success metrics: {', '.join(specifics['success_metrics'])}")
        
        return "\n".join(context_parts)
    
    @staticmethod
    def build_debate_context(topic: str, participants: List[str], round_num: int) -> str:
        """Build context for a debate"""
        return f"""
Debate topic: {topic}
Participants: {', '.join(participants)}
Current round: {round_num}

Guidelines:
- Address arguments directly and constructively
- Support claims with evidence
- Acknowledge valid points from others
- Work towards productive synthesis
- Maintain respectful discourse
"""
    
    @staticmethod
    def format_agent_prompt(template: Template, **kwargs) -> str:
        """Format an agent prompt with error handling"""
        try:
            # Provide defaults for common fields
            defaults = {
                'personality_adjectives': 'thoughtful and thorough',
                'personality_traits': 'Professional and analytical',
                'communication_style': 'Clear and concise',
                'domain_context': '',
                'tone': 'professional'
            }
            
            # Merge defaults with provided kwargs
            prompt_vars = {**defaults, **kwargs}
            
            return template.safe_substitute(**prompt_vars)
        except Exception as e:
            raise ValueError(f"Error formatting prompt: {str(e)}")


class DomainPrompts:
    """Domain-specific prompt enhancements"""
    
    DOMAIN_ENHANCEMENTS = {
        "cooking": {
            "explorers": {
                "focus_areas": ["ingredients", "techniques", "flavors", "nutrition"],
                "key_concepts": ["taste profiles", "cooking methods", "dietary restrictions", 
                               "ingredient compatibility", "nutritional balance"],
                "quality_focus": "delicious and nutritious outcomes"
            },
            "debaters": {
                "stances": ["traditional techniques", "modern innovation"],
                "debate_points": ["authenticity vs creativity", "time vs quality", 
                                "cost vs premium ingredients"]
            }
        },
        "healthcare": {
            "explorers": {
                "focus_areas": ["symptoms", "medical history", "research", "lifestyle"],
                "key_concepts": ["evidence-based medicine", "patient safety", 
                               "treatment efficacy", "quality of life"],
                "quality_focus": "patient wellbeing and safety"
            },
            "debaters": {
                "stances": ["conservative treatment", "proactive intervention"],
                "debate_points": ["risk vs benefit", "immediate vs long-term", 
                                "standard vs personalized care"]
            }
        },
        "technical_writing": {
            "explorers": {
                "focus_areas": ["structure", "clarity", "accuracy", "audience"],
                "key_concepts": ["documentation standards", "user experience", 
                               "technical accuracy", "accessibility"],
                "quality_focus": "clear and comprehensive documentation"
            },
            "debaters": {
                "stances": ["detailed comprehensiveness", "concise clarity"],
                "debate_points": ["depth vs brevity", "technical vs accessible", 
                                "examples vs concepts"]
            }
        }
    }
    
    @classmethod
    def get_domain_enhancements(cls, domain: str) -> Dict[str, Any]:
        """Get domain-specific enhancements"""
        return cls.DOMAIN_ENHANCEMENTS.get(
            domain.lower(),
            {
                "explorers": {
                    "focus_areas": ["key aspects", "important factors", "critical elements"],
                    "key_concepts": ["domain expertise", "best practices", "quality standards"],
                    "quality_focus": "optimal outcomes"
                },
                "debaters": {
                    "stances": ["position A", "position B"],
                    "debate_points": ["tradeoffs", "priorities", "approaches"]
                }
            }
        )