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
    AgentSpecification, DomainWorkflow, AgentRole
)
from .topic_analyzer import TopicAnalyzer, TopicAnalysis
from .domain_analyzer import DomainAnalyzer
from .agent_factory import AgentFactory, AgentCreationRequest
from .debate_orchestrator import DebateOrchestrator, DebateStructure
from .workflow_adapter import WorkflowAdapter, WorkflowAdaptationRequest

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
        
        # Initialize supporting services
        self.topic_analyzer = TopicAnalyzer(api_key)
        self.domain_analyzer = DomainAnalyzer(api_key)
        self.agent_factory = AgentFactory(api_key)
        self.debate_orchestrator = DebateOrchestrator(api_key)
        self.workflow_adapter = WorkflowAdapter(api_key)
        
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
    
    async def respond_to_topic(
        self,
        topic: str,
        auto_execute: bool = True,
        show_progress: bool = True
    ) -> Dict[str, Any]:
        """
        Complete end-to-end response to a user topic.
        
        This method:
        1. Analyzes the topic to determine domain and requirements
        2. Creates a specialized agent team
        3. Executes the workflow
        4. Returns comprehensive results
        
        Args:
            topic: The user's topic or question
            auto_execute: Whether to automatically execute the workflow
            show_progress: Whether to show progress updates
            
        Returns:
            Dictionary containing analysis, team, and results
        """
        task_id = str(uuid4())
        
        if show_progress:
            logger.info(f"🔍 Analyzing topic: {topic[:100]}...")
        
        # Step 1: Analyze the topic
        topic_analysis = await self.topic_analyzer.analyze_topic(topic)
        
        if show_progress:
            logger.info(f"📊 Identified domain: {topic_analysis.domain} "
                       f"(confidence: {topic_analysis.domain_confidence:.2f})")
            logger.info(f"🎯 Task type: {topic_analysis.task_type}")
        
        # Step 2: Convert to task request
        task_request = await self.topic_analyzer.extract_requirements(
            topic, topic_analysis
        )
        
        # Step 3: Analyze domain in detail
        domain_analysis = await self.domain_analyzer.analyze_domain(
            domain=topic_analysis.domain,
            task_context=topic,
            constraints=topic_analysis.constraints
        )
        
        if show_progress:
            logger.info(f"👥 Creating team with {len(domain_analysis.required_specialists)} specialists...")
        
        # Step 4: Create agent team dynamically
        agents = []
        
        # Create specialist agents
        for i, specialist in enumerate(domain_analysis.required_specialists[:6]):
            if show_progress:
                logger.info(f"   🤖 Creating {specialist.get('name', f'Specialist {i+1}')}...")
            
            agent_request = AgentCreationRequest(
                name=specialist.get('name', f'{topic_analysis.domain.title()} Specialist {i+1}'),
                role=AgentRole.EXPLORER,
                domain=topic_analysis.domain,
                specialization=specialist.get('expertise', 'general analysis'),
                personality_keywords=self._get_personality_keywords(i),
                capabilities_needed=topic_analysis.specialist_needs
            )
            
            agent_spec = await self.agent_factory.create_agent(agent_request)
            agents.append(agent_spec)
        
        # Create debaters based on debate topics
        if topic_analysis.debate_topics:
            debate_positions = self.topic_analyzer._extract_debaters(topic_analysis.debate_topics)
            for i, position in enumerate(debate_positions[:2]):
                if show_progress:
                    logger.info(f"   💬 Creating debater: {position}")
                
                debater_request = AgentCreationRequest(
                    name=f"{position} Advocate",
                    role=AgentRole.DEBATER,
                    domain=topic_analysis.domain,
                    specialization=f"advocating for {position.lower()} perspective",
                    personality_keywords=["persuasive", "analytical", "evidence-based"],
                    capabilities_needed=["debate", "argumentation", "synthesis"]
                )
                
                agent_spec = await self.agent_factory.create_agent(debater_request)
                agents.append(agent_spec)
        
        # Step 5: Create workflow
        workflow_request = WorkflowAdaptationRequest(
            domain=topic_analysis.domain,
            base_workflow="explore_debate_synthesize",
            domain_requirements=topic_analysis.requirements,
            constraints=topic_analysis.constraints
        )
        
        adapted_workflow = await self.workflow_adapter.adapt_workflow(workflow_request)
        
        # Step 6: Assemble team
        team = AgentTeam(
            domain=topic_analysis.domain,
            agents=agents,
            workflow=adapted_workflow.workflow,
            debate_structures=[domain_analysis.debate_structure]
        )
        
        self.active_teams[task_id] = team
        
        if show_progress:
            logger.info(f"✅ Team created with {len(agents)} agents")
        
        # Step 7: Execute workflow if requested
        result = None
        if auto_execute:
            if show_progress:
                logger.info("🚀 Executing workflow...")
            
            result = await self.orchestrate_workflow(
                task_id=task_id,
                inputs={
                    "topic": topic,
                    "requirements": topic_analysis.requirements,
                    "constraints": topic_analysis.constraints
                }
            )
            
            if show_progress:
                logger.info(f"✨ Workflow completed with quality score: {result.quality_score:.2f}")
        
        return {
            "task_id": task_id,
            "topic": topic,
            "analysis": topic_analysis,
            "domain_analysis": domain_analysis,
            "team": team,
            "result": result,
            "status": "completed" if result else "team_created"
        }
    
    def _get_personality_keywords(self, index: int) -> List[str]:
        """Get personality keywords for agent variety"""
        personality_sets = [
            ["analytical", "thorough", "detail-oriented"],
            ["creative", "innovative", "visionary"],
            ["practical", "efficient", "results-focused"],
            ["collaborative", "inclusive", "communicative"],
            ["critical", "questioning", "evidence-based"],
            ["optimistic", "enthusiastic", "proactive"]
        ]
        return personality_sets[index % len(personality_sets)]