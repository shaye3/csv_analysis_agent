"""
Agent Manager Module

This module contains the AgentManager class for high-level agent operations.
"""

from typing import Optional
from langchain_core.language_models.base import BaseLanguageModel

from models.schemas import CSVQuestionClassification


class AgentManager:
    """
    Manages high-level agent operations and query processing.
    
    This class handles query classification and agent coordination tasks.
    """
    
    def __init__(self, structured_llm: BaseLanguageModel):
        """
        Initialize the agent manager.
        
        Args:
            structured_llm (BaseLanguageModel): LLM instance configured for structured output
        """
        self.structured_llm = structured_llm
    
    def is_query_in_scope(self, question: str, conversation_history: str = "") -> CSVQuestionClassification:
        """
        Determine if a query is within the scope of CSV data analysis.
        
        Args:
            question (str): The user's question
            conversation_history (str): Full conversation context for pronouns/references
            
        Returns:
            CSVQuestionClassification: Classification result
        """
        # Build context section
        context_section = ""
        if conversation_history.strip():
            context_section = f"FULL CONVERSATION HISTORY:\n{conversation_history}\n\n"
        
        prompt = f"""You are a data analysis expert. Your task is to determine if a user's CURRENT/LAST question is related to analyzing a CSV dataset or if it's a general question unrelated to data analysis.

{context_section}CURRENT USER QUESTION: "{question}"

CRITICAL INSTRUCTIONS:
- Focus ONLY on whether the CURRENT/LAST question "{question}" is about CSV data analysis
- The question might be a follow-up to previous questions in the conversation
- Consider the conversation context to understand pronouns, references, and follow-up nature
- Even if it's a follow-up question with pronouns like "it", "that", "them", classify based on whether it relates to data analysis

GUIDELINES FOR CSV-RELATED QUESTIONS (is_csv_related = True):
- Analyzing, summarizing, or describing CSV data
- Asking about specific columns, rows, or values in datasets
- Statistical analysis, distributions, or patterns in data
- Searching, filtering, or finding specific information in data
- Comparisons or relationships within datasets
- Data quality, missing values, or data characteristics
- Questions that reference data elements, even indirectly through context
- Follow-up questions about previously discussed data analysis topics

GUIDELINES FOR NON-CSV QUESTIONS (is_csv_related = False):
- General knowledge not related to data analysis
- Requests for explanations of concepts unrelated to the data
- Questions about external information not in CSV datasets
- Programming help unrelated to analyzing datasets
- Personal questions or general conversation
- Questions about non-data topics

IMPORTANT: Even very short questions like "What about it?", "Tell me more", "Why?" can be CSV-related if they follow up on data analysis topics. Use the conversation context to determine the true intent.

Analyze the CURRENT question and provide your classification with reasoning."""

        return self.structured_llm.invoke(prompt)
