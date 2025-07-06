# Meta-Agent System Troubleshooting Guide

## Common Issues and Solutions

### 1. ModelHTTPError / RetryError

**Error**: `RetryError[<Future at 0x... state=finished raised ModelHTTPError>]`

**Possible Causes**:
- Invalid or missing OpenAI API key
- Invalid model name
- Network connectivity issues
- OpenAI API rate limits

**Solutions**:
1. Verify your API key is set correctly:
   ```bash
   echo $OPENAI_API_KEY
   ```

2. Test the OpenAI connection:
   ```bash
   make test-openai
   ```

3. Check which models are available for your API key:
   - Standard models: `gpt-3.5-turbo`, `gpt-4`
   - If you don't have GPT-4 access, the system defaults to `gpt-3.5-turbo`

4. If using a custom OpenAI endpoint, ensure it's properly configured

### 2. SyntaxError in CLI

**Error**: `SyntaxError: expected 'except' or 'finally' block`

**Solution**: This has been fixed. Rebuild the Docker image:
```bash
make build
```

### 3. API Key Not Found

**Error**: `Warning: OPENAI_API_KEY environment variable is not set`

**Solution**:
```bash
export OPENAI_API_KEY="your-api-key-here"
```

### 4. Docker Build Issues

**Error**: `failed to calculate checksum... '/meta_agent': not found`

**Solution**: Run make commands from the meta_agent directory:
```bash
cd meta_agent
make build
```

## Testing the System

### 1. Test OpenAI Connection
```bash
make test-openai
```

### 2. Run with Debug Mode
```bash
# Open a shell in the container
make shell

# Run the CLI with logging
python -m meta_agent.interfaces.cli analyze "test topic" --log-level DEBUG
```

### 3. Check Container Logs
```bash
make logs
```

## Model Configuration

The system defaults to `gpt-3.5-turbo`. To use a different model:

1. Set environment variable:
   ```bash
   export OPENAI_MODEL="gpt-4"  # if you have access
   ```

2. Or modify the default in `/meta_agent/services/base.py`

## Common Model Names
- `gpt-3.5-turbo` - Most cost-effective, widely available
- `gpt-4` - More capable but requires access
- `gpt-4-turbo-preview` - Latest GPT-4 variant

## Rate Limiting

If you encounter rate limits:
1. The system has built-in retry logic with exponential backoff
2. Consider using a less expensive model like `gpt-3.5-turbo`
3. Add delays between requests

## Network Issues

If behind a corporate proxy:
1. Set proxy environment variables before running:
   ```bash
   export HTTP_PROXY=http://proxy.company.com:8080
   export HTTPS_PROXY=http://proxy.company.com:8080
   ```

2. Pass proxy settings to Docker:
   ```bash
   docker run -e HTTP_PROXY=$HTTP_PROXY -e HTTPS_PROXY=$HTTPS_PROXY ...
   ```

## Getting Help

1. Check the logs for detailed error messages
2. Run `make test-openai` to verify basic connectivity
3. Review the API key permissions in your OpenAI account
4. Ensure you're using a supported model name