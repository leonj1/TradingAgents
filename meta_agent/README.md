# Meta-Agent System

A dynamic multi-agent system that can analyze any domain and automatically create specialized agent teams following the proven explore → debate → synthesize pattern from TradingAgents.

## 🌟 Overview

The Meta-Agent System is a sophisticated framework that can:
- Analyze any domain (cooking, healthcare, technical writing, etc.)
- Dynamically create specialized agent teams with distinct personalities
- Orchestrate multi-agent debates and decision-making
- Adapt workflows to domain-specific needs
- Ensure quality through validation and continuous improvement

## 🏗️ Architecture

The system consists of 8 core AI services, all using Pydantic AI with OpenAI's o3 model:

### Core Services

1. **MetaAgentOrchestrator** - Main orchestrator that creates and manages domain-specific agent teams
2. **DomainAnalyzer** - Analyzes domains to determine optimal agent compositions and workflows
3. **AgentFactory** - Creates individual agents with specific personalities and capabilities
4. **DebateOrchestrator** - Manages and moderates debates between agents
5. **PersonalityGenerator** - Creates coherent, domain-appropriate agent personalities
6. **ToolSelector** - Selects and configures appropriate tools for domain agents
7. **QualityValidator** - Validates generated agents and their outputs
8. **WorkflowAdapter** - Adapts generic workflows to specific domains

## 🚀 Quick Start

### Installation

```bash
# Install dependencies
pip install -r meta_agent/requirements.txt

# Set up environment variables
export OPENAI_API_KEY="your-api-key-here"
```

### Basic Usage

```python
import asyncio
from meta_agent import MetaAgentOrchestrator, TaskRequest

async def main():
    # Initialize orchestrator
    orchestrator = MetaAgentOrchestrator(api_key="your-api-key")
    
    # Create a task request
    task = TaskRequest(
        domain="cooking",
        task_description="Create a healthy dinner menu",
        constraints={"budget": "$50", "time": "2 hours"},
        expected_output="Complete menu with recipes"
    )
    
    # Analyze and create agent team
    plan = await orchestrator.analyze_task(task)
    team = await orchestrator.create_agent_team(plan)
    
    # Execute workflow
    result = await orchestrator.orchestrate_workflow(
        task_id=plan.task_id,
        inputs={"preferences": "healthy"}
    )
    
    print(f"Result: {result.decision_rationale}")

asyncio.run(main())
```

## 📋 Examples

### Cooking Domain Team

```python
from meta_agent.examples.cooking_domain import create_cooking_team

# Creates a team with:
# - Ingredients Analyst
# - Technique Specialist  
# - Flavor Profile Expert
# - Nutrition Analyst
# - Traditional vs Modern Chef debaters
# - Risk assessors for time, cost, and quality

result = await create_cooking_team()
```

### Healthcare Domain Team

```python
# Creates a team with:
# - Symptoms Analyst
# - Medical History Expert
# - Research Specialist
# - Lifestyle Analyst
# - Conservative vs Proactive treatment debaters
# - Safety and efficacy assessors
```

## 🔧 Creating Custom Domains

### 1. Define Your Domain

```python
from meta_agent import DomainAnalyzer

analyzer = DomainAnalyzer(api_key)
analysis = await analyzer.analyze_domain(
    domain="your-domain",
    task_context="What you want to accomplish",
    constraints={"time": "1 hour", "resources": "limited"}
)
```

### 2. Create Specialized Agents

```python
from meta_agent import AgentFactory
from meta_agent.schemas.domain import AgentRole

factory = AgentFactory(api_key)
agent = await factory.create_agent({
    "name": "Domain Expert",
    "role": AgentRole.EXPLORER,
    "domain": "your-domain",
    "specialization": "specific area",
    "personality_keywords": ["analytical", "creative"],
    "capabilities_needed": ["analyze", "synthesize"]
})
```

### 3. Configure Debates

```python
from meta_agent import DebateOrchestrator

debate_orchestrator = DebateOrchestrator(api_key)
synthesis = await debate_orchestrator.synthesize_debate(
    topic="Best approach for task",
    rounds=debate_rounds,
    structure=debate_structure
)
```

## 📊 Workflow Pattern

All domains follow the proven pattern:

```
1. Explore (Specialists gather information)
   ↓
2. Debate (Different perspectives discuss)
   ↓
3. Synthesize (Combine insights)
   ↓
4. Decide (Make recommendations)
```

## 🧪 Testing

```bash
# Run tests
python -m pytest meta_agent/tests/

# Run specific test
python -m pytest meta_agent/tests/test_services.py::TestDomainAnalyzer
```

## 📁 Project Structure

```
meta_agent/
├── services/           # Core AI services
│   ├── base.py        # Base service class
│   ├── meta_orchestrator.py
│   ├── domain_analyzer.py
│   └── ...
├── schemas/           # Pydantic models
│   └── domain.py
├── utils/            # Utilities
│   └── prompts.py
├── examples/         # Usage examples
│   └── cooking_domain.py
└── tests/           # Test suite
```

## 🔑 Key Features

- **Domain Agnostic**: Works with any domain from cooking to quantum physics
- **Dynamic Agent Creation**: Generates agents with appropriate personalities and skills
- **Structured Debates**: Facilitates productive disagreement and synthesis
- **Quality Assurance**: Built-in validation and improvement mechanisms
- **Scalable Architecture**: Easy to extend with new domains and capabilities

## 🛠️ Advanced Usage

### Custom Personality Traits

```python
from meta_agent import PersonalityGenerator

generator = PersonalityGenerator(api_key)
personality = await generator.generate_personality({
    "role": "analyst",
    "domain": "finance",
    "required_traits": ["detail-oriented", "risk-aware"],
    "avoid_traits": ["impulsive"],
    "team_context": ["optimistic trader", "cautious advisor"]
})
```

### Workflow Optimization

```python
from meta_agent import WorkflowAdapter

adapter = WorkflowAdapter(api_key)
optimized = await adapter.optimize_workflow(
    workflow=current_workflow,
    performance_data={"avg_time": 120, "quality": 0.85}
)
```

## 🤝 Contributing

Contributions are welcome! Please:
1. Fork the repository
2. Create a feature branch
3. Add tests for new functionality
4. Submit a pull request

## 📄 License

This project is licensed under the same license as TradingAgents.

## 🔗 Related

- [TradingAgents](https://github.com/TauricResearch/TradingAgents) - The original trading agents implementation
- [Pydantic AI](https://github.com/pydantic/pydantic-ai) - The AI framework used

## 📞 Support

For questions or issues:
- Open an issue on GitHub
- Check the examples directory
- Review the test cases for usage patterns