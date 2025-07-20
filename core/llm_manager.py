"""
LLM Manager Module

This module handles LLM initialization and management for different providers.
"""

from typing import Optional, Dict, Any
from langchain_openai import ChatOpenAI
from langchain_core.language_models.base import BaseLanguageModel
import os

from models.config import LLMConfig, LLMProvider
from models.schemas import CSVQuestionClassification


class LLMManager:
    """
    Manages LLM initialization and configuration.
    
    Supports multiple LLM providers and handles structured output generation.
    """
    
    def __init__(self, config: LLMConfig):
        """
        Initialize the LLM manager.
        
        Args:
            config (LLMConfig): LLM configuration
        """
        self.config = config
        self._llm: Optional[BaseLanguageModel] = None
        self._structured_llm: Optional[BaseLanguageModel] = None
        self._initialize_llm()
    
    def _initialize_llm(self) -> None:
        """Initialize the LLM based on configuration."""
        api_key = self.config.api_key or self._get_api_key()
        
        if not api_key:
            raise ValueError(
                f"API key required for {self.config.provider}. "
                "Set it in config or environment variable."
            )
        
        if self.config.provider == LLMProvider.OPENAI:
            self._llm = ChatOpenAI(
                api_key=api_key,
                model=self.config.model_name,
                temperature=self.config.temperature,
                max_tokens=self.config.max_tokens,
                base_url=self.config.api_base
            )
        else:
            raise ValueError(f"Unsupported LLM provider: {self.config.provider}")
        
        # Create structured LLM for classification tasks
        # Use function_calling method to avoid warnings with gpt-3.5-turbo
        self._structured_llm = self._llm.with_structured_output(CSVQuestionClassification, method="function_calling")
    
    def _get_api_key(self) -> Optional[str]:
        """Get API key from environment variables."""
        if self.config.provider == LLMProvider.OPENAI:
            return os.getenv("OPENAI_API_KEY")
        return None
    
    def get_llm(self) -> BaseLanguageModel:
        """
        Get the main LLM instance.
        
        Returns:
            BaseLanguageModel: The LLM instance
        """
        return self._llm
    
    def get_structured_llm(self) -> BaseLanguageModel:
        """
        Get the structured LLM for classification tasks.
        
        Returns:
            BaseLanguageModel: The structured LLM instance
        """
        return self._structured_llm
    

    
    def update_config(self, new_config: LLMConfig) -> None:
        """
        Update LLM configuration and reinitialize.
        
        Args:
            new_config (LLMConfig): New configuration
        """
        self.config = new_config
        self._initialize_llm() 