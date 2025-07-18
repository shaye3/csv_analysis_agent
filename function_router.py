"""
Function Router Module

This module contains the FunctionRouter class responsible for managing
function calling and tool registration for the CSV QA Agent system.
"""

from typing import Dict, Any, List, Callable, Optional
from langchain.tools import Tool
from langchain_core.tools import BaseTool
from pydantic import BaseModel, Field
import pandas as pd
import json
from abc import ABC, abstractmethod


class CSVAnalysisTool(BaseModel, ABC):
    """Base class for CSV analysis tools."""
    
    name: str
    description: str
    csv_loader: Any = Field(exclude=True)  # Reference to CSVLoader instance
    
    @abstractmethod
    def execute(self, *args, **kwargs) -> str:
        """Execute the tool function."""
        pass


class GetDataSummaryTool(CSVAnalysisTool):
    """Tool to get a summary of the loaded CSV data."""
    
    name: str = "get_data_summary"
    description: str = "Get a comprehensive summary of the loaded CSV dataset including shape, columns, and basic statistics"
    
    def execute(self, *args, **kwargs) -> str:
        """Get data summary."""
        if not self.csv_loader.is_loaded():
            return "No CSV data is currently loaded. Please load a CSV file first."
        
        return self.csv_loader.get_data_summary()


class GetColumnInfoTool(CSVAnalysisTool):
    """Tool to get detailed information about a specific column."""
    
    name: str = "get_column_info"
    description: str = "Get detailed information about a specific column including data type, missing values, unique values, and sample data. Takes column_name as parameter."
    
    def execute(self, column_name: str) -> str:
        """Get column information."""
        if not self.csv_loader.is_loaded():
            return "No CSV data is currently loaded. Please load a CSV file first."
        
        column_info = self.csv_loader.get_column_info(column_name)
        if column_info is None:
            available_columns = self.csv_loader.get_metadata().get('columns', [])
            return f"Column '{column_name}' not found. Available columns: {', '.join(available_columns)}"
        
        # Format the column information nicely
        info_parts = [
            f"Column: {column_info['name']}",
            f"Description: {column_info['description']}",
            f"Data Type: {column_info['dtype']}",
            f"Missing Values: {column_info['null_count']} ({column_info['null_count']/self.csv_loader.get_dataframe().shape[0]*100:.1f}%)",
            f"Unique Values: {column_info['unique_count']}",
            f"Sample Values: {', '.join(map(str, column_info['sample_values'][:5]))}"
        ]
        
        return "\n".join(info_parts)


class SearchDataTool(CSVAnalysisTool):
    """Tool to search for specific data in the CSV."""
    
    name: str = "search_data"
    description: str = "Search for rows containing specific text or values. Takes search_query as parameter and optionally column_names to limit search scope."
    
    def execute(self, search_query: str, column_names: Optional[str] = None) -> str:
        """Search data in CSV."""
        if not self.csv_loader.is_loaded():
            return "No CSV data is currently loaded. Please load a CSV file first."
        
        # Parse column names if provided
        columns = None
        if column_names:
            columns = [col.strip() for col in column_names.split(',')]
        
        results = self.csv_loader.search_data(search_query, columns)
        
        if results.empty:
            return f"No rows found containing '{search_query}'"
        
        # Limit results to prevent overwhelming output
        max_rows = 10
        if len(results) > max_rows:
            result_text = f"Found {len(results)} rows containing '{search_query}'. Showing first {max_rows}:\n\n"
            result_text += results.head(max_rows).to_string(index=False)
            result_text += f"\n\n... and {len(results) - max_rows} more rows."
        else:
            result_text = f"Found {len(results)} rows containing '{search_query}':\n\n"
            result_text += results.to_string(index=False)
        
        return result_text


class GetBasicStatsTool(CSVAnalysisTool):
    """Tool to get basic statistics for numeric columns."""
    
    name: str = "get_basic_stats"
    description: str = "Get basic statistics (mean, median, std, min, max) for numeric columns. Optionally takes column_name to get stats for a specific column."
    
    def execute(self, column_name: Optional[str] = None) -> str:
        """Get basic statistics."""
        if not self.csv_loader.is_loaded():
            return "No CSV data is currently loaded. Please load a CSV file first."
        
        df = self.csv_loader.get_dataframe()
        
        if column_name:
            if column_name not in df.columns:
                return f"Column '{column_name}' not found."
            
            if not pd.api.types.is_numeric_dtype(df[column_name]):
                return f"Column '{column_name}' is not numeric. Cannot calculate statistics."
            
            stats = df[column_name].describe()
            return f"Statistics for '{column_name}':\n{stats.to_string()}"
        else:
            # Get stats for all numeric columns
            numeric_df = df.select_dtypes(include=[float, int])
            if numeric_df.empty:
                return "No numeric columns found in the dataset."
            
            stats = numeric_df.describe()
            return f"Basic statistics for all numeric columns:\n{stats.to_string()}"


class GetValueCountsTool(CSVAnalysisTool):
    """Tool to get value counts for categorical columns."""
    
    name: str = "get_value_counts"
    description: str = "Get value counts (frequency distribution) for a specific column. Takes column_name as parameter."
    
    def execute(self, column_name: str) -> str:
        """Get value counts for a column."""
        if not self.csv_loader.is_loaded():
            return "No CSV data is currently loaded. Please load a CSV file first."
        
        df = self.csv_loader.get_dataframe()
        
        if column_name not in df.columns:
            available_columns = list(df.columns)
            return f"Column '{column_name}' not found. Available columns: {', '.join(available_columns)}"
        
        value_counts = df[column_name].value_counts()
        
        # Limit output to top 20 values
        if len(value_counts) > 20:
            result_text = f"Top 20 values in '{column_name}' (out of {len(value_counts)} unique values):\n\n"
            result_text += value_counts.head(20).to_string()
        else:
            result_text = f"Value counts for '{column_name}':\n\n"
            result_text += value_counts.to_string()
        
        return result_text


