"""
MetaAgentOrchestrator: The main orchestrator that creates and manages domain-specific agent teams.
"""

import asyncio
import logging
from typing import Dict, Any, List, Optional
from uuid import uuid4

from pydantic import BaseModel, Field

from .base import BaseAIService
from ..schemas.domain import (
    TaskRequest, TaskResult, AgentTeam, DomainAnalysis,
    AgentSpecification, DomainWorkflow
)

logger = logging.getLogger(__name__)


class OrchestrationPlan(BaseModel):
    """Plan for orchestrating a task"""
    task_id: str = Field(..., description="Unique task identifier")
    domain_analysis: DomainAnalysis = Field(..., description="Domain analysis results")
    agent_team: AgentTeam = Field(..., description="Configured agent team")
    execution_strategy: str = Field(..., description="How to execute the task")
    estimated_duration: int = Field(..., description="Estimated duration in seconds")
    resource_requirements: Dict[str, Any] = Field(
        default_factory=dict, description="Required resources"
    )


class MetaAgentOrchestrator(BaseAIService[OrchestrationPlan]):
    """
    Main orchestrator that creates and manages domain-specific agent teams.
    This is the entry point for the meta-agent system.
    """
    
    def __init__(self, api_key: str):
        """Initialize the orchestrator with required services"""
        super().__init__(api_key)
        self.active_teams: Dict[str, AgentTeam] = {}
        self.task_history: List[TaskResult] = []
        
    def get_system_prompt(self) -> str:
        """System prompt for the meta-orchestrator"""
        return """You are a meta-agent orchestrator responsible for creating and managing 
domain-specific agent teams. Your role is to:

1. Analyze incoming tasks to understand domain requirements
2. Design optimal agent team compositions
3. Create workflow plans that leverage agent specializations
4. Orchestrate multi-agent collaboration following the explore → debate → synthesize pattern
5. Ensure quality outcomes through proper team dynamics

You have deep understanding of:
- Multi-agent system design patterns
- Domain-specific requirements across various fields
- Effective team composition strategies
- Workflow optimization techniques
- Quality assurance in AI systems

When analyzing tasks, consider:
- Domain complexity and nuances
- Required specialist perspectives
- Optimal debate structures for the domain
- Resource and time constraints
- Success criteria and quality metrics

Your responses should be thorough, well-structured, and actionable, providing clear 
orchestration plans that can be executed by the system."""
    
    def get_response_model(self) -> type[BaseModel]:
        """Return the response model for structured outputs"""
        return OrchestrationPlan
    
    async def analyze_task(self, task_request: TaskRequest) -> OrchestrationPlan:
        """
        Analyze a task request and create an orchestration plan.
        
        Args:
            task_request: The incoming task request
            
        Returns:
            Complete orchestration plan
        """
        task_id = str(uuid4())
        
        prompt = f"""Analyze this task request and create a comprehensive orchestration plan:

Domain: {task_request.domain}
Task: {task_request.task_description}
Expected Output: {task_request.expected_output}
Constraints: {task_request.constraints}
Priority: {task_request.priority}

Create an orchestration plan that includes:
1. Detailed domain analysis with required specialists
2. Complete agent team specification with personalities and roles
3. Workflow design with clear phases
4. Execution strategy
5. Resource requirements and time estimates

Ensure the plan follows the explore → debate → synthesize pattern that has proven 
effective in complex decision-making scenarios."""

        logger.info(f"Analyzing task {task_id} in domain {task_request.domain}")
        
        result = await self.invoke_agent(prompt)
        
        # Add task_id to the result
        result.task_id = task_id
        
        return result
    
    async def create_agent_team(self, orchestration_plan: OrchestrationPlan) -> AgentTeam:
        """
        Create an agent team based on the orchestration plan.
        
        Args:
            orchestration_plan: The plan to execute
            
        Returns:
            Configured agent team
        """
        logger.info(f"Creating agent team for task {orchestration_plan.task_id}")
        
        # In a full implementation, this would instantiate actual agents
        # For now, we return the team specification
        team = orchestration_plan.agent_team
        
        # Store the active team
        self.active_teams[orchestration_plan.task_id] = team
        
        return team
    
    async def orchestrate_workflow(
        self, 
        task_id: str,
        inputs: Dict[str, Any]
    ) -> TaskResult:
        """
        Orchestrate the workflow execution for a task.
        
        Args:
            task_id: The task identifier
            inputs: Input data for the task
            
        Returns:
            Task execution result
        """
        logger.info(f"Orchestrating workflow for task {task_id}")
        
        if task_id not in self.active_teams:
            raise ValueError(f"No active team found for task {task_id}")
        
        team = self.active_teams[task_id]
        
        # Simulate workflow execution
        # In a full implementation, this would coordinate actual agent interactions
        
        result = TaskResult(
            task_id=task_id,
            domain=team.domain,
            status="completed",
            result=f"Simulated result for {team.domain} task",
            agent_reports={
                agent.name: f"Report from {agent.name}"
                for agent in team.agents
            },
            debate_summaries=[
                {
                    "debate": "main_debate",
                    "participants": [agent.name for agent in team.agents[:2]],
                    "outcome": "Consensus reached on approach"
                }
            ],
            decision_rationale="Based on comprehensive analysis and debate synthesis",
            quality_score=0.85,
            execution_time=120.5,
            metadata={"workflow_phases": len(team.workflow.phases)}
        )
        
        # Store in history
        self.task_history.append(result)
        
        # Clean up active team
        del self.active_teams[task_id]
        
        return result
    
    def get_active_teams(self) -> Dict[str, str]:
        """Get currently active teams"""
        return {
            task_id: team.domain 
            for task_id, team in self.active_teams.items()
        }
    
    def get_task_history(self, domain: Optional[str] = None) -> List[TaskResult]:
        """Get task history, optionally filtered by domain"""
        if domain:
            return [
                result for result in self.task_history 
                if result.domain == domain
            ]
        return self.task_history
    
    async def optimize_team_composition(
        self, 
        domain: str,
        performance_data: List[TaskResult]
    ) -> Dict[str, Any]:
        """
        Optimize team composition based on historical performance.
        
        Args:
            domain: The domain to optimize for
            performance_data: Historical performance data
            
        Returns:
            Optimization recommendations
        """
        prompt = f"""Analyze the performance data for the {domain} domain and provide 
recommendations for optimizing agent team composition:

Performance metrics from {len(performance_data)} previous tasks:
- Average quality score: {sum(r.quality_score for r in performance_data) / len(performance_data):.2f}
- Average execution time: {sum(r.execution_time for r in performance_data) / len(performance_data):.1f}s

Provide specific recommendations for:
1. Agent role adjustments
2. Personality trait modifications  
3. Workflow optimizations
4. Debate structure improvements
5. Tool and resource allocation

Base your recommendations on patterns in the performance data."""

        result = await self.invoke_agent(prompt)
        
        return {
            "domain": domain,
            "sample_size": len(performance_data),
            "recommendations": result
        }