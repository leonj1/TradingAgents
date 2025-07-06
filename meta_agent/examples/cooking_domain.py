"""
Example: Creating a cooking domain agent team using the meta-agent system.
"""

import asyncio
import os
from dotenv import load_dotenv

from meta_agent import (
    MetaAgentOrchestrator,
    DomainAnalyzer,
    AgentFactory,
    DebateOrchestrator,
    PersonalityGenerator,
    ToolSelector,
    QualityValidator,
    WorkflowAdapter
)
from meta_agent.schemas.domain import TaskRequest, AgentRole

# Load environment variables
load_dotenv()


async def create_cooking_team():
    """Example of creating a cooking domain agent team"""
    
    # Initialize services with API key
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise ValueError("Please set OPENAI_API_KEY environment variable")
    
    # Initialize core services
    print("Initializing meta-agent services...")
    orchestrator = MetaAgentOrchestrator(api_key)
    domain_analyzer = DomainAnalyzer(api_key)
    agent_factory = AgentFactory(api_key)
    
    # Create a task request
    task_request = TaskRequest(
        domain="cooking",
        task_description="Create a healthy, delicious dinner menu for a vegan guest with nut allergies",
        constraints={
            "budget": "$50",
            "preparation_time": "2 hours",
            "dietary_restrictions": ["vegan", "nut-free"],
            "servings": 4
        },
        expected_output="Complete dinner menu with recipes, shopping list, and preparation timeline",
        priority="high"
    )
    
    print(f"\n📋 Task: {task_request.task_description}")
    print(f"   Domain: {task_request.domain}")
    print(f"   Constraints: {task_request.constraints}")
    
    # Step 1: Analyze the task and create orchestration plan
    print("\n🔍 Analyzing task and creating orchestration plan...")
    orchestration_plan = await orchestrator.analyze_task(task_request)
    
    print(f"   ✓ Task ID: {orchestration_plan.task_id}")
    print(f"   ✓ Estimated duration: {orchestration_plan.estimated_duration}s")
    print(f"   ✓ Execution strategy: {orchestration_plan.execution_strategy}")
    
    # Step 2: Analyze the domain
    print("\n🌐 Analyzing cooking domain...")
    domain_analysis = await domain_analyzer.analyze_domain(
        domain="cooking",
        task_context=task_request.task_description,
        constraints=task_request.constraints
    )
    
    print(f"   ✓ Required specialists: {len(domain_analysis.required_specialists)}")
    for spec in domain_analysis.required_specialists[:3]:
        print(f"      - {spec.get('name', 'Specialist')}")
    print(f"   ✓ Data sources: {', '.join(domain_analysis.data_sources[:3])}")
    print(f"   ✓ Success metrics: {len(domain_analysis.success_metrics)}")
    
    # Step 3: Create agent team
    print("\n👥 Creating agent team...")
    agent_team = await orchestrator.create_agent_team(orchestration_plan)
    
    print(f"   ✓ Team size: {len(agent_team.agents)} agents")
    print(f"   ✓ Workflow phases: {len(agent_team.workflow.phases)}")
    
    # Step 4: Create specific agents
    print("\n🤖 Creating individual agents...")
    
    # Example: Create an Ingredients Analyst
    from meta_agent.services.agent_factory import AgentCreationRequest
    
    ingredients_request = AgentCreationRequest(
        name="Chef Marina",
        role=AgentRole.EXPLORER,
        domain="cooking",
        specialization="ingredients and nutrition",
        personality_keywords=["analytical", "creative", "health-conscious"],
        capabilities_needed=[
            "ingredient analysis",
            "nutritional assessment",
            "allergen detection",
            "flavor pairing"
        ]
    )
    
    ingredients_analyst = await agent_factory.create_agent(ingredients_request)
    print(f"   ✓ Created: {ingredients_analyst.name}")
    print(f"     Role: {ingredients_analyst.role.value}")
    print(f"     Personality: {', '.join([t.name for t in ingredients_analyst.personality.traits[:3]])}")
    
    # Step 5: Simulate workflow execution
    print("\n🚀 Simulating workflow execution...")
    
    # In a real implementation, this would coordinate actual agent interactions
    task_result = await orchestrator.orchestrate_workflow(
        task_id=orchestration_plan.task_id,
        inputs={
            "requirements": task_request.constraints,
            "preferences": "healthy and delicious"
        }
    )
    
    print(f"   ✓ Status: {task_result.status}")
    print(f"   ✓ Quality score: {task_result.quality_score:.2f}")
    print(f"   ✓ Execution time: {task_result.execution_time:.1f}s")
    print(f"   ✓ Decision: {task_result.decision_rationale}")
    
    return {
        "task_id": orchestration_plan.task_id,
        "team": agent_team,
        "result": task_result
    }


async def demonstrate_debate():
    """Demonstrate debate orchestration"""
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise ValueError("Please set OPENAI_API_KEY environment variable")
    
    debate_orchestrator = DebateOrchestrator(api_key)
    
    print("\n💬 Demonstrating debate orchestration...")
    
    # Create a debate structure
    from meta_agent.schemas.domain import DebateStructure
    
    debate_structure = DebateStructure(
        participants=["Traditional Chef", "Modern Innovation Chef"],
        rounds=2,
        moderator_required=True,
        synthesis_method="balanced_synthesis",
        rules=[
            "Focus on evidence and experience",
            "Respect different culinary philosophies",
            "Work towards practical solutions"
        ]
    )
    
    # Initial positions
    initial_positions = {
        "Traditional Chef": "Classic techniques and time-tested recipes ensure quality",
        "Modern Innovation Chef": "New techniques and ingredients expand possibilities"
    }
    
    # Conduct debate
    debate_rounds = await debate_orchestrator.moderate_debate(
        topic="Best approach for the vegan dinner menu",
        structure=debate_structure,
        initial_positions=initial_positions
    )
    
    print(f"   ✓ Conducted {len(debate_rounds)} debate rounds")
    
    # Synthesize results
    synthesis = await debate_orchestrator.synthesize_debate(
        topic="Best approach for the vegan dinner menu",
        rounds=debate_rounds,
        structure=debate_structure
    )
    
    print(f"   ✓ Consensus points: {len(synthesis.consensus_points)}")
    print(f"   ✓ Recommendation: {synthesis.recommended_action}")
    print(f"   ✓ Confidence: {synthesis.confidence_level:.2f}")
    
    return synthesis


async def main():
    """Run the cooking domain example"""
    print("🍳 Meta-Agent System: Cooking Domain Example")
    print("=" * 50)
    
    try:
        # Create cooking team
        result = await create_cooking_team()
        
        # Demonstrate debate
        debate_result = await demonstrate_debate()
        
        print("\n✅ Example completed successfully!")
        print(f"\nTask ID: {result['task_id']}")
        print(f"Team created with {len(result['team'].agents)} agents")
        print(f"Final quality score: {result['result'].quality_score:.2f}")
        
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        raise


if __name__ == "__main__":
    asyncio.run(main())