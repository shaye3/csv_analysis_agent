"""
Query Context Module

This module manages context and suggestions for CSV queries.
"""

from typing import List, Optional, Dict, Any
from data_io.csv_loader import CSVLoader


class QueryContext:
    """
    Manages query context and provides intelligent suggestions.
    
    This class helps build context for LLM queries and suggests relevant questions.
    """
    
    def __init__(self, csv_loader: CSVLoader):
        """
        Initialize query context manager.
        
        Args:
            csv_loader (CSVLoader): CSV loader instance
        """
        self.csv_loader = csv_loader
    
    def get_context_for_classification(self) -> str:
        """
        Get context string for question classification.
        
        Returns:
            str: Context string describing the current dataset
        """
        if not self.csv_loader.is_loaded():
            return "No CSV data is currently loaded."
        
        metadata = self.csv_loader.get_metadata()
        if not metadata:
            return "CSV loaded but metadata unavailable."
        
        context_parts = [
            f"Currently loaded CSV file: {metadata.file_name}",
            f"Number of rows: {metadata.shape[0]}",
            f"Number of columns: {metadata.shape[1]}",
            f"Column names: {', '.join(metadata.columns)}",
        ]
        
        # Add sample data types (first 5 columns)
        sample_dtypes = list(metadata.dtypes.items())[:5]
        if sample_dtypes:
            dtype_info = ', '.join([f"{col}({dtype})" for col, dtype in sample_dtypes])
            context_parts.append(f"Sample data types: {dtype_info}")
        
        return "\n".join(context_parts)
    
    def suggest_questions(self) -> List[str]:
        """
        Suggest relevant questions based on the loaded data.
        
        Returns:
            List[str]: List of suggested questions
        """
        if not self.csv_loader.is_loaded():
            return ["Please load a CSV file first to get question suggestions."]
        
        metadata = self.csv_loader.get_metadata()
        if not metadata:
            return ["Dataset loaded but unable to generate suggestions."]
        
        suggestions = [
            "What is the summary of this dataset?",
            "How many rows and columns are in the data?",
            "What are the column names and their data types?",
        ]
        
        # Add column-specific suggestions
        if metadata.columns:
            first_col = metadata.columns[0]
            suggestions.extend([
                f"Tell me about the '{first_col}' column",
                f"What are the unique values in '{first_col}'?",
            ])
        
        # Add suggestions for numeric columns
        numeric_columns = [
            col for col, dtype in metadata.dtypes.items() 
            if 'int' in dtype.lower() or 'float' in dtype.lower()
        ]
        
        if numeric_columns:
            suggestions.append(f"What are the statistics for '{numeric_columns[0]}'?")
        
        # Add suggestions for categorical columns
        categorical_columns = [
            col for col, dtype in metadata.dtypes.items() 
            if dtype.lower() == 'object'
        ]
        
        if categorical_columns:
            suggestions.append(f"What are the value counts for '{categorical_columns[0]}'?")
        
        # Add search suggestion if we have text columns
        if categorical_columns:
            suggestions.append("Search for specific data in the dataset")
        
        return suggestions
    
    def get_column_suggestions(self, column_name: str) -> List[str]:
        """
        Get suggestions specific to a column.
        
        Args:
            column_name (str): Name of the column
            
        Returns:
            List[str]: Column-specific suggestions
        """
        if not self.csv_loader.is_loaded():
            return []
        
        column_info = self.csv_loader.get_column_info(column_name)
        if not column_info:
            return []
        
        suggestions = [
            f"Tell me about the '{column_name}' column",
            f"What are the unique values in '{column_name}'?",
        ]
        
        # Type-specific suggestions
        if 'int' in column_info.dtype.lower() or 'float' in column_info.dtype.lower():
            suggestions.extend([
                f"What are the statistics for '{column_name}'?",
                f"What is the average value of '{column_name}'?",
                f"What is the range of values in '{column_name}'?"
            ])
        elif column_info.dtype.lower() == 'object':
            suggestions.extend([
                f"What are the most common values in '{column_name}'?",
                f"How many unique values are in '{column_name}'?",
                f"Search for specific values in '{column_name}'"
            ])
        
        return suggestions
    
    def get_dataset_overview(self) -> Dict[str, Any]:
        """
        Get a comprehensive overview of the dataset for context building.
        
        Returns:
            Dict[str, Any]: Dataset overview information
        """
        if not self.csv_loader.is_loaded():
            return {"status": "no_data_loaded"}
        
        metadata = self.csv_loader.get_metadata()
        if not metadata:
            return {"status": "metadata_unavailable"}
        
        # Categorize columns by type
        numeric_columns = []
        text_columns = []
        datetime_columns = []
        
        for col, dtype in metadata.dtypes.items():
            if 'int' in dtype.lower() or 'float' in dtype.lower():
                numeric_columns.append(col)
            elif 'datetime' in dtype.lower():
                datetime_columns.append(col)
            else:
                text_columns.append(col)
        
        return {
            "status": "loaded",
            "file_name": metadata.file_name,
            "shape": metadata.shape,
            "total_missing_values": sum(metadata.null_counts.values()),
            "memory_usage_kb": metadata.memory_usage / 1024,
            "column_types": {
                "numeric": numeric_columns,
                "text": text_columns,
                "datetime": datetime_columns
            },
            "sample_data_available": len(metadata.sample_data) > 0
        } 