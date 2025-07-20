"""
Pydantic Schemas

This module contains all Pydantic models for data validation and API schemas.
"""

from typing import Optional, Dict, Any, List, Union
from pydantic import BaseModel, Field
from datetime import datetime
from enum import Enum


class ColumnType(str, Enum):
    """Classification of column types for analytics."""
    MEASURE = "measure"
    DIMENSION = "dimension"


class ColumnAnalysisResult(BaseModel):
    """Schema for LLM column analysis result."""
    description: str = Field(description="Clear description of what the column represents")
    column_type: ColumnType = Field(description="Classification as measure or dimension") 
    rationale: str = Field(description="Explanation for the measure/dimension classification")


class CSVQuestionClassification(BaseModel):
    """Pydantic model for CSV question classification response."""
    
    is_csv_related: bool = Field(
        description="True if the question is related to analyzing the CSV dataset, False otherwise"
    )
    reasoning: str = Field(
        description="Brief explanation of why the question is or isn't CSV-related"
    )


class ColumnInfo(BaseModel):
    """Schema for column information."""
    name: str
    dtype: str
    null_count: int
    unique_count: int
    sample_values: List[Any]
    description: str
    column_type: ColumnType


class DatasetMetadata(BaseModel):
    """Schema for dataset metadata."""
    file_path: str
    file_name: str
    shape: tuple[int, int]
    columns: List[str]
    dtypes: Dict[str, str]
    memory_usage: int
    null_counts: Dict[str, int]
    sample_data: List[Dict[str, Any]]


class QueryResponse(BaseModel):
    """Schema for query responses."""
    answer: str
    is_csv_related: bool
    used_tools: List[str]
    metadata: Optional[Dict[str, Any]] = None
    timestamp: datetime = Field(default_factory=datetime.now)


class AgentStatus(BaseModel):
    """Schema for agent status."""
    csv_loaded: bool
    csv_file: Optional[str]
    memory_summary: Dict[str, Any]
    available_tools: List[str]
    is_initialized: bool


class LoadCSVResult(BaseModel):
    """Schema for CSV loading results."""
    success: bool
    message: str
    metadata: Optional[DatasetMetadata]


class ConversationEntry(BaseModel):
    """Schema for conversation entries."""
    timestamp: datetime
    human_message: str
    ai_response: str
    metadata: Dict[str, Any] = Field(default_factory=dict)


class ToolExecutionResult(BaseModel):
    """Schema for tool execution results."""
    tool_name: str
    success: bool
    result: str
    execution_time: float
    metadata: Dict[str, Any] = Field(default_factory=dict) 