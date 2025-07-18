"""
CSV Loader Module

This module contains the CSVLoader class responsible for loading, parsing,
and managing CSV data for the CSV QA Agent system.
"""

import pandas as pd
import os
from typing import Optional, Dict, Any, List
from pathlib import Path


class CSVLoader:
    """
    Handles CSV file loading, parsing, and data management.
    
    This class provides functionality to load CSV files, validate them,
    and provide structured access to the data for the QA agent.
    """
    
    def __init__(self):
        """Initialize the CSV loader."""
        self._dataframe: Optional[pd.DataFrame] = None
        self._file_path: Optional[str] = None
        self._metadata: Dict[str, Any] = {}
    
    def load_csv(self, file_path: str, **kwargs) -> bool:
        """
        Load a CSV file into memory.
        
        Args:
            file_path (str): Path to the CSV file
            **kwargs: Additional arguments to pass to pd.read_csv()
            
        Returns:
            bool: True if loading was successful, False otherwise
            
        Raises:
            FileNotFoundError: If the file doesn't exist
            ValueError: If the file is not a valid CSV
        """
        try:
            # Validate file exists
            if not os.path.exists(file_path):
                raise FileNotFoundError(f"File not found: {file_path}")
            
            # Validate file extension
            if not file_path.lower().endswith('.csv'):
                raise ValueError("File must have .csv extension")
            
            # Load the CSV
            self._dataframe = pd.read_csv(file_path, **kwargs)
            self._file_path = file_path
            
            # Generate metadata
            self._generate_metadata()
            
            return True
            
        except Exception as e:
            print(f"Error loading CSV: {str(e)}")
            return False
    
    def _generate_metadata(self) -> None:
        """Generate metadata about the loaded CSV."""
        if self._dataframe is None:
            return
        
        self._metadata = {
            'file_path': self._file_path,
            'file_name': Path(self._file_path).name if self._file_path else None,
            'shape': self._dataframe.shape,
            'columns': list(self._dataframe.columns),
            'dtypes': self._dataframe.dtypes.to_dict(),
            'memory_usage': self._dataframe.memory_usage(deep=True).sum(),
            'null_counts': self._dataframe.isnull().sum().to_dict(),
            'sample_data': self._dataframe.head(3).to_dict('records') if len(self._dataframe) > 0 else []
        }
    
    def get_dataframe(self) -> Optional[pd.DataFrame]:
        """
        Get the loaded DataFrame.
        
        Returns:
            Optional[pd.DataFrame]: The loaded DataFrame or None if no data is loaded
        """
        return self._dataframe
    
    def get_metadata(self) -> Dict[str, Any]:
        """
        Get metadata about the loaded CSV.
        
        Returns:
            Dict[str, Any]: Metadata dictionary
        """
        return self._metadata.copy()
    
    def get_column_info(self, column_name: str) -> Optional[Dict[str, Any]]:
        """
        Get detailed information about a specific column.
        
        Args:
            column_name (str): Name of the column
            
        Returns:
            Optional[Dict[str, Any]]: Column information or None if column doesn't exist
        """
        if self._dataframe is None or column_name not in self._dataframe.columns:
            return None
        
        series = self._dataframe[column_name]
        
        return {
            'name': column_name,
            'dtype': str(series.dtype),
            'null_count': int(series.isnull().sum()),
            'unique_count': int(series.nunique()),
            'sample_values': series.dropna().unique()[:10].tolist(),
            'description': self._infer_column_description(column_name, series)
        }
    
    def _infer_column_description(self, column_name: str, series: pd.Series) -> str:
        """
        Infer a description for a column based on its name and data.
        
        Args:
            column_name (str): Name of the column
            series (pd.Series): The column data
            
        Returns:
            str: Inferred description
        """
        name_lower = column_name.lower()
        
        # Common patterns
        if any(keyword in name_lower for keyword in ['id', '_id', 'identifier']):
            return f"Unique identifier column"
        elif any(keyword in name_lower for keyword in ['name', 'title']):
            return f"Name/title column containing text values"
        elif any(keyword in name_lower for keyword in ['date', 'time']):
            return f"Date/time column"
        elif any(keyword in name_lower for keyword in ['email']):
            return f"Email address column"
        elif any(keyword in name_lower for keyword in ['price', 'cost', 'amount']):
            return f"Monetary value column"
        elif any(keyword in name_lower for keyword in ['age']):
            return f"Age column (numeric)"
        elif series.dtype == 'object':
            if series.nunique() < len(series) * 0.1:
                return f"Categorical column with {series.nunique()} unique values"
            else:
                return f"Text column"
        elif pd.api.types.is_numeric_dtype(series):
            return f"Numeric column (range: {series.min():.2f} to {series.max():.2f})"
        else:
            return f"Column of type {series.dtype}"
    
    def get_data_summary(self) -> str:
        """
        Get a human-readable summary of the loaded data.
        
        Returns:
            str: Summary of the data
        """
        if self._dataframe is None:
            return "No data loaded."
        
        summary_parts = [
            f"Dataset: {self._metadata.get('file_name', 'Unknown')}",
            f"Shape: {self._metadata['shape'][0]} rows × {self._metadata['shape'][1]} columns",
            f"Columns: {', '.join(self._metadata['columns'])}",
            f"Memory usage: {self._metadata['memory_usage'] / 1024:.2f} KB"
        ]
        
        # Add info about missing data
        total_nulls = sum(self._metadata['null_counts'].values())
        if total_nulls > 0:
            summary_parts.append(f"Missing values: {total_nulls} total")
        
        return "\n".join(summary_parts)
    
    def search_data(self, query: str, columns: Optional[List[str]] = None) -> pd.DataFrame:
        """
        Search for data containing the query string.
        
        Args:
            query (str): Search query
            columns (Optional[List[str]]): Specific columns to search in
            
        Returns:
            pd.DataFrame: Filtered dataframe with matching rows
        """
        if self._dataframe is None:
            return pd.DataFrame()
        
        search_columns = columns if columns else self._dataframe.select_dtypes(include=['object']).columns.tolist()
        
        # Create a boolean mask for rows containing the query
        mask = pd.Series([False] * len(self._dataframe))
        
        for col in search_columns:
            if col in self._dataframe.columns:
                mask |= self._dataframe[col].astype(str).str.contains(query, case=False, na=False)
        
        return self._dataframe[mask]
    
    def is_loaded(self) -> bool:
        """
        Check if data is currently loaded.
        
        Returns:
            bool: True if data is loaded, False otherwise
        """
        return self._dataframe is not None
    
    def clear(self) -> None:
        """Clear the loaded data and reset the loader."""
        self._dataframe = None
        self._file_path = None
        self._metadata = {} 