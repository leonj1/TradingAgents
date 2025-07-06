"""
QualityValidator: Validates generated agents and their outputs.
"""

import logging
from typing import List, Dict, Any

from pydantic import BaseModel, Field

from .base import BaseAIService
from ..schemas.domain import AgentSpecification, TaskResult

logger = logging.getLogger(__name__)


class ValidationRequest(BaseModel):
    """Request for validation"""
    validation_type: str = Field(..., description="Type of validation")
    subject: Any = Field(..., description="Subject to validate")
    criteria: List[str] = Field(..., description="Validation criteria")
    context: Dict[str, Any] = Field(
        default_factory=dict, description="Additional context"
    )


class ValidationResult(BaseModel):
    """Result of validation"""
    is_valid: bool = Field(..., description="Whether validation passed")
    quality_score: float = Field(..., ge=0.0, le=1.0, description="Quality score")
    issues: List[str] = Field(default_factory=list, description="Issues found")
    improvements: List[str] = Field(
        default_factory=list, description="Suggested improvements"
    )
    strengths: List[str] = Field(default_factory=list, description="Identified strengths")


class QualityValidator(BaseAIService[ValidationResult]):
    """
    Validates the quality of generated agents and their outputs.
    """
    
    def __init__(self, api_key: str):
        """Initialize the quality validator"""
        super().__init__(api_key)
        
    def get_system_prompt(self) -> str:
        """System prompt for quality validation"""
        return """You are an expert quality validator for AI systems, specializing in 
evaluating agents and their outputs. You assess:

1. Agent coherence and effectiveness
2. Output quality and accuracy
3. Domain appropriateness
4. Task completion effectiveness
5. System integration quality

Your validation approach is:
- Thorough and systematic
- Constructive and improvement-focused
- Based on clear criteria
- Practical and actionable

You provide specific, actionable feedback for improvement."""
    
    def get_response_model(self) -> type[BaseModel]:
        """Return the response model"""
        return ValidationResult
    
    async def validate_agent(
        self,
        agent: AgentSpecification,
        domain: str
    ) -> ValidationResult:
        """Validate an agent specification"""
        prompt = f"""Validate this agent specification for the {domain} domain:

Agent Name: {agent.name}
Role: {agent.role.value}
Personality Traits: {', '.join([t.name for t in agent.personality.traits])}
Communication Style: {agent.personality.communication_style}
Capabilities: {', '.join(agent.capabilities)}

Validation Criteria:
1. Role-personality alignment
2. Domain appropriateness
3. Capability completeness
4. Team compatibility potential
5. Practical implementability

Assess the agent's validity, quality, and potential effectiveness."""

        logger.info(f"Validating agent: {agent.name}")
        
        return await self.invoke_agent(prompt)
    
    async def validate_output(
        self,
        task_result: TaskResult,
        expected_quality: Dict[str, Any]
    ) -> ValidationResult:
        """Validate task output quality"""
        prompt = f"""Validate this task output:

Domain: {task_result.domain}
Task Status: {task_result.status}
Quality Score: {task_result.quality_score}
Execution Time: {task_result.execution_time}s
Decision Rationale: {task_result.decision_rationale}

Expected Quality Metrics:
{self._format_quality_metrics(expected_quality)}

Evaluate:
1. Output completeness
2. Decision quality
3. Process effectiveness
4. Time efficiency
5. Overall quality

Provide specific feedback on strengths and areas for improvement."""

        return await self.invoke_agent(prompt)
    
    def _format_quality_metrics(self, metrics: Dict[str, Any]) -> str:
        """Format quality metrics for prompt"""
        formatted = []
        for metric, value in metrics.items():
            formatted.append(f"- {metric}: {value}")
        return "\n".join(formatted)