class FunctionRouter:
    """
    Manages function calling and tool registration for the CSV QA Agent.
    
    This class handles the registration of tools and routing function calls
    to the appropriate tool implementations.
    """
    
    def __init__(self, csv_loader):
        """
        Initialize the function router.
        
        Args:
            csv_loader: Instance of CSVLoader class
        """
        self.csv_loader = csv_loader
        self._tools: Dict[str, CSVAnalysisTool] = {}
        self._langchain_tools: List[Tool] = []
        
        # Register default tools
        self._register_default_tools()
    
    def _register_default_tools(self) -> None:
        """Register the default set of CSV analysis tools."""
        default_tools = [
            GetDataSummaryTool(csv_loader=self.csv_loader),
            GetColumnInfoTool(csv_loader=self.csv_loader),
            SearchDataTool(csv_loader=self.csv_loader),
            GetBasicStatsTool(csv_loader=self.csv_loader),
            GetValueCountsTool(csv_loader=self.csv_loader)
        ]
        
        for tool in default_tools:
            self.register_tool(tool)
    
    def register_tool(self, tool: CSVAnalysisTool) -> None:
        """
        Register a new tool.
        
        Args:
            tool (CSVAnalysisTool): Tool instance to register
        """
        self._tools[tool.name] = tool
        
        # Create LangChain Tool wrapper
        def tool_func(*args, **kwargs):
            return tool.execute(*args, **kwargs)
        
        langchain_tool = Tool(
            name=tool.name,
            description=tool.description,
            func=tool_func
        )
        
        self._langchain_tools.append(langchain_tool)
    
    def get_available_tools(self) -> List[str]:
        """
        Get list of available tool names.
        
        Returns:
            List[str]: List of tool names
        """
        return list(self._tools.keys())
    
    def get_tool_descriptions(self) -> Dict[str, str]:
        """
        Get descriptions of all available tools.
        
        Returns:
            Dict[str, str]: Dictionary mapping tool names to descriptions
        """
        return {name: tool.description for name, tool in self._tools.items()}
    
    def get_langchain_tools(self) -> List[Tool]:
        """
        Get LangChain Tool objects for use with agents.
        
        Returns:
            List[Tool]: List of LangChain Tool objects
        """
        return self._langchain_tools.copy()
    
    def execute_tool(self, tool_name: str, *args, **kwargs) -> str:
        """
        Execute a specific tool by name.
        
        Args:
            tool_name (str): Name of the tool to execute
            *args: Positional arguments for the tool
            **kwargs: Keyword arguments for the tool
            
        Returns:
            str: Result from tool execution
        """
        if tool_name not in self._tools:
            available_tools = ', '.join(self.get_available_tools())
            return f"Tool '{tool_name}' not found. Available tools: {available_tools}"
        
        try:
            return self._tools[tool_name].execute(*args, **kwargs)
        except Exception as e:
            return f"Error executing tool '{tool_name}': {str(e)}"
    
    def get_tools_for_question(self, question: str) -> List[str]:
        """
        Suggest appropriate tools based on the question content.
        
        Args:
            question (str): User's question
            
        Returns:
            List[str]: List of suggested tool names
        """
        question_lower = question.lower()
        suggested_tools = []
        
        # Simple keyword-based tool suggestion
        if any(keyword in question_lower for keyword in ['summary', 'overview', 'describe', 'about']):
            suggested_tools.append('get_data_summary')
        
        if any(keyword in question_lower for keyword in ['column', 'field', 'variable']):
            suggested_tools.append('get_column_info')
        
        if any(keyword in question_lower for keyword in ['search', 'find', 'contains', 'rows with']):
            suggested_tools.append('search_data')
        
        if any(keyword in question_lower for keyword in ['statistics', 'stats', 'mean', 'average', 'median']):
            suggested_tools.append('get_basic_stats')
        
        if any(keyword in question_lower for keyword in ['count', 'frequency', 'distribution', 'values']):
            suggested_tools.append('get_value_counts')
        
        return suggested_tools
    
    def create_tool_usage_prompt(self) -> str:
        """
        Create a prompt describing available tools for the LLM.
        
        Returns:
            str: Formatted prompt describing available tools
        """
        if not self._tools:
            return "No tools are currently available."
        
        prompt_parts = [
            "You have access to the following tools for analyzing CSV data:",
            ""
        ]
        
        for tool_name, tool in self._tools.items():
            prompt_parts.append(f"- {tool_name}: {tool.description}")
        
        prompt_parts.extend([
            "",
            "Use these tools to answer questions about the CSV data.",
            "Only use tools when you need specific information from the dataset.",
            "Always base your answers on the actual data, not assumptions."
        ])
        
        return "\n".join(prompt_parts)
    
    def validate_csv_context(self) -> bool:
        """
        Validate that CSV data is loaded and tools can be used.
        
        Returns:
            bool: True if CSV context is valid, False otherwise
        """
        return self.csv_loader.is_loaded()
    
    def get_tool_usage_stats(self) -> Dict[str, int]:
        """
        Get usage statistics for tools (placeholder for future implementation).
        
        Returns:
            Dict[str, int]: Tool usage counts
        """
        # This would be implemented to track tool usage over time
        return {tool_name: 0 for tool_name in self._tools.keys()} 
    