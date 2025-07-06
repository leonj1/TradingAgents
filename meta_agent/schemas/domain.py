"""
Domain-related schemas for the meta-agent system.
"""

from typing import List, Dict, Any, Optional
from enum import Enum
from pydantic import BaseModel, Field


class AgentRole(str, Enum):
    """Types of agent roles"""
    EXPLORER = "explorer"
    DEBATER = "debater"
    RISK_ASSESSOR = "risk_assessor"
    DECISION_MAKER = "decision_maker"
    MODERATOR = "moderator"


class PersonalityTrait(BaseModel):
    """Individual personality trait"""
    name: str = Field(..., description="Name of the trait")
    description: str = Field(..., description="Description of the trait")
    strength: float = Field(0.5, ge=0.0, le=1.0, description="Strength of the trait (0-1)")
    domain_mapping: Dict[str, str] = Field(
        default_factory=dict,
        description="How this trait manifests in specific domains"
    )


class AgentPersonality(BaseModel):
    """Complete personality profile for an agent"""
    traits: List[PersonalityTrait] = Field(..., description="List of personality traits")
    communication_style: str = Field(..., description="How the agent communicates")
    decision_style: str = Field(..., description="How the agent makes decisions")
    domain_expertise: List[str] = Field(default_factory=list, description="Areas of expertise")


class AgentSpecification(BaseModel):
    """Specification for creating an agent"""
    name: str = Field(..., description="Agent name")
    role: AgentRole = Field(..., description="Agent's role in the system")
    personality: AgentPersonality = Field(..., description="Agent's personality")
    system_prompt: str = Field(..., description="System prompt for the agent")
    tools: List[str] = Field(default_factory=list, description="Tools available to the agent")
    capabilities: List[str] = Field(default_factory=list, description="Agent capabilities")


class DebateStructure(BaseModel):
    """Structure for organizing debates"""
    participants: List[str] = Field(..., description="Names of debate participants")
    rounds: int = Field(3, ge=1, description="Number of debate rounds")
    moderator_required: bool = Field(True, description="Whether a moderator is needed")
    synthesis_method: str = Field("consensus", description="How to synthesize debate results")
    rules: List[str] = Field(default_factory=list, description="Debate rules")


class WorkflowPhase(BaseModel):
    """Individual phase in a workflow"""
    name: str = Field(..., description="Phase name")
    agents: List[str] = Field(..., description="Agents involved in this phase")
    duration_estimate: Optional[int] = Field(None, description="Estimated duration in seconds")
    inputs: List[str] = Field(default_factory=list, description="Required inputs")
    outputs: List[str] = Field(default_factory=list, description="Expected outputs")
    validation_criteria: List[str] = Field(default_factory=list, description="Success criteria")


class DomainWorkflow(BaseModel):
    """Complete workflow for a domain"""
    domain: str = Field(..., description="Domain name")
    phases: List[WorkflowPhase] = Field(..., description="Workflow phases")
    decision_criteria: List[str] = Field(..., description="Criteria for final decisions")
    quality_metrics: Dict[str, Any] = Field(default_factory=dict, description="Quality metrics")


class DomainAnalysis(BaseModel):
    """Result of domain analysis"""
    domain: str = Field(..., description="Analyzed domain")
    description: str = Field(..., description="Domain description")
    required_specialists: List[Dict[str, str]] = Field(
        ..., description="Required specialist agents"
    )
    debate_structure: DebateStructure = Field(..., description="Recommended debate structure")
    data_sources: List[str] = Field(..., description="Relevant data sources")
    tools_needed: List[str] = Field(..., description="Required tools")
    constraints: Dict[str, Any] = Field(default_factory=dict, description="Domain constraints")
    success_metrics: List[str] = Field(..., description="How to measure success")


class AgentTeam(BaseModel):
    """Complete agent team specification"""
    domain: str = Field(..., description="Domain for this team")
    agents: List[AgentSpecification] = Field(..., description="Team members")
    workflow: DomainWorkflow = Field(..., description="Team workflow")
    debate_structures: List[DebateStructure] = Field(
        default_factory=list, description="Debate configurations"
    )
    team_dynamics: Dict[str, Any] = Field(
        default_factory=dict, description="How agents interact"
    )


class TaskRequest(BaseModel):
    """Request to create an agent team for a task"""
    domain: str = Field(..., description="Domain of the task")
    task_description: str = Field(..., description="What needs to be done")
    constraints: Dict[str, Any] = Field(default_factory=dict, description="Task constraints")
    expected_output: str = Field(..., description="What output is expected")
    priority: str = Field("medium", description="Task priority")
    deadline: Optional[str] = Field(None, description="Task deadline")


class TaskResult(BaseModel):
    """Result from agent team execution"""
    task_id: str = Field(..., description="Unique task identifier")
    domain: str = Field(..., description="Task domain")
    status: str = Field(..., description="Completion status")
    result: Any = Field(..., description="Task result")
    agent_reports: Dict[str, str] = Field(
        default_factory=dict, description="Individual agent reports"
    )
    debate_summaries: List[Dict[str, Any]] = Field(
        default_factory=list, description="Debate summaries"
    )
    decision_rationale: str = Field(..., description="Explanation of final decision")
    quality_score: float = Field(..., ge=0.0, le=1.0, description="Quality score (0-1)")
    execution_time: float = Field(..., description="Execution time in seconds")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")