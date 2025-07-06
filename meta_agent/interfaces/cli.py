"""
CLI interface for dynamic topic submission and agent team creation.
"""

import asyncio
import os
import sys
from typing import Optional, Dict, Any
from datetime import datetime

import typer
from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.markdown import Markdown
from rich.table import Table
from rich.tree import Tree
from rich.prompt import Prompt, Confirm
from rich.live import Live
from rich.layout import Layout
from rich.text import Text
import questionary
from dotenv import load_dotenv

from meta_agent import MetaAgentOrchestrator

# Load environment variables
load_dotenv()

# Initialize Rich console
console = Console()
app = typer.Typer(
    name="meta-agent",
    help="Dynamic AI agent team creation for any topic",
    add_completion=True
)


class TopicResponder:
    """Handles topic analysis and agent team creation"""
    
    def __init__(self, api_key: str):
        self.orchestrator = MetaAgentOrchestrator(api_key)
        self.console = console
        
    async def respond_to_topic(self, topic: str, auto_execute: bool = True):
        """Process a topic and display results"""
        
        # Create layout for live display
        layout = Layout()
        layout.split_column(
            Layout(name="header", size=3),
            Layout(name="progress", size=5),
            Layout(name="agents", size=10),
            Layout(name="status", size=3)
        )
        
        # Header
        layout["header"].update(
            Panel(
                f"[bold blue]Topic:[/bold blue] {topic[:100]}{'...' if len(topic) > 100 else ''}",
                title="🤖 Meta-Agent System",
                border_style="blue"
            )
        )
        
        # Progress tracking
        progress_text = Text()
        layout["progress"].update(Panel(progress_text, title="Progress", border_style="green"))
        
        # Agents display
        agents_tree = Tree("Agent Team")
        layout["agents"].update(Panel(agents_tree, title="Created Agents", border_style="yellow"))
        
        # Status
        status_text = Text("Starting analysis...", style="italic")
        layout["status"].update(Panel(status_text, border_style="cyan"))
        
        with Live(layout, refresh_per_second=2, console=self.console):
            try:
                # Update progress
                progress_text.append("🔍 Analyzing topic...\n", style="yellow")
                
                # Call the orchestrator
                result = await self.orchestrator.respond_to_topic(
                    topic=topic,
                    auto_execute=auto_execute,
                    show_progress=False  # We handle our own progress display
                )
                
                # Update progress with domain info
                analysis = result["analysis"]
                progress_text.append(
                    f"📊 Domain: [bold]{analysis.domain}[/bold] "
                    f"(confidence: {analysis.domain_confidence:.0%})\n",
                    style="green"
                )
                progress_text.append(
                    f"🎯 Task type: {analysis.task_type}\n",
                    style="green"
                )
                progress_text.append(
                    f"📈 Complexity: {analysis.complexity_level}\n",
                    style="green"
                )
                
                # Update agents tree
                team = result["team"]
                
                # Group agents by role
                explorers = agents_tree.add("🔍 Explorers")
                debaters = agents_tree.add("💬 Debaters")
                
                for agent in team.agents:
                    if agent.role.value == "explorer":
                        node = explorers.add(f"[cyan]{agent.name}[/cyan]")
                        node.add(f"Focus: {agent.personality.domain_expertise[0] if agent.personality.domain_expertise else 'General'}")
                        traits = ", ".join([t.name for t in agent.personality.traits[:3]])
                        node.add(f"Traits: {traits}")
                    elif agent.role.value == "debater":
                        node = debaters.add(f"[magenta]{agent.name}[/magenta]")
                        node.add(f"Stance: {agent.personality.communication_style}")
                
                # Update status
                if result["status"] == "completed" and result["result"]:
                    status_text.plain = f"✅ Analysis complete! Quality: {result['result'].quality_score:.0%}"
                    status_text.style = "bold green"
                else:
                    status_text.plain = "✅ Team created successfully!"
                    status_text.style = "bold green"
                
                # Brief pause to show final state
                await asyncio.sleep(2)
                
            except Exception as e:
                # Update status with error
                status_text.plain = f"❌ Error: {str(e)}"
                status_text.style = "bold red"
                
                # Log the error
                import traceback
                error_details = traceback.format_exc()
                progress_text.append(f"\n[red]Error details:[/red]\n{error_details}", style="red")
                
                # Re-raise to ensure proper error handling upstream
                raise
                
        return result
    
    def display_results(self, result: Dict[str, Any]):
        """Display the final results"""
        
        console.print("\n")
        
        # Analysis Summary
        analysis = result["analysis"]
        summary_table = Table(title="📊 Topic Analysis Summary", show_header=False)
        summary_table.add_column("Property", style="cyan", width=20)
        summary_table.add_column("Value", style="white")
        
        summary_table.add_row("Domain", f"[bold]{analysis.domain}[/bold]")
        summary_table.add_row("Confidence", f"{analysis.domain_confidence:.0%}")
        summary_table.add_row("Task Type", analysis.task_type)
        summary_table.add_row("Complexity", analysis.complexity_level)
        summary_table.add_row("Expected Output", analysis.expected_output_type)
        
        console.print(summary_table)
        console.print()
        
        # Key Concepts
        console.print(Panel(
            "\n".join([f"• {concept}" for concept in analysis.key_concepts]),
            title="🔑 Key Concepts",
            border_style="blue"
        ))
        console.print()
        
        # Team Composition
        team = result["team"]
        team_table = Table(title=f"👥 Agent Team ({len(team.agents)} agents)")
        team_table.add_column("Agent", style="cyan")
        team_table.add_column("Role", style="magenta")
        team_table.add_column("Specialization", style="green")
        team_table.add_column("Key Traits", style="yellow")
        
        for agent in team.agents:
            traits = ", ".join([t.name for t in agent.personality.traits[:2]])
            specialization = agent.personality.domain_expertise[0] if agent.personality.domain_expertise else "General"
            team_table.add_row(
                agent.name,
                agent.role.value.title(),
                specialization,
                traits
            )
        
        console.print(team_table)
        console.print()
        
        # Decision/Result
        if result["result"]:
            console.print(Panel(
                f"[bold]Decision:[/bold] {result['result'].decision_rationale}\n\n"
                f"[bold]Quality Score:[/bold] {result['result'].quality_score:.0%}\n"
                f"[bold]Execution Time:[/bold] {result['result'].execution_time:.1f}s",
                title="📋 Final Result",
                border_style="green"
            ))


