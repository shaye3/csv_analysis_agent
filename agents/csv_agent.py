"""
Main CSV Agent Module

This module contains the main CSVAgent class that ties together all components.
"""

from typing import Optional, List
from models.config import AgentConfig
from models.schemas import QueryResponse, LoadCSVResult, AgentStatus
from core.agent_builder import AgentBuilder
from data_io.csv_loader import CSVLoader


class CSVAgent:
    """
    Main CSV analysis agent that orchestrates all components.
    
    This is the primary interface for users to interact with the CSV analysis system.
    """
    
    def __init__(self, config: Optional[AgentConfig] = None):
        """
        Initialize the CSV agent.
        
        Args:
            config (Optional[AgentConfig]): Agent configuration
        """
        self.config = config or AgentConfig()
        self.agent_builder = AgentBuilder(self.config)
        
        # Quick access to components
        self.csv_loader = self.agent_builder.csv_loader
        self.memory_manager = self.agent_builder.memory_manager
        self.tool_manager = self.agent_builder.tool_manager
        self.query_context = self.agent_builder.query_context
    
    def load_csv(self, file_path: str, **kwargs) -> LoadCSVResult:
        """
        Load a CSV file for analysis.
        
        Args:
            file_path (str): Path to CSV file
            **kwargs: Additional arguments for pandas.read_csv()
            
        Returns:
            LoadCSVResult: Result of the loading operation
        """
        success = self.csv_loader.load_csv(file_path, **kwargs)
        
        if success:
            metadata = self.csv_loader.get_metadata()
            summary = self.csv_loader.get_data_summary()
            
            # Update memory with CSV context
            self.memory_manager.set_csv_context(
                csv_file=metadata.file_name,
                csv_summary=summary
            )
            
            return LoadCSVResult(
                success=True,
                message=f"Successfully loaded {metadata.file_name}",
                metadata=metadata
            )
        else:
            return LoadCSVResult(
                success=False,
                message="Failed to load CSV file",
                metadata=None
            )
    
    def ask_question(self, question: str) -> QueryResponse:
        """
        Ask a question about the CSV data.
        
        Args:
            question (str): User's question
            
        Returns:
            QueryResponse: Complete response with metadata
        """
        return self.agent_builder.query(question)
    
    def get_status(self) -> AgentStatus:
        """Get current agent status."""
        return self.agent_builder.get_status()
    
    def get_data_summary(self) -> Optional[str]:
        """Get summary of loaded data."""
        if not self.csv_loader.is_loaded():
            return None
        return self.csv_loader.get_data_summary()
    
    def get_available_tools(self) -> List[str]:
        """Get list of available tools."""
        return self.tool_manager.get_available_tools()
    
    def get_conversation_history(self) -> str:
        """Get formatted conversation history."""
        return self.memory_manager.get_conversation_context()
    
    def clear_conversation(self) -> None:
        """Clear conversation history."""
        self.agent_builder.clear_conversation()
    
    def suggest_questions(self) -> List[str]:
        """Get suggested questions based on loaded data."""
        return self.agent_builder.suggest_questions()
    
    def execute_tool_directly(self, tool_name: str, *args, **kwargs) -> str:
        """
        Execute a tool directly without going through the agent.
        
        Args:
            tool_name (str): Name of tool to execute
            *args: Positional arguments
            **kwargs: Keyword arguments
            
        Returns:
            str: Tool execution result
        """
        result = self.tool_manager.execute_tool(tool_name, *args, **kwargs)
        return result.result
    
    def get_tool_usage_stats(self) -> dict:
        """Get tool usage statistics."""
        return self.tool_manager.get_tool_usage_stats() 