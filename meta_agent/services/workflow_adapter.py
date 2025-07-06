"""
WorkflowAdapter: Adapts the generic workflow to specific domains.
"""

import logging
from typing import List, Dict, Any

from pydantic import BaseModel, Field

from .base import BaseAIService
from ..schemas.domain import DomainWorkflow, WorkflowPhase

logger = logging.getLogger(__name__)


class WorkflowAdaptationRequest(BaseModel):
    """Request for workflow adaptation"""
    domain: str = Field(..., description="Target domain")
    base_workflow: str = Field(..., description="Base workflow pattern")
    domain_requirements: List[str] = Field(..., description="Domain-specific requirements")
    constraints: Dict[str, Any] = Field(
        default_factory=dict, description="Workflow constraints"
    )


class AdaptedWorkflow(BaseModel):
    """Adapted workflow for a specific domain"""
    workflow: DomainWorkflow = Field(..., description="The adapted workflow")
    adaptations: List[str] = Field(..., description="Key adaptations made")
    optimization_notes: str = Field(..., description="Notes on optimizations")
    risk_considerations: List[str] = Field(
        default_factory=list, description="Risk considerations"
    )


class WorkflowAdapter(BaseAIService[AdaptedWorkflow]):
    """
    Adapts generic multi-agent workflows to specific domain requirements.
    """
    
    def __init__(self, api_key: str):
        """Initialize the workflow adapter"""
        super().__init__(api_key)
        
    def get_system_prompt(self) -> str:
        """System prompt for workflow adaptation"""
        return """You are an expert in workflow design and adaptation for multi-agent systems. 
You specialize in:

1. Adapting generic workflows to domain-specific needs
2. Optimizing phase transitions and agent coordination
3. Identifying domain-specific workflow requirements
4. Ensuring workflow efficiency and effectiveness
5. Managing workflow risks and contingencies

When adapting workflows, you consider:
- Domain-specific constraints and requirements
- Optimal phase sequencing
- Agent coordination needs
- Resource and time efficiency
- Quality assurance checkpoints

Your workflow designs are practical, efficient, and domain-optimized."""
    
    def get_response_model(self) -> type[BaseModel]:
        """Return the response model"""
        return AdaptedWorkflow
    
    async def adapt_workflow(
        self,
        request: WorkflowAdaptationRequest
    ) -> AdaptedWorkflow:
        """Adapt a workflow for a specific domain"""
        prompt = f"""Adapt the {request.base_workflow} workflow pattern for the {request.domain} domain:

Domain Requirements:
{self._format_requirements(request.domain_requirements)}

Constraints:
{self._format_constraints(request.constraints)}

Create an adapted workflow that:
1. Maintains the explore → debate → synthesize pattern
2. Addresses all domain requirements
3. Optimizes for domain-specific needs
4. Includes appropriate validation steps
5. Manages domain-specific risks

Design workflow phases with:
- Clear agent assignments
- Realistic time estimates
- Specific inputs/outputs
- Validation criteria
- Phase transitions

Explain key adaptations and optimizations made."""

        logger.info(f"Adapting workflow for {request.domain}")
        
        return await self.invoke_agent(prompt)
    
    async def optimize_workflow(
        self,
        workflow: DomainWorkflow,
        performance_data: Dict[str, Any]
    ) -> AdaptedWorkflow:
        """Optimize an existing workflow based on performance data"""
        prompt = f"""Optimize this workflow based on performance data:

Current Workflow: {workflow.domain}
Phases: {len(workflow.phases)}
Performance Metrics:
{self._format_performance_data(performance_data)}

Identify optimizations for:
1. Phase sequencing
2. Agent utilization
3. Time efficiency
4. Quality improvements
5. Risk mitigation

Provide specific, actionable optimizations."""

        return await self.invoke_agent(prompt)
    
    def _format_requirements(self, requirements: List[str]) -> str:
        """Format requirements for prompt"""
        return "\n".join([f"- {req}" for req in requirements])
    
    def _format_constraints(self, constraints: Dict[str, Any]) -> str:
        """Format constraints for prompt"""
        return "\n".join([f"- {k}: {v}" for k, v in constraints.items()])
    
    def _format_performance_data(self, data: Dict[str, Any]) -> str:
        """Format performance data for prompt"""
        formatted = []
        for metric, value in data.items():
            formatted.append(f"- {metric}: {value}")
        return "\n".join(formatted)