@app.command()
def analyze(
    topic: Optional[str] = typer.Argument(
        None,
        help="The topic or question to analyze"
    ),
    execute: bool = typer.Option(
        True,
        "--execute/--no-execute",
        help="Execute the workflow after creating the team"
    ),
    api_key: Optional[str] = typer.Option(
        None,
        "--api-key",
        envvar="OPENAI_API_KEY",
        help="OpenAI API key (can also use OPENAI_API_KEY env var)"
    )
):
    """
    Analyze a topic and create a specialized agent team to respond to it.
    
    Examples:
        meta-agent analyze "How can I reduce my carbon footprint?"
        meta-agent analyze "Create a healthy meal plan for weight loss"
        meta-agent analyze "Explain quantum computing to a beginner"
    """
    
    # Check API key
    if not api_key:
        console.print("[red]Error: OpenAI API key not found![/red]")
        console.print("Set it with: export OPENAI_API_KEY=your-key")
        raise typer.Exit(1)
    
    # Get topic interactively if not provided
    if not topic:
        console.print(Panel(
            "[bold]Welcome to Meta-Agent System![/bold]\n\n"
            "I can create specialized AI agent teams to help with any topic.\n"
            "Just tell me what you'd like to explore!",
            title="🤖 Dynamic Agent Team Creator",
            border_style="blue"
        ))
        
        topic = Prompt.ask("\n[bold cyan]What topic would you like help with?[/bold cyan]")
        
        if not topic.strip():
            console.print("[red]No topic provided. Exiting.[/red]")
            raise typer.Exit(1)
    
    # Create responder
    responder = TopicResponder(api_key)
    
    # Process topic
    console.print(f"\n[bold]Processing:[/bold] {topic}\n")
    
    try:
        # Run async function
        result = asyncio.run(responder.respond_to_topic(topic, auto_execute=execute))
        
        # Display results
        responder.display_results(result)
        
        # Save option - check if running in TTY
        import sys
        should_save = False
        if sys.stdin.isatty():
            should_save = Confirm.ask("\n💾 Would you like to save the results?")
        else:
            # Auto-save in non-interactive mode
            should_save = True
            console.print("\n💾 Auto-saving results (non-interactive mode)...")
        
        if should_save:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            # Save to results directory
            import os
            results_dir = "/app/results"
            os.makedirs(results_dir, exist_ok=True)
            filename = os.path.join(results_dir, f"meta_agent_results_{timestamp}.json")
            
            import json
            with open(filename, 'w') as f:
                # Convert objects to dict for JSON serialization
                json_result = {
                    "topic": result["topic"],
                    "task_id": result["task_id"],
                    "status": result["status"],
                    "analysis": {
                        "domain": result["analysis"].domain,
                        "confidence": result["analysis"].domain_confidence,
                        "task_type": result["analysis"].task_type,
                        "complexity": result["analysis"].complexity_level,
                        "key_concepts": result["analysis"].key_concepts,
                    },
                    "team_size": len(result["team"].agents),
                    "agent_names": [a.name for a in result["team"].agents]
                }
                if result["result"]:
                    json_result["result"] = {
                        "quality_score": result["result"].quality_score,
                        "execution_time": result["result"].execution_time,
                        "decision": result["result"].decision_rationale
                    }
                
                json.dump(json_result, f, indent=2)
            
            console.print(f"\n✅ Results saved to: [green]{filename}[/green]")
            
    except Exception as e:
        console.print(f"\n[red]Error: {str(e)}[/red]")
        raise typer.Exit(1)


