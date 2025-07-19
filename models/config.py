"""
Configuration Models

This module contains Pydantic models for configuring the CSV agent system.
"""

import os
from typing import Optional, Dict, Any, List
from pydantic import BaseModel, Field
from enum import Enum


class LLMProvider(str, Enum):
    """Supported LLM providers."""
    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    LOCAL = "local"


class MemoryType(str, Enum):
    """Supported memory types."""
    BUFFER = "buffer"
    SUMMARY = "summary"
    SLIDING_WINDOW = "sliding_window"


class LLMConfig(BaseModel):
    """Configuration for LLM settings."""
    provider: LLMProvider = LLMProvider.OPENAI
    model_name: str = Field(default_factory=lambda: os.getenv("DEFAULT_MODEL", "gpt-4o-mini"))
    temperature: float = Field(default_factory=lambda: float(os.getenv("DEFAULT_TEMPERATURE", "0.1")), ge=0.0, le=1.0)
    max_tokens: Optional[int] = None
    api_key: Optional[str] = Field(default_factory=lambda: os.getenv("OPENAI_API_KEY"))
    api_base: Optional[str] = None


class MemoryConfig(BaseModel):
    """Configuration for memory settings."""
    memory_type: MemoryType = MemoryType.BUFFER
    max_token_limit: int = Field(default=4000, gt=0)  # Increased for better context retention
    max_interactions: int = Field(default=30, gt=0)  # More interactions for follow-up questions
    enable_summarization: bool = False


class ToolConfig(BaseModel):
    """Configuration for tool settings."""
    enabled_tools: List[str] = Field(default_factory=lambda: [
        "get_data_summary", "get_column_info", "sort_data", "filter_data", "group_and_aggregate",
        "get_basic_stats", "get_analytics_classification", "list_measures", "list_dimensions"
    ])
    max_search_results: int = Field(default=10, gt=0)
    enable_custom_tools: bool = True


class AgentConfig(BaseModel):
    """Main configuration for the CSV agent."""
    llm: LLMConfig = Field(default_factory=LLMConfig)
    memory: MemoryConfig = Field(default_factory=MemoryConfig)
    tools: ToolConfig = Field(default_factory=ToolConfig)
    verbose: bool = True  # Enable verbose mode by default for debugging
    max_iterations: int = Field(default=15, gt=0)  # Increased for complex follow-up questions
    
    class Config:
        """Pydantic config."""
        use_enum_values = True


class CSVLoaderConfig(BaseModel):
    """Configuration for CSV loading."""
    max_file_size_mb: float = Field(default=100.0, gt=0)
    encoding: str = "utf-8"
    delimiter: str = ","
    enable_type_inference: bool = True
    sample_size_for_inference: int = Field(default=1000, gt=0) 