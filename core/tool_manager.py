"""
Tool Manager Module

This module contains the enhanced tool management system for CSV analysis.
"""

from typing import Dict, Any, List, Optional, Type
from langchain.tools import Tool, StructuredTool
from pydantic import BaseModel, Field
import pandas as pd
from abc import ABC, abstractmethod
import time

from models.config import ToolConfig
from models.schemas import ToolExecutionResult

# Import visualization components
try:
    from utils.visualizer import CSVVisualizer
    VISUALIZATION_AVAILABLE = True
except ImportError:
    VISUALIZATION_AVAILABLE = False


class VisualizationInput(BaseModel):
    """Input schema for visualization tool."""
    analysis_type: str = Field(description="Type of analysis: 'distribution', 'sum', 'average', or 'count'")
    measure: str = Field(default="", description="Column name for measure (required for distribution, sum, average)")
    dimension: str = Field(default="", description="Column name for dimension (required for sum, average, count)")


class CSVAnalysisTool(BaseModel, ABC):
    """Abstract base class for CSV analysis tools."""
    
    name: str
    description: str
    csv_loader: Any = Field(exclude=True)
    
    @abstractmethod
    def execute(self, *args, **kwargs) -> str:
        """Execute the tool function."""
        pass
    
    def validate_csv_loaded(self) -> bool:
        """Check if CSV data is loaded."""
        return self.csv_loader and self.csv_loader.is_loaded()


class GetDataSummaryTool(CSVAnalysisTool):
    """Tool to get dataset summary."""
    
    name: str = "get_data_summary"
    description: str = "Get comprehensive summary of the loaded CSV dataset including shape, columns, and basic statistics"
    
    def execute(self) -> str:
        """Get data summary."""
        if not self.validate_csv_loaded():
            return "No CSV data is currently loaded. Please load a CSV file first."
        return self.csv_loader.get_data_summary()


class GetColumnInfoTool(CSVAnalysisTool):
    """Tool to get column information."""
    
    name: str = "get_column_info"
    description: str = "Get detailed information about a specific column including data type, missing values, unique values, and sample data. Takes column_name as parameter."
    
    def execute(self, column_name: str) -> str:
        """Get column information."""
        if not self.validate_csv_loaded():
            return "No CSV data is currently loaded. Please load a CSV file first."
        
        column_info = self.csv_loader.get_column_info(column_name)
        if column_info is None:
            available_columns = self.csv_loader.get_metadata().get('columns', [])
            return f"Column '{column_name}' not found. Available columns: {', '.join(available_columns)}"
        
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
    """Tool to search for data in CSV."""
    
    name: str = "search_data"
    description: str = "Search for rows containing specific text or values. Takes search_query as parameter and optionally column_names to limit search scope."
    
    def execute(self, search_query: str, column_names: Optional[str] = None) -> str:
        """Search data in CSV."""
        if not self.validate_csv_loaded():
            return "No CSV data is currently loaded. Please load a CSV file first."
        
        columns = None
        if column_names:
            columns = [col.strip() for col in column_names.split(',')]
        
        results = self.csv_loader.search_data(search_query, columns)
        
        if results.empty:
            return f"No rows found containing '{search_query}'"
        
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
    """Tool to get basic statistics."""
    
    name: str = "get_basic_stats"
    description: str = "Get basic statistics (mean, median, std, min, max) for numeric columns. Optionally takes column_name to get stats for a specific column."
    
    def execute(self, column_name: Optional[str] = None) -> str:
        """Get basic statistics."""
        if not self.validate_csv_loaded():
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
            numeric_df = df.select_dtypes(include=[float, int])
            if numeric_df.empty:
                return "No numeric columns found in the dataset."
            
            stats = numeric_df.describe()
            return f"Basic statistics for all numeric columns:\n{stats.to_string()}"


class GetValueCountsTool(CSVAnalysisTool):
    """Tool to get value counts."""
    
    name: str = "get_value_counts"
    description: str = "Get value counts (frequency distribution) for a specific column. Takes column_name as parameter."
    
    def execute(self, column_name: str) -> str:
        """Get value counts for a column."""
        if not self.validate_csv_loaded():
            return "No CSV data is currently loaded. Please load a CSV file first."
        
        df = self.csv_loader.get_dataframe()
        
        if column_name not in df.columns:
            available_columns = list(df.columns)
            return f"Column '{column_name}' not found. Available columns: {', '.join(available_columns)}"
        
        value_counts = df[column_name].value_counts()
        
        if len(value_counts) > 20:
            result_text = f"Top 20 values in '{column_name}' (out of {len(value_counts)} unique values):\n\n"
            result_text += value_counts.head(20).to_string()
        else:
            result_text = f"Value counts for '{column_name}':\n\n"
            result_text += value_counts.to_string()
        
        return result_text