@app.command()
def interactive():
    """
    Interactive mode for exploring multiple topics.
    """
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        console.print("[red]Error: OpenAI API key not found![/red]")
        raise typer.Exit(1)
    
    responder = TopicResponder(api_key)
    
    console.print(Panel(
        "[bold]Meta-Agent Interactive Mode[/bold]\n\n"
        "Create specialized AI teams for any topic!\n"
        "Type 'exit' or 'quit' to leave.",
        title="🤖 Welcome",
        border_style="blue"
    ))
    
    while True:
        topic = questionary.text(
            "What topic would you like to explore?",
            qmark="🎯",
            instruction="(or 'exit' to quit)"
        ).ask()
        
        if not topic or topic.lower() in ['exit', 'quit']:
            console.print("\n[yellow]Goodbye! 👋[/yellow]")
            break
        
        # Ask about execution
        execute = questionary.confirm(
            "Execute the workflow after creating the team?",
            default=True,
            qmark="🚀"
        ).ask()
        
        try:
            result = asyncio.run(responder.respond_to_topic(topic, auto_execute=execute))
            responder.display_results(result)
            
            console.print("\n" + "="*60 + "\n")
            
        except Exception as e:
            console.print(f"\n[red]Error: {str(e)}[/red]\n")


@app.command()
def domains():
    """
    List supported domains and example topics.
    """
    domains_info = {
        "cooking": ["Recipe creation", "Meal planning", "Dietary advice"],
        "healthcare": ["Symptom analysis", "Wellness tips", "Treatment options"],
        "technology": ["Programming help", "System design", "Tech explanations"],
        "finance": ["Investment advice", "Budget planning", "Market analysis"],
        "education": ["Learning strategies", "Course design", "Study planning"],
        "environment": ["Sustainability tips", "Carbon reduction", "Eco-friendly choices"],
        "business": ["Strategy planning", "Marketing ideas", "Startup advice"],
        "creative": ["Design concepts", "Writing help", "Artistic guidance"],
        "science": ["Research methods", "Experiment design", "Theory explanation"]
    }
    
    table = Table(title="🌐 Supported Domains", show_lines=True)
    table.add_column("Domain", style="cyan", width=15)
    table.add_column("Example Topics", style="green", width=65)
    
    for domain, examples in domains_info.items():
        table.add_row(
            domain.title(),
            " • " + "\n • ".join(examples)
        )
    
    console.print(table)
    console.print("\n[italic]Note: The system can handle any domain - these are just examples![/italic]")


if __name__ == "__main__":
    app()