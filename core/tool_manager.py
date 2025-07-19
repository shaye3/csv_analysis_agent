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

# Removed visualization components for simplified interface


class GroupAggregateInput(BaseModel):
    """Input schema for group and aggregate tool."""
    group_by_columns: str = Field(description="Comma-separated list of columns to group by")
    aggregations: str = Field(description="Comma-separated list in format 'column:operation' where operation is sum/average/count_distinct")


class SortDataInput(BaseModel):
    """Input schema for sort data tool."""
    sort_columns: str = Field(description="Comma-separated list of columns to sort by")
    sort_orders: str = Field(description="Comma-separated list of sort orders ('asc' or 'desc') matching the sort columns", default="asc")


class FilterDataInput(BaseModel):
    """Input schema for filter data tool."""
    column_name: str = Field(description="Name of the column to filter by")
    values: str = Field(description="Comma-separated list of values to filter by")


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
            available_columns = self.csv_loader.get_metadata().columns
            return f"Column '{column_name}' not found. Available columns: {', '.join(available_columns)}"
        
        info_parts = [
            f"Column: {column_info.name}",
            f"Description: {column_info.description}",
            f"Data Type: {column_info.dtype}",
            f"Missing Values: {column_info.null_count} ({column_info.null_count/self.csv_loader.get_dataframe().shape[0]*100:.1f}%)",
            f"Unique Values: {column_info.unique_count}",
            f"Sample Values: {', '.join(map(str, column_info.sample_values[:5]))}"
        ]
        
        return "\n".join(info_parts)





class SortDataTool(CSVAnalysisTool):
    """Tool to sort CSV data by specified columns."""
    
    name: str = "sort_data"
    description: str = """Sort CSV data by one or more columns with specified order.
    Parameters: 
    - sort_columns (required): comma-separated list of columns to sort by
    - sort_orders (optional): comma-separated list of 'asc' or 'desc' orders (defaults to 'asc' if not specified)
    Examples: 
    - sort_data('salary', 'desc') - sort by salary descending
    - sort_data('department,salary', 'asc,desc') - sort by department ascending, then salary descending
    - sort_data('age,salary,name', 'desc,desc,asc') - sort by age desc, salary desc, name asc"""
    
    def execute(self, sort_columns: str, sort_orders: str = "asc") -> str:
        """Sort data by specified columns."""
        if not self.validate_csv_loaded():
            return "No CSV data is currently loaded. Please load a CSV file first."
        
        df = self.csv_loader.get_dataframe()
        
        # Parse sort columns
        if not sort_columns.strip():
            return "Please provide columns to sort by (comma-separated list)."
        
        sort_cols = [col.strip() for col in sort_columns.split(',')]
        sort_cols = [col for col in sort_cols if col]  # Remove empty values
        
        if not sort_cols:
            return "No valid sort columns provided."
        
        # Validate sort columns exist
        missing_cols = [col for col in sort_cols if col not in df.columns]
        if missing_cols:
            available_columns = ', '.join(df.columns)
            return f"Sort columns not found: {', '.join(missing_cols)}. Available columns: {available_columns}"
        
        # Parse sort orders
        sort_order_list = [order.strip().lower() for order in sort_orders.split(',')]
        sort_order_list = [order for order in sort_order_list if order]  # Remove empty values
        
        # Validate sort orders
        valid_orders = ['asc', 'desc']
        invalid_orders = [order for order in sort_order_list if order not in valid_orders]
        if invalid_orders:
            return f"Invalid sort orders: {', '.join(invalid_orders)}. Use 'asc' or 'desc'."
        
        # If fewer sort orders than columns, pad with 'asc'
        while len(sort_order_list) < len(sort_cols):
            sort_order_list.append('asc')
        
        # Convert to boolean list for pandas (True = ascending, False = descending)
        ascending_list = [order == 'asc' for order in sort_order_list[:len(sort_cols)]]
        
        # Perform the sorting
        try:
            sorted_df = df.sort_values(by=sort_cols, ascending=ascending_list)
            
            if sorted_df.empty:
                return "No data found after sorting."
            
            # Format the results
            result_count = len(sorted_df)
            max_rows = 50
            
            # Create sort description
            sort_desc = []
            for col, order in zip(sort_cols, sort_order_list[:len(sort_cols)]):
                sort_desc.append(f"{col} ({order})")
            
            result_text = f"Data sorted by: {', '.join(sort_desc)}\n"
            result_text += f"Total rows: {result_count}\n\n"
            
            if result_count > max_rows:
                result_text += sorted_df.head(max_rows).to_string(index=False)
                result_text += f"\n\n... and {result_count - max_rows} more rows."
            else:
                result_text += sorted_df.to_string(index=False)
            
            # Add some insights about the sorting
            if len(sort_cols) == 1 and pd.api.types.is_numeric_dtype(df[sort_cols[0]]):
                col = sort_cols[0]
                if sort_order_list[0] == 'desc':
                    result_text += f"\n\nHighest {col}: {sorted_df[col].iloc[0]}"
                    result_text += f"\nLowest {col}: {sorted_df[col].iloc[-1]}"
                else:
                    result_text += f"\n\nLowest {col}: {sorted_df[col].iloc[0]}"
                    result_text += f"\nHighest {col}: {sorted_df[col].iloc[-1]}"
            
            return result_text
            
        except Exception as e:
            return f"Error sorting data: {str(e)}"


