# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

TradingAgents is a multi-agent LLM-powered financial trading framework that simulates real-world trading firms. The system uses specialized AI agents (analysts, researchers, traders, risk managers) working collaboratively to analyze markets and make trading decisions.

**Key Technologies:**
- Language: Python (>=3.10)
- Framework: LangGraph for agent orchestration
- LLMs: OpenAI, Google, Anthropic support
- Data Sources: FinnHub, Yahoo Finance, Reddit, news feeds
- CLI: Rich terminal UI with Typer

## Common Commands

### Running the Application

```bash
# Interactive CLI interface (recommended for first-time users)
python -m cli.main

# Direct script execution with default settings
python main.py

# Using the installed package command
tradingagents analyze
```

### Development Setup

```bash
# Install dependencies (multiple options available)
pip install -r requirements.txt

# Using UV package manager (if installed)
uv sync

# Install in development mode
pip install -e .
```

### Required Environment Variables

```bash
export FINNHUB_API_KEY=$YOUR_FINNHUB_API_KEY  # Required for financial data
export OPENAI_API_KEY=$YOUR_OPENAI_API_KEY    # Required for agents
# Optional for alternative LLM providers:
export GOOGLE_API_KEY=$YOUR_GOOGLE_API_KEY
export ANTHROPIC_API_KEY=$YOUR_ANTHROPIC_API_KEY
```

## Architecture Overview

### Directory Structure

```
tradingagents/
├── agents/              # All agent implementations
│   ├── analysts/       # 4 specialist analysts
│   │   ├── fundamentals_analyst.py
│   │   ├── sentiment_analyst.py
│   │   ├── news_analyst.py
│   │   └── technical_analyst.py
│   ├── researchers/    # Bull/bear researchers
│   ├── trader/         # Trading decision maker
│   ├── risk_mgmt/      # Risk assessment team
│   └── managers/       # Research and portfolio managers
├── graph/              # LangGraph workflow orchestration
├── dataflows/          # Data integrations (APIs, scrapers)
└── default_config.py   # Configuration settings
```

### Agent Flow

1. **Analysts** gather data from various sources (financial, news, sentiment, technical)
2. **Researchers** (bull & bear) debate the analysts' findings
3. **Trader** synthesizes reports and proposes trades
4. **Risk Management** team evaluates proposals
5. **Portfolio Manager** makes final approval/rejection

### Key Files

- `tradingagents/graph/trading_graph.py`: Main orchestration logic
- `tradingagents/default_config.py`: Configuration options
- `cli/main.py`: Interactive CLI implementation
- `main.py`: Example usage script

## Development Guidelines

### Working with Agents

1. **Agent Structure**: Each agent inherits from base classes and implements specific analysis methods
2. **LLM Usage**: Agents use configurable LLMs (deep_think_llm for complex analysis, quick_think_llm for simple tasks)
3. **State Management**: Uses LangGraph's state system for passing data between agents

### Configuration

The system uses `tradingagents/default_config.py`. Key options:

```python
{
    "llm_provider": "openai",          # or "google", "anthropic"
    "deep_think_llm": "o4-mini",       # For complex reasoning
    "quick_think_llm": "gpt-4o-mini",  # For quick tasks
    "max_debate_rounds": 1,            # Researcher debate rounds
    "max_risk_discuss_rounds": 1,      # Risk team discussion rounds
    "online_tools": True,              # True for real-time data, False for cached
    "results_dir": "result_tradingagents"  # Output directory
}
```

### Cost Optimization

- Use cheaper models (o4-mini, gpt-4o-mini) for development/testing
- The framework makes many API calls - monitor usage
- Set `online_tools: False` to use cached data during development

### Results Storage

Analysis results are saved in structured directories:
```
{results_dir}/{ticker}/{analysis_date}/
├── reports/           # Agent reports
├── messages/          # Agent communications
└── final_decision.md  # Trading decision
```

## Important Considerations

1. **No Test Suite**: Currently lacks formal testing infrastructure
2. **No Linting**: No configured linting or formatting tools
3. **Multiple Dependency Files**: `requirements.txt`, `pyproject.toml`, and `setup.py` may have inconsistencies
4. **API Rate Limits**: Be mindful of FinnHub and LLM API limits
5. **Non-deterministic**: Results vary based on LLM temperature and market conditions

## Adding New Features

1. **New Agent**: Create in appropriate subdirectory under `tradingagents/agents/`
2. **New Data Source**: Add to `tradingagents/dataflows/`
3. **Graph Modifications**: Update `tradingagents/graph/trading_graph.py`
4. **CLI Updates**: Modify `cli/main.py` for new user options

## Debugging

- Set `debug=True` when initializing `TradingAgentsGraph`
- Check message logs in results directory
- Use CLI's real-time display to monitor agent progress
- Review agent reports for decision reasoning

## Known Limitations

- Designed for research, not production trading
- Performance depends heavily on LLM quality and prompts
- Real-time data requires paid API subscriptions
- No backtesting framework currently integrated

## Docker Usage

### Quick Start with Docker

1. **Clone the repository and set up environment:**
```bash
git clone https://github.com/TauricResearch/TradingAgents.git
cd TradingAgents
cp .env.example .env
# Edit .env and add your API keys
```

2. **Build and run with Docker Compose:**
```bash
# Build the image
docker-compose build

# Run the interactive CLI
docker-compose run --rm tradingagents

# Run analysis for specific ticker
docker-compose run --rm tradingagents analyze NVDA 2024-05-10

# Run with custom Python script
docker-compose run --rm tradingagents python main.py
```

3. **Using Docker directly:**
```bash
# Build the image
docker build -t tradingagents .

# Run with environment file
docker run -it --env-file .env -v $(pwd)/result_tradingagents:/app/result_tradingagents tradingagents

# Run specific commands
docker run -it --env-file .env tradingagents analyze TSLA 2024-05-15
docker run -it --env-file .env tradingagents bash
```

### Docker Configuration

- **Dockerfile**: Multi-stage build with Python 3.13, includes all system dependencies
- **docker-compose.yml**: Includes optional Redis service for caching
- **docker-entrypoint.sh**: Flexible entry point supporting CLI, analysis, and custom commands
- **.dockerignore**: Optimizes build context by excluding unnecessary files
- **.env.example**: Template for required API keys

### Docker Commands

```bash
# View help
docker-compose run --rm tradingagents help

# Interactive shell
docker-compose run --rm tradingagents bash

# Run with specific LLM provider
docker-compose run --rm -e LLM_PROVIDER=google tradingagents

# Persist results outside container
docker-compose up -d  # Runs in background with volume mounts
```

### Docker Volumes

- Results are persisted in `./result_tradingagents` on the host
- Redis data persisted in named volume `redis-data`
- Config can be mounted read-only for customization

### Makefile Usage

A Makefile is provided for convenient Docker operations:

```bash
# Build the Docker image
make build

# Start services in background
make start

# Stop services
make stop

# Restart services
make restart

# Run interactive CLI
make cli

# Analyze specific ticker
make analyze TICKER=NVDA DATE=2024-05-10

# View logs
make logs

# Open shell in container
make shell

# Run Python scripts
make python                    # Runs main.py
make python SCRIPT=myfile.py   # Runs specific script

# Cleanup
make clean        # Remove containers and volumes
make clean-all    # Full cleanup including images

# Show help
make help
```

The Makefile includes colored output and automatic `.env` file checking. A `PORT` variable is available for future web interface extensions (default: 8000).