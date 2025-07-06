"""
Meta-Agent System: Dynamic Domain-Specific Agent Team Generator

This system can analyze any domain and dynamically create specialized agent teams
that follow the explore → debate → synthesize pattern from TradingAgents.
"""

__version__ = "0.1.0"

from .services.base import BaseAIService
from .services.meta_orchestrator import MetaAgentOrchestrator
from .services.domain_analyzer import DomainAnalyzer
from .services.agent_factory import AgentFactory
from .services.debate_orchestrator import DebateOrchestrator
from .services.personality_generator import PersonalityGenerator
from .services.tool_selector import ToolSelector
from .services.quality_validator import QualityValidator
from .services.workflow_adapter import WorkflowAdapter
from .services.topic_analyzer import TopicAnalyzer

__all__ = [
    "BaseAIService",
    "MetaAgentOrchestrator",
    "DomainAnalyzer", 
    "AgentFactory",
    "DebateOrchestrator",
    "PersonalityGenerator",
    "ToolSelector",
    "QualityValidator",
    "WorkflowAdapter",
    "TopicAnalyzer",
]