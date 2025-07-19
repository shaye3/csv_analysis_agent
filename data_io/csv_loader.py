"""
Enhanced CSV Loader Module

This module contains the enhanced CSVLoader class for loading and managing CSV data.
"""

import pandas as pd
import os
from typing import Optional, Dict, Any, List
from pathlib import Path
from langchain_core.language_models import BaseLanguageModel

from models.config import CSVLoaderConfig
from models.schemas import DatasetMetadata, ColumnInfo, ColumnType, ColumnAnalysisResult


class CSVLoader:
    """
    Enhanced CSV loader with configuration support and better metadata handling.
    
    Handles CSV file loading, validation, and provides structured access to data.
    """
    
    def __init__(self, config: Optional[CSVLoaderConfig] = None, llm: Optional[BaseLanguageModel] = None):
        """
        Initialize the CSV loader.
        
        Args:
            config (Optional[CSVLoaderConfig]): Loader configuration
            llm (Optional[BaseLanguageModel]): LLM instance for intelligent column descriptions
        """
        self.config = config or CSVLoaderConfig()
        self.llm = llm
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
        
        # Get LLM analysis including description and measure/dimension classification
        description, column_type, rationale = self._analyze_column_with_llm(column_name, series)
        
        return ColumnInfo(
            name=column_name,
            dtype=str(series.dtype),
            null_count=int(series.isnull().sum()),
            unique_count=int(series.nunique()),
            sample_values=series.dropna().unique()[:10].tolist(),
            description=description,
            column_type=column_type
        )
    
    def _analyze_column_with_llm(self, column_name: str, series: pd.Series) -> tuple[str, ColumnType, str]:
        """Analyze column with LLM to get description and classification."""
        
        # Use LLM for intelligent analysis if available
        if self.llm is not None:
            return self._generate_llm_column_description(column_name, series)
        
        # Simple fallback when no LLM is available
        if pd.api.types.is_numeric_dtype(series) and not column_name.lower().endswith('id'):
            description = f"Numeric column (range: {series.min():.2f} to {series.max():.2f})"
            column_type = ColumnType.MEASURE
            rationale = "Numeric field suitable for aggregation"
        else:
            description = f"Text column with {series.nunique()} unique values"
            column_type = ColumnType.DIMENSION
            rationale = "Categorical field suitable for grouping"
            
        return (description, column_type, rationale)
    
    def _generate_llm_column_description(self, column_name: str, series: pd.Series) -> tuple[str, ColumnType, str]:
        """Generate intelligent column description and classification using LLM."""
        try:
            # Create structured LLM that returns our analysis model
            structured_llm = self.llm.with_structured_output(ColumnAnalysisResult)
            
            # Prepare context about the entire dataset
            dataset_context = self._prepare_dataset_context()
            
            # Prepare specific column information
            column_stats = self._prepare_column_statistics(series)
            
            # Create comprehensive prompt for measure/dimension classification
            prompt = f"""You are a data analyst expert. Analyze the following column from a CSV dataset and classify it as either a MEASURE or DIMENSION, along with providing a clear description.

DEFINITIONS:
- MEASURE: Numerical fields that can be aggregated, summed, averaged, or mathematically analyzed. Examples: sales, revenue, quantity, price, score, count, rating, amount.
- DIMENSION: Categorical fields used to describe, group, filter, or slice data. Examples: country, department, product category, date, gender, name, ID, status.

DATASET CONTEXT:
{dataset_context}

COLUMN TO ANALYZE:
- Column Name: "{column_name}"
- Data Type: {series.dtype}
- Total Values: {len(series)}
- Non-null Values: {series.count()}
- Unique Values: {series.nunique()}

COLUMN STATISTICS:
{column_stats}

SAMPLE VALUES (first 10 non-null):
{', '.join(map(str, series.dropna().head(10).tolist()))}

CLASSIFICATION GUIDELINES:
1. MEASURE if:
   - Numeric values that represent quantities, amounts, or metrics
   - Values that make sense to sum, average, or aggregate
   - Examples: salary, sales, temperature, count, score, revenue

2. DIMENSION if:
   - Categorical values used for grouping or filtering
   - Identifiers, names, codes, or categories
   - Date/time fields (used for time-based grouping)
   - Text fields representing categories or labels
   - Even numeric fields if they're IDs or categorical codes

INSTRUCTIONS:
- Provide a clear description of what this column represents (under 150 characters)
- Classify as MEASURE or DIMENSION based on its analytical purpose
- Explain your reasoning for the classification
- Consider how this column would typically be used in data analysis"""

            # Get structured LLM response
            analysis_result: ColumnAnalysisResult = structured_llm.invoke(prompt)
            
            return (
                analysis_result.description,
                analysis_result.column_type,
                analysis_result.rationale
            )
            
        except Exception as e:
            print(f"Error generating LLM analysis for column '{column_name}': {e}")
            # Simple fallback when LLM fails
            description = f"Column '{column_name}' - {series.dtype} type"
            
            # Basic heuristic for classification
            if pd.api.types.is_numeric_dtype(series) and not column_name.lower().endswith('id'):
                column_type = ColumnType.MEASURE
                rationale = "Numeric field suitable for aggregation"
            else:
                column_type = ColumnType.DIMENSION
                rationale = "Categorical field suitable for grouping"
            
            return (description, column_type, rationale)
    
    def _prepare_dataset_context(self) -> str:
        """Prepare context about the entire dataset for LLM analysis."""
        if self._metadata is None:
            return "Unknown dataset"
        
        context_parts = [
            f"Dataset: {self._metadata.file_name}",
            f"Size: {self._metadata.shape[0]} rows × {self._metadata.shape[1]} columns",
            f"All columns: {', '.join(self._metadata.columns)}"
        ]
        
        return "\n".join(context_parts)
    
    def _prepare_column_statistics(self, series: pd.Series) -> str:
        """Prepare statistical information about the column."""
        stats = []
        
        if pd.api.types.is_numeric_dtype(series):
            stats.extend([
                f"Min: {series.min():.2f}" if not pd.isna(series.min()) else "Min: N/A",
                f"Max: {series.max():.2f}" if not pd.isna(series.max()) else "Max: N/A",
                f"Mean: {series.mean():.2f}" if not pd.isna(series.mean()) else "Mean: N/A",
                f"Median: {series.median():.2f}" if not pd.isna(series.median()) else "Median: N/A"
            ])
        elif series.dtype == 'object':
            # For text columns, show value distribution
            value_counts = series.value_counts().head(5)
            if len(value_counts) > 0:
                stats.append("Top values: " + ", ".join([f"'{val}' ({count})" for val, count in value_counts.items()]))
        
        # Missing data info
        null_count = series.isnull().sum()
        if null_count > 0:
            stats.append(f"Missing values: {null_count} ({null_count/len(series)*100:.1f}%)")
        
        return "; ".join(stats) if stats else "No additional statistics available"
    

    
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
    
    def get_measures(self) -> List[str]:
        """
        Get all columns classified as measures.
        
        Returns:
            List[str]: List of measure column names
        """
        if not self.is_loaded():
            return []
        
        measures = []
        for column in self._dataframe.columns:
            column_info = self.get_column_info(column)
            if column_info and column_info.column_type == ColumnType.MEASURE:
                measures.append(column)
        return measures
    
    def get_dimensions(self) -> List[str]:
        """
        Get all columns classified as dimensions.
        
        Returns:
            List[str]: List of dimension column names
        """
        if not self.is_loaded():
            return []
        
        dimensions = []
        for column in self._dataframe.columns:
            column_info = self.get_column_info(column)
            if column_info and column_info.column_type == ColumnType.DIMENSION:
                dimensions.append(column)
        return dimensions
    
    def get_analytics_summary(self) -> Dict[str, Any]:
        """
        Get analytics summary with measures and dimensions.
        
        Returns:
            Dict[str, Any]: Summary of analytical structure
        """
        if not self.is_loaded():
            return {"measures": [], "dimensions": [], "summary": "No data loaded"}
        
        measures = self.get_measures()
        dimensions = self.get_dimensions()
        
        return {
            "measures": measures,
            "dimensions": dimensions,
            "measure_count": len(measures),
            "dimension_count": len(dimensions),
            "total_columns": len(self._dataframe.columns),
            "summary": f"Dataset has {len(measures)} measures and {len(dimensions)} dimensions"
        }

    def clear(self) -> None:
        """Clear loaded data and reset."""
        self._dataframe = None
        self._file_path = None
        self._metadata = None 