class FilterDataTool(CSVAnalysisTool):
    """Tool to filter CSV data by column values."""
    
    name: str = "filter_data"
    description: str = """Filter CSV data by specific column values. 
    Parameters: column_name (required), values (required - comma-separated list of values to filter by).
    Examples: filter_data('department', 'Engineering,Sales'), filter_data('status', 'active,pending')"""
    
    def execute(self, column_name: str, values: str) -> str:
        """Filter data by column values."""
        if not self.validate_csv_loaded():
            return "No CSV data is currently loaded. Please load a CSV file first."
        
        df = self.csv_loader.get_dataframe()
        
        if column_name not in df.columns:
            available_columns = ', '.join(df.columns)
            return f"Column '{column_name}' not found. Available columns: {available_columns}"
        
        # Parse the values list
        if not values.strip():
            return "Please provide values to filter by (comma-separated list)."
        
        filter_values = [value.strip() for value in values.split(',')]
        filter_values = [value for value in filter_values if value]  # Remove empty values
        
        if not filter_values:
            return "No valid filter values provided."
        
        # Perform the filtering
        try:
            # Convert DataFrame column to string for comparison to handle mixed types
            filtered_df = df[df[column_name].astype(str).isin([str(v) for v in filter_values])]
            
            if filtered_df.empty:
                unique_values = df[column_name].unique()[:10]  # Show first 10 unique values
                return f"No rows found with {column_name} in {filter_values}.\nAvailable values in '{column_name}': {', '.join(map(str, unique_values))}"
            
            # Format the results
            max_rows = 20
            result_count = len(filtered_df)
            
            result_text = f"Found {result_count} rows where '{column_name}' is in {filter_values}:\n\n"
            
            if result_count > max_rows:
                result_text += filtered_df.head(max_rows).to_string(index=False)
                result_text += f"\n\n... and {result_count - max_rows} more rows."
            else:
                result_text += filtered_df.to_string(index=False)
            
            return result_text
            
        except Exception as e:
            return f"Error filtering data: {str(e)}"