class GetAnalyticsClassificationTool(CSVAnalysisTool):
    """Tool to get analytics classification (measures vs dimensions)."""
    
    name: str = "get_analytics_classification"
    description: str = "Get analytics classification showing which columns are measures vs dimensions for business intelligence analysis"
    
    def execute(self) -> str:
        """Get analytics classification summary."""
        if not self.validate_csv_loaded():
            return "No CSV data is currently loaded. Please load a CSV file first."
        
        try:
            analytics_summary = self.csv_loader.get_analytics_summary()
            
            result = f"📊 Analytics Classification Summary:\n"
            result += f"═══════════════════════════════════════\n\n"
            result += f"📈 MEASURES ({analytics_summary['measure_count']}):\n"
            result += f"   • {', '.join(analytics_summary['measures'])}\n\n"
            result += f"📂 DIMENSIONS ({analytics_summary['dimension_count']}):\n"
            result += f"   • {', '.join(analytics_summary['dimensions'])}\n\n"
            result += f"💡 {analytics_summary['summary']}\n\n"
            result += f"🎯 Use measures for: aggregation, sum, average, min, max\n"
            result += f"🔍 Use dimensions for: grouping, filtering, categorizing"
            
            return result
            
        except Exception as e:
            return f"Error getting analytics classification: {str(e)}"


class ListAvailableMeasuresTool(CSVAnalysisTool):
    """Tool to list available measures."""
    
    name: str = "list_measures"
    description: str = "List all available measures (numerical fields for aggregation) in the dataset"
    
    def execute(self) -> str:
        """Get list of available measures."""
        if not self.validate_csv_loaded():
            return "No CSV data is currently loaded. Please load a CSV file first."
        
        try:
            measures = self.csv_loader.get_measures()
            
            if not measures:
                return "No measures found in the dataset. All columns appear to be dimensions."
            
            result = f"📈 Available Measures ({len(measures)}):\n"
            result += "═══════════════════════════════════\n\n"
            
            for measure in measures:
                column_info = self.csv_loader.get_column_info(measure)
                if column_info:
                    result += f"• {measure} ({column_info.dtype})\n"
                    result += f"  📝 {column_info.description}\n"
                    result += f"  📊 {column_info.unique_count} unique values\n\n"
            
            result += "💡 These fields can be used for: sum, average, min, max, distribution analysis"
            return result
            
        except Exception as e:
            return f"Error listing measures: {str(e)}"


class ListAvailableDimensionsTool(CSVAnalysisTool):
    """Tool to list available dimensions."""
    
    name: str = "list_dimensions"
    description: str = "List all available dimensions (categorical fields for grouping) in the dataset"
    
    def execute(self) -> str:
        """Get list of available dimensions."""
        if not self.validate_csv_loaded():
            return "No CSV data is currently loaded. Please load a CSV file first."
        
        try:
            dimensions = self.csv_loader.get_dimensions()
            
            if not dimensions:
                return "No dimensions found in the dataset. All columns appear to be measures."
            
            result = f"📂 Available Dimensions ({len(dimensions)}):\n"
            result += "═══════════════════════════════════════\n\n"
            
            for dimension in dimensions:
                column_info = self.csv_loader.get_column_info(dimension)
                if column_info:
                    result += f"• {dimension} ({column_info.dtype})\n"
                    result += f"  📝 {column_info.description}\n"
                    result += f"  📊 {column_info.unique_count} unique values\n\n"
            
            result += "💡 These fields can be used for: grouping, filtering, categorizing, count analysis"
            return result
            
        except Exception as e:
            return f"Error listing dimensions: {str(e)}"


