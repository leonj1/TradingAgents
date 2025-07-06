# Multi-stage Dockerfile for TradingAgents
# Stage 1: Base image with system dependencies
FROM python:3.13-slim as base

# Install system dependencies required by various Python packages
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    git \
    curl \
    build-essential \
    libssl-dev \
    libffi-dev \
    libxml2-dev \
    libxslt1-dev \
    zlib1g-dev \
    # Required for some financial data libraries
    libopenblas-dev \
    liblapack-dev \
    gfortran \
    # Cleanup
    && rm -rf /var/lib/apt/lists/*

# Stage 2: Dependencies installation
FROM base as dependencies

WORKDIR /app

# Copy dependency files
COPY requirements.txt pyproject.toml setup.py ./
COPY README.md ./

# Upgrade pip and install dependencies
RUN pip install --upgrade pip setuptools wheel && \
    pip install --no-cache-dir -r requirements.txt

# Stage 3: Application
FROM dependencies as app

WORKDIR /app

# Copy the entire application
COPY . .

# Install the package in development mode
RUN pip install -e .

# Create directory for results
RUN mkdir -p /app/result_tradingagents

# Set environment variables for Python
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

# Default environment variables (can be overridden)
ENV FINNHUB_API_KEY=""
ENV OPENAI_API_KEY=""
ENV GOOGLE_API_KEY=""
ENV ANTHROPIC_API_KEY=""

# Create a non-root user for security
RUN useradd -m -u 1000 trader && \
    chown -R trader:trader /app

USER trader

# Copy and set permissions for entrypoint script
COPY --chown=trader:trader docker-entrypoint.sh /usr/local/bin/
RUN chmod +x /usr/local/bin/docker-entrypoint.sh

# Volume for results persistence
VOLUME ["/app/result_tradingagents"]

# Expose port if using chainlit (web interface)
EXPOSE 8000

# Set the entrypoint
ENTRYPOINT ["docker-entrypoint.sh"]

# Default command runs the CLI
CMD ["cli"]