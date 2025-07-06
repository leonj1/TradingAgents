# Topic Response System Guide

The Meta-Agent System can now dynamically respond to any user topic by automatically creating specialized agent teams. This guide explains how to use this powerful feature.

## 🌟 Overview

The Topic Response System allows users to:
1. Submit any topic or question in natural language
2. Automatically detect the domain and requirements
3. Create a specialized team of AI agents
4. Execute multi-agent workflows to provide comprehensive responses

## 🚀 Quick Start

### Using the CLI

```bash
# Analyze a single topic
python -m meta_agent.interfaces.cli analyze "How can I reduce my carbon footprint?"

# Interactive mode
python -m meta_agent.interfaces.cli interactive

# List supported domains
python -m meta_agent.interfaces.cli domains
```

### Using the API

```bash
# Start the API server
python -m meta_agent.interfaces.api

# Submit a topic
curl -X POST http://localhost:8000/analyze \
  -H "Content-Type: application/json" \
  -d '{"topic": "Create a healthy meal plan for weight loss"}'

# Check status
curl http://localhost:8000/status/{task_id}
```

### Using Python

```python
from meta_agent import MetaAgentOrchestrator

orchestrator = MetaAgentOrchestrator(api_key="your-key")

# Analyze any topic
result = await orchestrator.respond_to_topic(
    "Explain quantum computing to a beginner",
    auto_execute=True
)

print(f"Domain: {result['analysis'].domain}")
print(f"Team size: {len(result['team'].agents)}")
print(f"Decision: {result['result'].decision_rationale}")
```

## 📋 How It Works

### 1. Topic Analysis
When you submit a topic, the system:
- Identifies the primary domain (cooking, healthcare, technology, etc.)
- Extracts key concepts and requirements
- Determines task complexity
- Identifies potential debate topics

### 2. Dynamic Agent Creation
Based on the analysis, the system creates:
- **Specialist Agents**: 4-6 domain experts with unique perspectives
- **Debater Agents**: 2 agents representing opposing viewpoints
- **Personality Diversity**: Each agent has distinct traits

### 3. Workflow Execution
The agents follow the pattern:
1. **Explore**: Specialists analyze different aspects
2. **Debate**: Opposing views are discussed
3. **Synthesize**: Insights are combined
4. **Decide**: Final recommendations are made

## 🎯 Example Topics

### Environment
```
"How can I make my home more eco-friendly?"
→ Creates: Environmental Analyst, Energy Expert, Cost Analyst, Lifestyle Coach
```

### Healthcare
```
"What are natural ways to improve sleep quality?"
→ Creates: Sleep Specialist, Nutrition Expert, Exercise Analyst, Stress Management Coach
```

### Technology
```
"Should I learn Python or JavaScript first?"
→ Creates: Language Expert, Career Advisor, Learning Specialist, Project Analyst
```

### Business
```
"How do I validate a startup idea?"
→ Creates: Market Researcher, Customer Expert, Financial Analyst, Risk Assessor
```

## 🔧 Advanced Features

### Custom Domain Hints
```python
# Suggest a specific domain
result = await orchestrator.topic_analyzer.refine_for_domain(
    topic="Best practices for remote work",
    suggested_domain="business"
)
```

### Team Composition Control
```python
# Get team suggestions without execution
team_suggestions = await orchestrator.topic_analyzer.suggest_team_composition(
    analysis
)
```

### Progress Monitoring
```python
# With progress callbacks
result = await orchestrator.respond_to_topic(
    topic="Your topic",
    show_progress=True  # Shows real-time updates
)
```

## 📊 Response Quality

The system provides:
- **Quality Score**: 0-100% rating of the response
- **Confidence Level**: How certain the system is about domain identification
- **Decision Rationale**: Clear explanation of conclusions
- **Execution Time**: Performance metrics

## 🛠️ CLI Commands

### Basic Analysis
```bash
# Analyze without executing
meta-agent analyze "Your topic" --no-execute

# Save results
meta-agent analyze "Your topic" --output results.json
```

### Interactive Mode
```bash
# Explore multiple topics
meta-agent interactive

# Commands in interactive mode:
# - Enter any topic
# - Choose whether to execute workflow
# - Save results
# - Type 'exit' to quit
```

### API Endpoints

- `POST /analyze` - Submit a topic for analysis
- `GET /status/{task_id}` - Check task status
- `GET /tasks` - List all tasks
- `GET /task/{task_id}/team` - Get team details
- `WS /ws` - WebSocket for real-time updates

## 🎨 Customization

### Configure Response Style
```python
# In your topic
"Explain X in a fun, engaging way for kids"
"Provide a detailed technical analysis of Y"
"Give me a quick summary of Z"
```

### Domain-Specific Constraints
```python
# In your topic
"Create a meal plan (budget: $50, time: 30 min/meal)"
"Investment advice (risk: low, timeline: 5 years)"
```

## 📝 Tips for Best Results

1. **Be Specific**: More detail leads to better agent selection
2. **Include Constraints**: Mention any limitations or requirements
3. **State Expected Output**: Clarify what type of response you want
4. **Use Natural Language**: Write as you would ask a human expert

## 🔍 Debugging

Enable detailed logging:
```python
import logging
logging.basicConfig(level=logging.INFO)

result = await orchestrator.respond_to_topic(
    topic="Your topic",
    show_progress=True
)
```

## 🚦 Performance

- Simple topics: 10-20 seconds
- Complex topics: 30-60 seconds
- With workflow execution: 2-5 minutes

## 🔗 Integration Examples

### Slack Bot
```python
@slack_command("/ask")
async def handle_topic(topic: str):
    result = await orchestrator.respond_to_topic(topic)
    return format_slack_response(result)
```

### Web Application
```python
@app.post("/api/analyze")
async def analyze_endpoint(topic: str):
    task_id = await start_analysis(topic)
    return {"task_id": task_id, "status_url": f"/status/{task_id}"}
```

## 🎉 Next Steps

1. Try the interactive CLI to explore different topics
2. Experiment with complex, multi-domain topics
3. Build integrations for your specific use cases
4. Contribute new domain templates

The Topic Response System makes it easy to get expert-level analysis on any subject by automatically assembling the right team of AI specialists!