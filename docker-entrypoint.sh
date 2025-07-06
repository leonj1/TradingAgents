#!/bin/bash
set -e

# Function to check if required environment variables are set
check_env_vars() {
    local missing_vars=()
    
    if [ -z "$FINNHUB_API_KEY" ]; then
        missing_vars+=("FINNHUB_API_KEY")
    fi
    
    if [ -z "$OPENAI_API_KEY" ] && [ -z "$GOOGLE_API_KEY" ] && [ -z "$ANTHROPIC_API_KEY" ]; then
        echo "ERROR: At least one LLM API key must be set (OPENAI_API_KEY, GOOGLE_API_KEY, or ANTHROPIC_API_KEY)"
        exit 1
    fi
    
    if [ ${#missing_vars[@]} -ne 0 ]; then
        echo "ERROR: Required environment variables are not set: ${missing_vars[*]}"
        echo "Please set these variables in your .env file or docker-compose.yml"
        exit 1
    fi
}

# Function to display help
show_help() {
    echo "TradingAgents Docker Container"
    echo ""
    echo "Usage:"
    echo "  docker run -it tradingagents [COMMAND] [ARGS]"
    echo ""
    echo "Commands:"
    echo "  cli                    Run the interactive CLI (default)"
    echo "  analyze TICKER DATE    Run analysis for a specific ticker and date"
    echo "  python [script]        Run a Python script"
    echo "  bash                   Start a bash shell"
    echo "  help                   Show this help message"
    echo ""
    echo "Examples:"
    echo "  docker run -it tradingagents cli"
    echo "  docker run -it tradingagents analyze NVDA 2024-05-10"
    echo "  docker run -it tradingagents python main.py"
    echo ""
    echo "Environment Variables:"
    echo "  FINNHUB_API_KEY       Required for financial data"
    echo "  OPENAI_API_KEY        Required if using OpenAI models"
    echo "  GOOGLE_API_KEY        Required if using Google models"
    echo "  ANTHROPIC_API_KEY     Required if using Anthropic models"
}

# Check environment variables
check_env_vars

# Handle commands
case "$1" in
    ""|"cli")
        echo "Starting TradingAgents CLI..."
        exec python -m cli.main
        ;;
    "analyze")
        if [ -z "$2" ] || [ -z "$3" ]; then
            echo "ERROR: 'analyze' command requires TICKER and DATE arguments"
            echo "Usage: docker run -it tradingagents analyze TICKER DATE"
            echo "Example: docker run -it tradingagents analyze NVDA 2024-05-10"
            exit 1
        fi
        echo "Analyzing $2 for date $3..."
        exec python -c "
from tradingagents.graph.trading_graph import TradingAgentsGraph
from tradingagents.default_config import DEFAULT_CONFIG

ta = TradingAgentsGraph(debug=True, config=DEFAULT_CONFIG.copy())
_, decision = ta.propagate('$2', '$3')
print(decision)
"
        ;;
    "python")
        shift
        exec python "$@"
        ;;
    "bash")
        exec /bin/bash
        ;;
    "help"|"--help"|"-h")
        show_help
        exit 0
        ;;
    *)
        # Try to run the command directly
        exec "$@"
        ;;
esac