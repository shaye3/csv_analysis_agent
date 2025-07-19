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
        self._structured_llm = self._llm.with_structured_output(CSVQuestionClassification)
    
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
    
    def classify_question(self, question: str, csv_context: str) -> CSVQuestionClassification:
        """
        Classify if a question is related to CSV data analysis.
        
        Args:
            question (str): The user's question
            csv_context (str): Context about the current CSV dataset
            
        Returns:
            CSVQuestionClassification: Classification result
        """
        prompt = f"""You are a data analysis expert. Your task is to determine if a user's question is related to analyzing the currently loaded CSV dataset or if it's a general question unrelated to the data.

CURRENT CSV DATASET CONTEXT:
{csv_context}

USER QUESTION: "{question}"

GUIDELINES FOR CSV-RELATED QUESTIONS (is_csv_related = True):
- Analyzing, summarizing, or describing the CSV data
- Asking about specific columns, rows, or values in the dataset
- Statistical analysis, distributions, or patterns in the data
- Searching, filtering, or finding specific information in the data
- Comparisons or relationships within the dataset
- Data quality, missing values, or data characteristics
- Questions that reference column names from the dataset

GUIDELINES FOR NON-CSV QUESTIONS (is_csv_related = False):
- General knowledge not related to the specific dataset
- Requests for explanations of concepts unrelated to the data
- Questions about external information not in the CSV
- Programming help unrelated to analyzing this specific dataset
- Personal questions or general conversation

Analyze the question and provide your classification with reasoning."""

        return self._structured_llm.invoke(prompt)
    
    def update_config(self, new_config: LLMConfig) -> None:
        """
        Update LLM configuration and reinitialize.
        
        Args:
            new_config (LLMConfig): New configuration
        """
        self.config = new_config
        self._initialize_llm() 