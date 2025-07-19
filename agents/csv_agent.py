"""
Main CSV Agent Module

This module contains the main CSVAgent class that ties together all components.
"""

from typing import Optional, List
import pandas as pd
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
            
            # Gather comprehensive column context
            column_context = self._gather_full_column_context()
            
            # Update memory with complete CSV context
            self.memory_manager.set_csv_context(
                csv_file=metadata.file_name,
                csv_summary=summary
            )
            
            # Store column context in agent builder for use in queries
            self.agent_builder.set_column_context(column_context)
            
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
    
    def _gather_full_column_context(self) -> str:
        """
        Gather comprehensive context about all columns in the CSV.
        
        Returns:
            str: Formatted context with all column information
        """
        if not self.csv_loader.is_loaded():
            return "No CSV data loaded."
        
        context_parts = ["COMPLETE DATASET CONTEXT:"]
        context_parts.append("=" * 50)
        
        # Get analytics classification first
        analytics = self.csv_loader.get_analytics_summary()
        context_parts.append(f"\n📊 ANALYTICS OVERVIEW:")
        context_parts.append(f"• Dataset: {analytics['total_columns']} columns ({analytics['measure_count']} measures, {analytics['dimension_count']} dimensions)")
        context_parts.append(f"• Measures: {', '.join(analytics['measures'])}")
        context_parts.append(f"• Dimensions: {', '.join(analytics['dimensions'])}")
        
        # Get detailed info for each column
        context_parts.append(f"\n📋 DETAILED COLUMN INFORMATION:")
        
        df = self.csv_loader.get_dataframe()
        for column in df.columns:
            column_info = self.csv_loader.get_column_info(column)
            if column_info:
                context_parts.append(f"\n• {column} ({column_info.column_type.value.upper()}):")
                context_parts.append(f"  📝 {column_info.description}")
                context_parts.append(f"  🔢 Type: {column_info.dtype}")
                context_parts.append(f"  📊 Unique values: {column_info.unique_count}")
                context_parts.append(f"  ❌ Missing: {column_info.null_count}")
                
                # Show sample values for dimensions (categorical data)
                if column_info.column_type.value == "dimension" and column_info.unique_count <= 20:
                    sample_values = [str(v) for v in column_info.sample_values[:10]]
                    context_parts.append(f"  💡 Available values: {', '.join(sample_values)}")
                elif column_info.column_type.value == "dimension" and column_info.unique_count > 20:
                    sample_values = [str(v) for v in column_info.sample_values[:5]]
                    context_parts.append(f"  💡 Sample values: {', '.join(sample_values)}... (and {column_info.unique_count-5} more)")
                elif column_info.column_type.value == "measure":
                    # For measures, show min/max range
                    try:
                        series = df[column]
                        if pd.api.types.is_numeric_dtype(series):
                            min_val = series.min()
                            max_val = series.max()
                            context_parts.append(f"  📈 Range: {min_val} to {max_val}")
                    except:
                        pass
        
        context_parts.append(f"\n🎯 TOOL USAGE GUIDANCE:")
        context_parts.append(f"• Use sort_data() to sort by any columns with asc/desc order")
        context_parts.append(f"• Use filter_data() with dimensions and their available values")
        context_parts.append(f"• Use group_and_aggregate() to group by dimensions and aggregate measures")
        context_parts.append(f"• Use get_basic_stats() with measures for numerical analysis")
        context_parts.append(f"• Always reference exact column names and available values shown above")
        
        return "\n".join(context_parts)
    
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