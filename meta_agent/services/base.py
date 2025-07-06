"""
Base AI Service class using Pydantic AI with OpenAI o3 model.
All meta-agent services inherit from this base class.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, Optional, TypeVar, Generic
import logging
from tenacity import retry, stop_after_attempt, wait_exponential

from pydantic import BaseModel
from pydantic_ai import Agent
from pydantic_ai.models.openai import OpenAIModel
from pydantic_ai.providers.openai import OpenAIProvider

# Configure logging
logger = logging.getLogger(__name__)

# Type variable for response models
T = TypeVar('T', bound=BaseModel)


class BaseAIService(ABC, Generic[T]):
    """
    Abstract base class for all AI services in the meta-agent system.
    Uses Pydantic AI with OpenAI models.
    """
    
    def __init__(self, api_key: str, model_name: str = "gpt-4.1"):
        """
        Initialize the AI service with OpenAI API key.
        
        Args:
            api_key: OpenAI API key for authentication
            model_name: Model name (default: "gpt-4.1")
        """
        if not api_key:
            raise ValueError("API key is required")
        
        self.api_key = api_key
        self.model_name = model_name
        
        # Initialize OpenAI model with provider
        try:
            provider = OpenAIProvider(api_key=self.api_key)
            self.model = OpenAIModel(
                self.model_name,
                provider=provider
            )
        except Exception as e:
            logger.error(f"Failed to initialize OpenAI model: {str(e)}")
            logger.error(f"Model name: {self.model_name}")
            raise ValueError(f"Failed to initialize OpenAI model '{self.model_name}': {str(e)}")
        
        # Initialize Pydantic AI agent
        self.agent = Agent(
            model=self.model,
            system_prompt=self.get_system_prompt(),
            result_type=self.get_response_model()
        )
        
        logger.info(f"{self.__class__.__name__} initialized with model {model_name}")
    
    @abstractmethod
    def get_system_prompt(self) -> str:
        """
        Get the system prompt for this service.
        Must be implemented by each service.
        
        Returns:
            System prompt string
        """
        pass
    
    @abstractmethod
    def get_response_model(self) -> Optional[type[BaseModel]]:
        """
        Get the Pydantic model for structured responses.
        Return None for unstructured text responses.
        
        Returns:
            Pydantic model class or None
        """
        pass
    
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=4, max=10)
    )
    async def invoke_agent(self, user_prompt: str, **kwargs) -> Any:
        """
        Invoke the AI agent with retry logic.
        
        Args:
            user_prompt: The user prompt to send to the agent
            **kwargs: Additional arguments for the agent
            
        Returns:
            Agent response (structured or text based on response model)
        """
        try:
            result = await self.agent.run(user_prompt, **kwargs)
            return result.output if self.get_response_model() else result.output
        except Exception as e:
            logger.error(f"Error invoking agent: {str(e)}")
            raise
    
    def sync_invoke(self, user_prompt: str, **kwargs) -> Any:
        """
        Synchronous wrapper for invoke_agent.
        
        Args:
            user_prompt: The user prompt to send to the agent
            **kwargs: Additional arguments for the agent
            
        Returns:
            Agent response
        """
        import asyncio
        loop = asyncio.get_event_loop()
        return loop.run_until_complete(self.invoke_agent(user_prompt, **kwargs))
    
    def update_system_prompt(self, new_prompt: str) -> None:
        """
        Update the system prompt and reinitialize the agent.
        
        Args:
            new_prompt: New system prompt
        """
        self._system_prompt_override = new_prompt
        self.agent = Agent(
            model=self.model,
            system_prompt=new_prompt,
            result_type=self.get_response_model()
        )
        logger.info(f"Updated system prompt for {self.__class__.__name__}")
    
    def get_service_info(self) -> Dict[str, Any]:
        """
        Get information about this service.
        
        Returns:
            Dictionary with service information
        """
        return {
            "service_name": self.__class__.__name__,
            "model": self.model_name,
            "has_response_model": self.get_response_model() is not None,
            "system_prompt_length": len(self.get_system_prompt())
        }
