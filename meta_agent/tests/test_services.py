"""
Basic tests for meta-agent services.
"""

import pytest
import asyncio
from unittest.mock import Mock, AsyncMock, patch

from meta_agent.services.base import BaseAIService
from meta_agent.services.domain_analyzer import DomainAnalyzer
from meta_agent.schemas.domain import (
    TaskRequest, DomainAnalysis, AgentRole, 
    PersonalityTrait, AgentPersonality
)


class TestBaseAIService:
    """Test the base AI service"""
    
    def test_init_requires_api_key(self):
        """Test that initialization requires an API key"""
        with pytest.raises(ValueError, match="API key is required"):
            
            class TestService(BaseAIService):
                def get_system_prompt(self):
                    return "test"
                
                def get_response_model(self):
                    return None
            
            TestService("")
    
    def test_service_info(self):
        """Test service info method"""
        class TestService(BaseAIService):
            def get_system_prompt(self):
                return "test prompt"
            
            def get_response_model(self):
                return None
        
        service = TestService("test-key")
        info = service.get_service_info()
        
        assert info["service_name"] == "TestService"
        assert info["model"] == "o3"
        assert info["has_response_model"] is False
        assert info["system_prompt_length"] == 11


class TestDomainAnalyzer:
    """Test the domain analyzer service"""
    
    @pytest.fixture
    def analyzer(self):
        """Create a domain analyzer instance"""
        return DomainAnalyzer("test-key")
    
    def test_init(self, analyzer):
        """Test initialization"""
        assert analyzer.api_key == "test-key"
        assert analyzer.model_name == "o3"
        assert len(analyzer.domain_cache) == 0
    
    def test_get_cached_domains(self, analyzer):
        """Test getting cached domains"""
        # Add some fake cache entries
        analyzer.domain_cache["cooking:test1"] = Mock()
        analyzer.domain_cache["cooking:test2"] = Mock()
        analyzer.domain_cache["healthcare:test1"] = Mock()
        
        cached = analyzer.get_cached_domains()
        assert "cooking" in cached
        assert "healthcare" in cached
        assert len(cached) == 2
    
    def test_clear_cache(self, analyzer):
        """Test cache clearing"""
        # Add cache entries
        analyzer.domain_cache["cooking:test1"] = Mock()
        analyzer.domain_cache["healthcare:test1"] = Mock()
        
        # Clear specific domain
        analyzer.clear_cache("cooking")
        assert "cooking:test1" not in analyzer.domain_cache
        assert "healthcare:test1" in analyzer.domain_cache
        
        # Clear all
        analyzer.clear_cache()
        assert len(analyzer.domain_cache) == 0


class TestSchemas:
    """Test schema definitions"""
    
    def test_task_request(self):
        """Test TaskRequest schema"""
        task = TaskRequest(
            domain="cooking",
            task_description="Create a menu",
            constraints={"budget": "$50"},
            expected_output="A complete menu"
        )
        
        assert task.domain == "cooking"
        assert task.priority == "medium"  # default
        assert "budget" in task.constraints
    
    def test_personality_trait(self):
        """Test PersonalityTrait schema"""
        trait = PersonalityTrait(
            name="analytical",
            description="Methodical and detail-oriented",
            strength=0.8
        )
        
        assert trait.name == "analytical"
        assert trait.strength == 0.8
        assert trait.domain_mapping == {}  # default
    
    def test_agent_role_enum(self):
        """Test AgentRole enum"""
        assert AgentRole.EXPLORER.value == "explorer"
        assert AgentRole.DEBATER.value == "debater"
        assert AgentRole.RISK_ASSESSOR.value == "risk_assessor"


@pytest.mark.asyncio
class TestAsyncMethods:
    """Test async methods with mocking"""
    
    async def test_invoke_agent_mock(self):
        """Test invoking agent with mock"""
        class TestService(BaseAIService):
            def get_system_prompt(self):
                return "test"
            
            def get_response_model(self):
                return None
        
        service = TestService("test-key")
        
        # Mock the agent
        service.agent = AsyncMock()
        service.agent.run = AsyncMock(return_value=Mock(data="test response"))
        
        result = await service.invoke_agent("test prompt")
        assert result == "test response"
        service.agent.run.assert_called_once_with("test prompt")


def test_imports():
    """Test that all services can be imported"""
    from meta_agent import (
        MetaAgentOrchestrator,
        DomainAnalyzer,
        AgentFactory,
        DebateOrchestrator,
        PersonalityGenerator,
        ToolSelector,
        QualityValidator,
        WorkflowAdapter
    )
    
    assert MetaAgentOrchestrator is not None
    assert DomainAnalyzer is not None
    assert AgentFactory is not None
    assert DebateOrchestrator is not None
    assert PersonalityGenerator is not None
    assert ToolSelector is not None
    assert QualityValidator is not None
    assert WorkflowAdapter is not None


if __name__ == "__main__":
    pytest.main([__file__, "-v"])