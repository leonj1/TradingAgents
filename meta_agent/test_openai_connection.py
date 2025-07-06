#!/usr/bin/env python3
"""
Test OpenAI connection with pydantic-ai
"""
import os
import asyncio
import sys
from pydantic_ai import Agent
from pydantic_ai.models.openai import OpenAIModel
from pydantic_ai.providers.openai import OpenAIProvider

async def test_connection():
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("Error: OPENAI_API_KEY environment variable not set")
        sys.exit(1)
    
    print(f"Testing OpenAI connection...")
    print(f"API Key: {api_key[:10]}...")
    
    try:
        # Test 
        model = "gpt-4.1"
        print(f"\nTesting with {model}...")
        provider = OpenAIProvider(api_key=api_key)
        model = OpenAIModel(model, provider=provider)
        agent = Agent(model=model, system_prompt="You are a helpful assistant.")
        
        result = await agent.run("Say hello")
        print(f"Success! Response: {result.data}")
        
    except Exception as e:
        print(f"Error with {model}: {type(e).__name__}: {str(e)}")
        
        # Try with gpt-4
        try:
            print("\nTrying with gpt-4...")
            provider = OpenAIProvider(api_key=api_key)
            model = OpenAIModel("gpt-4", provider=provider)
            agent = Agent(model=model, system_prompt="You are a helpful assistant.")
            
            result = await agent.run("Say hello")
            print(f"Success with gpt-4! Response: {result.data}")
        except Exception as e2:
            print(f"Error with gpt-4: {type(e2).__name__}: {str(e2)}")
            sys.exit(1)

if __name__ == "__main__":
    asyncio.run(test_connection())
