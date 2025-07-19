"""
Enhanced CSV Loader Module

This module contains the enhanced CSVLoader class for loading and managing CSV data.
"""

import pandas as pd
import os
from typing import Optional, Dict, Any, List
from pathlib import Path

from models.config import CSVLoaderConfig
from models.schemas import DatasetMetadata, ColumnInfo


class CSVLoader:
    """
    Enhanced CSV loader with configuration support and better metadata handling.
    
    Handles CSV file loading, validation, and provides structured access to data.
    """
    
    def __init__(self, config: Optional[CSVLoaderConfig] = None):
        """
        Initialize the CSV loader.
        
        Args:
            config (Optional[CSVLoaderConfig]): Loader configuration
        """
        self.config = config or CSVLoaderConfig()
        self._dataframe: Optional[pd.DataFrame] = None
        self._file_path: Optional[str] = None
        self._metadata: Optional[DatasetMetadata] = None
    
    def load_csv(self, file_path: str, **kwargs) -> bool:
        """
        Load a CSV file with validation and configuration.
        
        Args:
            file_path (str): Path to the CSV file
            **kwargs: Additional arguments for pd.read_csv()
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            # Validate file
            self._validate_file(file_path)
            
            # Prepare read arguments
            read_kwargs = {
                'encoding': self.config.encoding,
                'delimiter': self.config.delimiter,
                **kwargs
            }
            
            # Load the CSV
            self._dataframe = pd.read_csv(file_path, **read_kwargs)
            self._file_path = file_path
            
            # Generate metadata
            self._generate_metadata()
            
            return True
            
        except Exception as e:
            print(f"Error loading CSV: {str(e)}")
            return False
    
    def _validate_file(self, file_path: str) -> None:
        """Validate file before loading."""
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")
        
        if not file_path.lower().endswith('.csv'):
            raise ValueError("File must have .csv extension")
        
        # Check file size
        file_size_mb = os.path.getsize(file_path) / (1024 * 1024)
        if file_size_mb > self.config.max_file_size_mb:
            raise ValueError(f"File too large: {file_size_mb:.2f}MB > {self.config.max_file_size_mb}MB")
    
    def _generate_metadata(self) -> None:
        """Generate comprehensive metadata about the loaded CSV."""
        if self._dataframe is None:
            return
        
        # Convert dtypes to strings for serialization
        dtypes_dict = {col: str(dtype) for col, dtype in self._dataframe.dtypes.items()}
        
        self._metadata = DatasetMetadata(
            file_path=self._file_path,
            file_name=Path(self._file_path).name if self._file_path else "unknown",
            shape=self._dataframe.shape,
            columns=list(self._dataframe.columns),
            dtypes=dtypes_dict,
            memory_usage=int(self._dataframe.memory_usage(deep=True).sum()),
            null_counts={col: int(count) for col, count in self._dataframe.isnull().sum().items()},
            sample_data=self._dataframe.head(3).to_dict('records') if len(self._dataframe) > 0 else []
        )
    
    def get_dataframe(self) -> Optional[pd.DataFrame]:
        """Get the loaded DataFrame."""
        return self._dataframe
    
    def get_metadata(self) -> Optional[DatasetMetadata]:
        """Get dataset metadata."""
        return self._metadata
    
    def get_column_info(self, column_name: str) -> Optional[ColumnInfo]:
        """
        Get detailed information about a specific column.
        
        Args:
            column_name (str): Name of the column
            
        Returns:
            Optional[ColumnInfo]: Column information or None if not found
        """
        if self._dataframe is None or column_name not in self._dataframe.columns:
            return None
        
        series = self._dataframe[column_name]
        
        return ColumnInfo(
            name=column_name,
            dtype=str(series.dtype),
            null_count=int(series.isnull().sum()),
            unique_count=int(series.nunique()),
            sample_values=series.dropna().unique()[:10].tolist(),
            description=self._infer_column_description(column_name, series)
        )
    
    def _infer_column_description(self, column_name: str, series: pd.Series) -> str:
        """Infer description for a column based on name and data."""
        name_lower = column_name.lower()
        
        # Pattern matching for common column types
        patterns = {
            'id': ['id', '_id', 'identifier'],
            'name': ['name', 'title'],
            'date': ['date', 'time'],
            'email': ['email'],
            'price': ['price', 'cost', 'amount'],
            'age': ['age']
        }
        
        for pattern_type, keywords in patterns.items():
            if any(keyword in name_lower for keyword in keywords):
                if pattern_type == 'id':
                    return "Unique identifier column"
                elif pattern_type == 'name':
                    return "Name/title column containing text values"
                elif pattern_type == 'date':
                    return "Date/time column"
                elif pattern_type == 'email':
                    return "Email address column"
                elif pattern_type == 'price':
                    return "Monetary value column"
                elif pattern_type == 'age':
                    return "Age column (numeric)"
        
        # General type-based descriptions
        if series.dtype == 'object':
            if series.nunique() < len(series) * 0.1:
                return f"Categorical column with {series.nunique()} unique values"
            else:
                return "Text column"
        elif pd.api.types.is_numeric_dtype(series):
            return f"Numeric column (range: {series.min():.2f} to {series.max():.2f})"
        else:
            return f"Column of type {series.dtype}"
    
    def get_data_summary(self) -> str:
        """Get human-readable data summary."""
        if not self.is_loaded():
            return "No data loaded."
        
        summary_parts = [
            f"Dataset: {self._metadata.file_name}",
            f"Shape: {self._metadata.shape[0]} rows × {self._metadata.shape[1]} columns",
            f"Columns: {', '.join(self._metadata.columns)}",
            f"Memory usage: {self._metadata.memory_usage / 1024:.2f} KB"
        ]
        
        # Add missing data info
        total_nulls = sum(self._metadata.null_counts.values())
        if total_nulls > 0:
            summary_parts.append(f"Missing values: {total_nulls} total")
        
        return "\n".join(summary_parts)
    
    def search_data(self, query: str, columns: Optional[List[str]] = None) -> pd.DataFrame:
        """
        Search for data containing the query string.
        
        Args:
            query (str): Search query
            columns (Optional[List[str]]): Specific columns to search
            
        Returns:
            pd.DataFrame: Filtered dataframe with matching rows
        """
        if not self.is_loaded():
            return pd.DataFrame()
        
        search_columns = columns if columns else self._dataframe.select_dtypes(include=['object']).columns.tolist()
        
        mask = pd.Series([False] * len(self._dataframe))
        
        for col in search_columns:
            if col in self._dataframe.columns:
                mask |= self._dataframe[col].astype(str).str.contains(query, case=False, na=False)
        
        return self._dataframe[mask]
    
    def is_loaded(self) -> bool:
        """Check if data is currently loaded."""
        return self._dataframe is not None
    
    def get_current_file(self) -> Optional[str]:
        """Get current file path."""
        return self._file_path
    
    def clear(self) -> None:
        """Clear loaded data and reset."""
        self._dataframe = None
        self._file_path = None
        self._metadata = None 