class GroupAndAggregateTool(CSVAnalysisTool):
    """Tool to group data by columns and perform aggregations."""
    
    name: str = "group_and_aggregate"
    description: str = """Group data by specified columns and perform aggregations on other columns.
    Parameters: 
    - group_by_columns (required): comma-separated list of columns to group by
    - aggregations (required): comma-separated list in format 'column:operation' where operation is sum/average/count_distinct
    Examples: 
    - group_and_aggregate('department', 'salary:average,age:average')
    - group_and_aggregate('department,city', 'salary:sum,employee_id:count_distinct')
    - group_and_aggregate('education_level', 'salary:average,years_experience:average,employee_id:count_distinct')"""
    
    def execute(self, group_by_columns: str, aggregations: str) -> str:
        """Group data and perform aggregations."""
        if not self.validate_csv_loaded():
            return "No CSV data is currently loaded. Please load a CSV file first."
        
        df = self.csv_loader.get_dataframe()
        
        # Parse group by columns
        if not group_by_columns.strip():
            return "Please provide columns to group by (comma-separated list)."
        
        group_cols = [col.strip() for col in group_by_columns.split(',')]
        group_cols = [col for col in group_cols if col]  # Remove empty values
        
        if not group_cols:
            return "No valid group by columns provided."
        
        # Validate group by columns exist
        missing_cols = [col for col in group_cols if col not in df.columns]
        if missing_cols:
            available_columns = ', '.join(df.columns)
            return f"Group by columns not found: {', '.join(missing_cols)}. Available columns: {available_columns}"
        
        # Parse aggregations
        if not aggregations.strip():
            return "Please provide aggregations in format 'column:operation' (comma-separated list)."
        
        agg_dict = {}
        agg_descriptions = []
        
        try:
            agg_specs = [spec.strip() for spec in aggregations.split(',')]
            for spec in agg_specs:
                if ':' not in spec:
                    return f"Invalid aggregation format '{spec}'. Use 'column:operation' format."
                
                col, operation = spec.split(':', 1)
                col = col.strip()
                operation = operation.strip().lower()
                
                if col not in df.columns:
                    available_columns = ', '.join(df.columns)
                    return f"Aggregation column '{col}' not found. Available columns: {available_columns}"
                
                if operation == 'sum':
                    if not pd.api.types.is_numeric_dtype(df[col]):
                        return f"Cannot sum non-numeric column '{col}'. Use count_distinct instead."
                    agg_dict[col] = 'sum'
                    agg_descriptions.append(f"Sum of {col}")
                    
                elif operation == 'average' or operation == 'avg':
                    if not pd.api.types.is_numeric_dtype(df[col]):
                        return f"Cannot average non-numeric column '{col}'. Use count_distinct instead."
                    agg_dict[col] = 'mean'
                    agg_descriptions.append(f"Average of {col}")
                    
                elif operation == 'count_distinct' or operation == 'count':
                    agg_dict[col] = 'nunique'
                    agg_descriptions.append(f"Count distinct of {col}")
                    
                else:
                    return f"Invalid operation '{operation}'. Use: sum, average, or count_distinct."
        
        except Exception as e:
            return f"Error parsing aggregations: {str(e)}"
        
        if not agg_dict:
            return "No valid aggregations provided."
        
        # Perform the groupby operation
        try:
            grouped = df.groupby(group_cols).agg(agg_dict).reset_index()
            
            # Rename columns to be more descriptive
            column_renames = {}
            for col, operation in agg_dict.items():
                if operation == 'sum':
                    column_renames[col] = f"{col}_sum"
                elif operation == 'mean':
                    column_renames[col] = f"{col}_avg"
                elif operation == 'nunique':
                    column_renames[col] = f"{col}_count_distinct"
            
            grouped = grouped.rename(columns=column_renames)
            
            if grouped.empty:
                return "No data found after grouping. Check your column names and values."
            
            # Format the results
            result_count = len(grouped)
            max_rows = 50
            
            result_text = f"Grouped by: {', '.join(group_cols)}\n"
            result_text += f"Aggregations: {', '.join(agg_descriptions)}\n"
            result_text += f"Found {result_count} groups:\n\n"
            
            if result_count > max_rows:
                result_text += grouped.head(max_rows).to_string(index=False, float_format='%.2f')
                result_text += f"\n\n... and {result_count - max_rows} more groups."
            else:
                result_text += grouped.to_string(index=False, float_format='%.2f')
            
            # Add summary statistics
            if result_count > 1:
                result_text += f"\n\nSUMMARY STATISTICS:"
                for col in grouped.columns:
                    if col not in group_cols and pd.api.types.is_numeric_dtype(grouped[col]):
                        min_val = grouped[col].min()
                        max_val = grouped[col].max()
                        avg_val = grouped[col].mean()
                        result_text += f"\n• {col}: min={min_val:.2f}, max={max_val:.2f}, avg={avg_val:.2f}"
            
            return result_text
            
        except Exception as e:
            return f"Error performing groupby operation: {str(e)}"


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


# Visualization tool removed for simplified interface


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
            SortDataTool(csv_loader=self.csv_loader),
            FilterDataTool(csv_loader=self.csv_loader),
            GroupAndAggregateTool(csv_loader=self.csv_loader),
            GetBasicStatsTool(csv_loader=self.csv_loader),
            GetAnalyticsClassificationTool(csv_loader=self.csv_loader),
            ListAvailableMeasuresTool(csv_loader=self.csv_loader),
            ListAvailableDimensionsTool(csv_loader=self.csv_loader)
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
        
        # Special handling for multi-parameter tools
        if tool.name == "group_and_aggregate":
            def group_aggregate_func(group_by_columns: str, aggregations: str) -> str:
                return self._execute_tool_with_tracking(tool.name, group_by_columns, aggregations)
            
            langchain_tool = StructuredTool.from_function(
                name=tool.name,
                description=tool.description,
                func=group_aggregate_func,
                args_schema=GroupAggregateInput
            )
        elif tool.name == "sort_data":
            def sort_data_func(sort_columns: str, sort_orders: str = "asc") -> str:
                return self._execute_tool_with_tracking(tool.name, sort_columns, sort_orders)
            
            langchain_tool = StructuredTool.from_function(
                name=tool.name,
                description=tool.description,
                func=sort_data_func,
                args_schema=SortDataInput
            )
        elif tool.name == "filter_data":
            def filter_data_func(column_name: str, values: str) -> str:
                return self._execute_tool_with_tracking(tool.name, column_name, values)
            
            langchain_tool = StructuredTool.from_function(
                name=tool.name,
                description=tool.description,
                func=filter_data_func,
                args_schema=FilterDataInput
            )
        else:
            # All other tools use regular single-parameter handling
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