class CreateVisualizationTool(CSVAnalysisTool):
    """Tool to create data visualizations."""
    
    name: str = "create_visualization"
    description: str = """Create data visualizations. Parameters:
    - analysis_type: 'distribution', 'sum', 'average', or 'count'
    - measure: column name (required for distribution, sum, average)
    - dimension: column name (required for sum, average, count)
    
    Examples:
    - create_visualization(analysis_type='distribution', measure='salary')
    - create_visualization(analysis_type='sum', measure='salary', dimension='department')
    - create_visualization(analysis_type='count', dimension='department')"""
    
    def execute(self, analysis_type: str, measure: str = "", dimension: str = "") -> str:
        """Create a visualization."""
        if not self.validate_csv_loaded():
            return "No CSV data is currently loaded. Please load a CSV file first."
        
        if not VISUALIZATION_AVAILABLE:
            return "Visualization functionality is not available. Please install matplotlib and seaborn."
        
        # Validate analysis type
        valid_types = ["distribution", "sum", "average", "count"]
        if analysis_type not in valid_types:
            return f"Invalid analysis_type '{analysis_type}'. Must be one of: {', '.join(valid_types)}"
        
        try:
            df = self.csv_loader.get_dataframe()
            visualizer = CSVVisualizer()
            
            # Create the visualization
            result = visualizer.analyze_and_plot(
                dataframe=df,
                dimension=dimension,
                measure=measure,
                analysis_type=analysis_type,
                show_plot=True
            )
            
            # Format the response
            response = f"✅ Successfully created {analysis_type} visualization!\n\n"
            response += f"📊 Analysis Type: {analysis_type.title()}\n"
            
            if measure:
                response += f"📈 Measure: {measure}\n"
            if dimension:
                response += f"📂 Dimension: {dimension}\n"
            
            if 'statistics' in result:
                stats = result['statistics']
                response += f"\n📊 Statistics:\n"
                response += f"   • Mean: {stats.get('mean', 'N/A'):.2f}\n"
                response += f"   • Median: {stats.get('median', 'N/A'):.2f}\n"
                response += f"   • Min: {stats.get('min', 'N/A')}\n"
                response += f"   • Max: {stats.get('max', 'N/A')}\n"
            
            if 'summary' in result:
                summary = result['summary']
                response += f"\n📈 Summary:\n"
                for key, value in summary.items():
                    response += f"   • {key.replace('_', ' ').title()}: {value}\n"
            
            response += f"\n💡 The chart has been displayed. You can now ask for more analysis or create additional visualizations!"
            
            return response
            
        except Exception as e:
            return f"Error creating visualization: {str(e)}\n\nMake sure you're using valid column names. Use 'list_measures' and 'list_dimensions' to see available options."


