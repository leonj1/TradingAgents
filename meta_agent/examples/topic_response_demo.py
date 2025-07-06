"""
Demonstration of the dynamic topic response system.
Shows how users can submit any topic and get specialized agent teams.
"""

import asyncio
import os
from dotenv import load_dotenv
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from meta_agent import MetaAgentOrchestrator

# Load environment variables
load_dotenv()
console = Console()


async def demo_topics():
    """Demonstrate the system with various topics"""
    
    # Check API key
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        console.print("[red]Please set OPENAI_API_KEY environment variable[/red]")
        return
    
    # Initialize orchestrator
    orchestrator = MetaAgentOrchestrator(api_key)
    
    # Example topics from different domains
    demo_topics = [
        {
            "topic": "How can I reduce my carbon footprint while living in a city apartment?",
            "expected_domain": "environment"
        },
        {
            "topic": "Create a 7-day meal plan for someone with diabetes who wants to lose weight",
            "expected_domain": "cooking/healthcare"
        },
        {
            "topic": "Explain quantum computing in simple terms for a high school student",
            "expected_domain": "education/technology"
        },
        {
            "topic": "What's the best strategy for starting a sustainable fashion brand?",
            "expected_domain": "business"
        },
        {
            "topic": "How do I write a compelling science fiction short story?",
            "expected_domain": "creative"
        }
    ]
    
    console.print(Panel(
        "[bold]Meta-Agent Topic Response Demo[/bold]\n\n"
        "This demo shows how the system analyzes different topics and creates "
        "specialized agent teams dynamically.",
        title="🎯 Demo Overview",
        border_style="blue"
    ))
    
    for i, demo in enumerate(demo_topics, 1):
        console.print(f"\n[bold cyan]Demo {i}:[/bold cyan] {demo['topic']}")
        console.print(f"[dim]Expected domain: {demo['expected_domain']}[/dim]\n")
        
        try:
            # Analyze topic (without executing workflow for speed)
            result = await orchestrator.respond_to_topic(
                topic=demo['topic'],
                auto_execute=False,
                show_progress=True
            )
            
            # Display results
            display_demo_results(result)
            
            if i < len(demo_topics):
                console.print("\n" + "="*80 + "\n")
                
        except Exception as e:
            console.print(f"[red]Error: {str(e)}[/red]")


def display_demo_results(result):
    """Display demo results in a formatted way"""
    
    analysis = result["analysis"]
    team = result["team"]
    
    # Domain and confidence
    console.print(
        f"✅ [green]Detected Domain:[/green] [bold]{analysis.domain}[/bold] "
        f"(confidence: {analysis.domain_confidence:.0%})"
    )
    
    # Task type and complexity
    console.print(f"📋 Task Type: {analysis.task_type}")
    console.print(f"📊 Complexity: {analysis.complexity_level}")
    
    # Key concepts
    console.print(f"\n🔑 Key Concepts: {', '.join(analysis.key_concepts[:3])}")
    
    # Created agents
    console.print(f"\n👥 Created {len(team.agents)} specialized agents:")
    
    # Group by role
    explorers = [a for a in team.agents if a.role.value == "explorer"]
    debaters = [a for a in team.agents if a.role.value == "debater"]
    
    if explorers:
        console.print("   [cyan]Explorers:[/cyan]")
        for agent in explorers[:4]:  # Show max 4
            traits = ", ".join([t.name for t in agent.personality.traits[:2]])
            console.print(f"   • {agent.name} ({traits})")
    
    if debaters:
        console.print("   [magenta]Debaters:[/magenta]")
        for agent in debaters:
            console.print(f"   • {agent.name}")
    
    # Debate topics
    if analysis.debate_topics:
        console.print(f"\n💬 Debate Topics: {', '.join(analysis.debate_topics[:2])}")


async def interactive_demo():
    """Interactive demo where users can try their own topics"""
    
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        console.print("[red]Please set OPENAI_API_KEY environment variable[/red]")
        return
    
    orchestrator = MetaAgentOrchestrator(api_key)
    
    console.print(Panel(
        "[bold]Interactive Topic Demo[/bold]\n\n"
        "Enter any topic and see what specialized agent team gets created!\n"
        "Type 'exit' to quit.",
        title="🤖 Try It Yourself",
        border_style="green"
    ))
    
    while True:
        topic = console.input("\n[bold cyan]Enter your topic:[/bold cyan] ")
        
        if topic.lower() in ['exit', 'quit']:
            break
        
        try:
            console.print("\n🔍 Analyzing your topic...\n")
            
            result = await orchestrator.respond_to_topic(
                topic=topic,
                auto_execute=False,
                show_progress=True
            )
            
            display_demo_results(result)
            
            # Ask if they want to see the full execution
            execute = console.input(
                "\n[yellow]Would you like to execute the full workflow? (y/n):[/yellow] "
            )
            
            if execute.lower() == 'y':
                console.print("\n🚀 Executing workflow...\n")
                
                # Execute the workflow
                exec_result = await orchestrator.orchestrate_workflow(
                    task_id=result["task_id"],
                    inputs={
                        "topic": topic,
                        "requirements": result["analysis"].requirements
                    }
                )
                
                console.print(Panel(
                    f"[bold]Final Decision:[/bold]\n{exec_result.decision_rationale}\n\n"
                    f"[bold]Quality Score:[/bold] {exec_result.quality_score:.0%}",
                    title="📋 Result",
                    border_style="green"
                ))
                
        except Exception as e:
            console.print(f"[red]Error: {str(e)}[/red]")


async def main():
    """Run the demos"""
    
    console.print("[bold]Meta-Agent Topic Response Demo[/bold]\n")
    
    # Show example topics
    await demo_topics()
    
    console.print("\n" + "="*80 + "\n")
    
    # Interactive demo
    try_interactive = console.input(
        "\n[yellow]Would you like to try your own topics? (y/n):[/yellow] "
    )
    
    if try_interactive.lower() == 'y':
        await interactive_demo()
    
    console.print("\n[green]Demo completed![/green]")


if __name__ == "__main__":
    asyncio.run(main())