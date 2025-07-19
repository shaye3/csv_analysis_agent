"""
Tests for CSV Agent
"""

import pytest
import pandas as pd
import tempfile
import os
from unittest.mock import Mock, patch

from agents.csv_agent import CSVAgent
from models.config import AgentConfig, LLMConfig


class TestCSVAgent:
    """Test cases for CSVAgent class."""
    
    @pytest.fixture
    def sample_csv_file(self):
        """Create a temporary CSV file for testing."""
        data = {
            'employee_id': [1, 2, 3, 4],
            'name': ['Alice', 'Bob', 'Charlie', 'Diana'],
            'department': ['Engineering', 'Marketing', 'Engineering', 'Sales'],
            'salary': [70000, 60000, 75000, 55000]
        }
        df = pd.DataFrame(data)
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            df.to_csv(f.name, index=False)
            yield f.name
        
        os.unlink(f.name)
    
    @pytest.fixture
    def agent_config(self):
        """Create agent configuration for testing."""
        return AgentConfig(
            llm=LLMConfig(
                model_name="gpt-3.5-turbo",
                temperature=0.1,
                api_key="test-key"
            ),
            verbose=False
        )
    
    @pytest.fixture
    def mock_agent(self, agent_config):
        """Create a mocked CSV agent."""
        with patch('core.llm_manager.LLMManager') as mock_llm_manager:
            # Mock the LLM manager to avoid actual API calls
            mock_llm_instance = Mock()
            mock_llm_manager.return_value = mock_llm_instance
            
            agent = CSVAgent(agent_config)
            yield agent
    
    def test_agent_initialization(self, agent_config):
        """Test agent initialization."""
        with patch('core.llm_manager.LLMManager'):
            agent = CSVAgent(agent_config)
            
            assert agent.config == agent_config
            assert agent.csv_loader is not None
            assert agent.memory_manager is not None
            assert agent.tool_manager is not None
    
    def test_load_csv_success(self, mock_agent, sample_csv_file):
        """Test successful CSV loading."""
        result = mock_agent.load_csv(sample_csv_file)
        
        assert result.success is True
        assert "Successfully loaded" in result.message
        assert result.metadata is not None
        assert result.metadata.shape == (4, 4)
    
    def test_load_csv_failure(self, mock_agent):
        """Test CSV loading failure."""
        result = mock_agent.load_csv("nonexistent.csv")
        
        assert result.success is False
        assert "Failed to load" in result.message
        assert result.metadata is None
    
    def test_get_status_no_csv(self, mock_agent):
        """Test status when no CSV is loaded."""
        status = mock_agent.get_status()
        
        assert status.csv_loaded is False
        assert status.csv_file is None
        assert isinstance(status.available_tools, list)
        assert len(status.available_tools) > 0
    
    def test_get_status_with_csv(self, mock_agent, sample_csv_file):
        """Test status when CSV is loaded."""
        mock_agent.load_csv(sample_csv_file)
        status = mock_agent.get_status()
        
        assert status.csv_loaded is True
        assert status.csv_file is not None
    
    def test_get_available_tools(self, mock_agent):
        """Test getting available tools."""
        tools = mock_agent.get_available_tools()
        
        assert isinstance(tools, list)
        assert len(tools) > 0
        
        # Check for expected tools
        expected_tools = [
            'get_data_summary',
            'get_column_info', 
            'search_data',
            'get_basic_stats',
            'get_value_counts'
        ]
        
        for tool in expected_tools:
            assert tool in tools
    
    def test_execute_tool_directly(self, mock_agent, sample_csv_file):
        """Test direct tool execution."""
        mock_agent.load_csv(sample_csv_file)
        
        # Test data summary tool
        result = mock_agent.execute_tool_directly('get_data_summary')
        assert isinstance(result, str)
        assert len(result) > 0
    
    def test_suggest_questions_no_csv(self, mock_agent):
        """Test question suggestions when no CSV is loaded."""
        suggestions = mock_agent.suggest_questions()
        
        assert isinstance(suggestions, list)
        assert len(suggestions) > 0
        assert "load a CSV file" in suggestions[0].lower()
    
    def test_suggest_questions_with_csv(self, mock_agent, sample_csv_file):
        """Test question suggestions when CSV is loaded."""
        mock_agent.load_csv(sample_csv_file)
        suggestions = mock_agent.suggest_questions()
        
        assert isinstance(suggestions, list)
        assert len(suggestions) > 0
        
        # Should have meaningful suggestions
        suggestion_text = ' '.join(suggestions).lower()
        assert 'summary' in suggestion_text or 'column' in suggestion_text
    
    def test_clear_conversation(self, mock_agent):
        """Test clearing conversation history."""
        # This should not raise an exception
        mock_agent.clear_conversation()
        
        # Verify conversation is cleared
        history = mock_agent.get_conversation_history()
        assert "No previous conversation" in history or len(history) == 0


class TestAgentIntegration:
    """Integration tests for the CSV agent system."""
    
    @pytest.fixture
    def integration_csv_file(self):
        """Create a more complex CSV for integration testing."""
        data = {
            'id': range(1, 101),
            'name': [f'Employee_{i}' for i in range(1, 101)],
            'department': ['Engineering', 'Marketing', 'Sales', 'HR'] * 25,
            'salary': [50000 + i * 1000 for i in range(100)],
            'years_experience': [i % 10 + 1 for i in range(100)],
            'location': ['NYC', 'LA', 'Chicago', 'Austin'] * 25
        }
        df = pd.DataFrame(data)
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            df.to_csv(f.name, index=False)
            yield f.name
        
        os.unlink(f.name)
    
    def test_full_workflow(self, integration_csv_file):
        """Test a complete workflow from loading to querying."""
        config = AgentConfig(
            llm=LLMConfig(api_key="test-key"),
            verbose=False
        )
        
        with patch('core.llm_manager.LLMManager'):
            agent = CSVAgent(config)
            
            # Load CSV
            result = agent.load_csv(integration_csv_file)
            assert result.success
            
            # Check status
            status = agent.get_status()
            assert status.csv_loaded
            
            # Execute tools
            summary = agent.execute_tool_directly('get_data_summary')
            assert 'Employee_' in summary or '100' in summary
            
            column_info = agent.execute_tool_directly('get_column_info', 'department')
            assert 'department' in column_info.lower() 