class ToolManager:
    """
    Enhanced tool manager for CSV analysis tools.
    
    Handles tool registration, execution, and monitoring.
    """
    
    def __init__(self, config: ToolConfig, csv_loader):
        """
        Initialize the tool manager.
        
        Args:
            config (ToolConfig): Tool configuration
            csv_loader: CSV loader instance
        """
        self.config = config
        self.csv_loader = csv_loader
        self._tools: Dict[str, CSVAnalysisTool] = {}
        self._langchain_tools: List[Tool] = []
        self._execution_stats: Dict[str, int] = {}
        
        self._register_default_tools()
    
    def _register_default_tools(self) -> None:
        """Register default CSV analysis tools."""
        default_tools = [
            GetDataSummaryTool(csv_loader=self.csv_loader),
            GetColumnInfoTool(csv_loader=self.csv_loader),
            SearchDataTool(csv_loader=self.csv_loader),
            GetBasicStatsTool(csv_loader=self.csv_loader),
            GetValueCountsTool(csv_loader=self.csv_loader),
            GetAnalyticsClassificationTool(csv_loader=self.csv_loader),
            ListAvailableMeasuresTool(csv_loader=self.csv_loader),
            ListAvailableDimensionsTool(csv_loader=self.csv_loader),
            CreateVisualizationTool(csv_loader=self.csv_loader)
        ]
        
        for tool in default_tools:
            if tool.name in self.config.enabled_tools:
                self.register_tool(tool)
    
    def register_tool(self, tool: CSVAnalysisTool) -> None:
        """
        Register a new tool.
        
        Args:
            tool (CSVAnalysisTool): Tool to register
        """
        self._tools[tool.name] = tool
        self._execution_stats[tool.name] = 0
        
        # Special handling for create_visualization tool (multi-parameter)
        if tool.name == "create_visualization":
            def visualization_func(analysis_type: str, measure: str = "", dimension: str = "") -> str:
                return self._execute_tool_with_tracking(tool.name, analysis_type, measure, dimension)
            
            langchain_tool = StructuredTool.from_function(
                name=tool.name,
                description=tool.description,
                func=visualization_func,
                args_schema=VisualizationInput
            )
        else:
            # Regular single-parameter tools
            def tool_func(*args, **kwargs):
                return self._execute_tool_with_tracking(tool.name, *args, **kwargs)
            
            langchain_tool = Tool(
                name=tool.name,
                description=tool.description,
                func=tool_func
            )
        
        self._langchain_tools.append(langchain_tool)
    
    def _execute_tool_with_tracking(self, tool_name: str, *args, **kwargs) -> str:
        """Execute tool with performance tracking."""
        start_time = time.time()
        try:
            result = self._tools[tool_name].execute(*args, **kwargs)
            self._execution_stats[tool_name] += 1
            execution_time = time.time() - start_time
            return result
        except Exception as e:
            execution_time = time.time() - start_time
            return f"Error executing tool '{tool_name}': {str(e)}"
    
    def get_available_tools(self) -> List[str]:
        """Get list of available tool names."""
        return list(self._tools.keys())
    
    def get_langchain_tools(self) -> List[Tool]:
        """Get LangChain tools for agent use."""
        return self._langchain_tools.copy()
    
    def execute_tool(self, tool_name: str, *args, **kwargs) -> ToolExecutionResult:
        """
        Execute a specific tool and return detailed result.
        
        Args:
            tool_name (str): Name of tool to execute
            *args: Positional arguments
            **kwargs: Keyword arguments
            
        Returns:
            ToolExecutionResult: Execution result with metadata
        """
        if tool_name not in self._tools:
            return ToolExecutionResult(
                tool_name=tool_name,
                success=False,
                result=f"Tool '{tool_name}' not found. Available: {', '.join(self.get_available_tools())}",
                execution_time=0.0
            )
        
        start_time = time.time()
        try:
            result = self._tools[tool_name].execute(*args, **kwargs)
            execution_time = time.time() - start_time
            self._execution_stats[tool_name] += 1
            
            return ToolExecutionResult(
                tool_name=tool_name,
                success=True,
                result=result,
                execution_time=execution_time,
                metadata={"args": args, "kwargs": kwargs}
            )
        except Exception as e:
            execution_time = time.time() - start_time
            return ToolExecutionResult(
                tool_name=tool_name,
                success=False,
                result=f"Error: {str(e)}",
                execution_time=execution_time,
                metadata={"error": str(e)}
            )
    
    def get_tool_usage_stats(self) -> Dict[str, int]:
        """Get tool usage statistics."""
        return self._execution_stats.copy()
    
    def suggest_tools_for_question(self, question: str) -> List[str]:
        """Suggest appropriate tools for a question."""
        question_lower = question.lower()
        suggested_tools = []
        
        keyword_mappings = {
            'get_data_summary': ['summary', 'overview', 'describe', 'about'],
            'get_column_info': ['column', 'field', 'variable'],
            'search_data': ['search', 'find', 'contains', 'rows with'],
            'get_basic_stats': ['statistics', 'stats', 'mean', 'average', 'median'],
            'get_value_counts': ['count', 'frequency', 'distribution', 'values']
        }
        
        for tool_name, keywords in keyword_mappings.items():
            if tool_name in self._tools and any(keyword in question_lower for keyword in keywords):
                suggested_tools.append(tool_name)
        
        return suggested_tools


# Legacy compatibility class
class FunctionRouter(ToolManager):
    """Legacy function router for backward compatibility."""
    
    def __init__(self, csv_loader):
        """Initialize with legacy interface."""
        config = ToolConfig()  # Use default config
        super().__init__(config, csv_loader)
    
    def get_langchain_tools(self) -> List[Tool]:
        """Get tools in legacy format."""
        return super().get_langchain_tools()
    
    def execute_tool(self, tool_name: str, *args, **kwargs) -> str:
        """Execute tool and return string result for legacy compatibility."""
        result = super().execute_tool(tool_name, *args, **kwargs)
        return result.result
    
    def create_tool_usage_prompt(self) -> str:
        """Create tool usage prompt for legacy compatibility."""
        tools = self.get_available_tools()
        if not tools:
            return "No tools are currently available."
        
        prompt_parts = [
            "You have access to the following tools for analyzing CSV data:",
            ""
        ]
        
        for tool_name in tools:
            if tool_name in self._tools:
                tool = self._tools[tool_name]
                prompt_parts.append(f"- {tool_name}: {tool.description}")
        
        prompt_parts.extend([
            "",
            "Use these tools to answer questions about the CSV data.",
            "Only use tools when you need specific information from the dataset.",
            "Always base your answers on the actual data, not assumptions."
        ])
        
        return "\n".join(prompt_parts) 