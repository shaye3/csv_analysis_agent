"""
Memory Manager Module

This module contains the MemoryManager class responsible for managing
conversation history and enabling follow-up questions in the CSV QA Agent.
"""

from typing import List, Dict, Any, Optional
from langchain.memory import ConversationBufferMemory, ConversationSummaryMemory
from langchain.schema import BaseMessage, HumanMessage, AIMessage
from langchain_core.chat_history import BaseChatMessageHistory
from langchain_core.messages import BaseMessage as CoreBaseMessage
import json
from datetime import datetime


class MemoryManager:
    """
    Manages conversation memory and context for the CSV QA Agent.
    
    This class handles storing and retrieving conversation history,
    enabling the agent to understand follow-up questions and maintain context.
    """
    
    def __init__(self, memory_type: str = "buffer", max_token_limit: int = 2000):
        """
        Initialize the memory manager.
        
        Args:
            memory_type (str): Type of memory to use ("buffer" or "summary")
            max_token_limit (int): Maximum token limit for memory
        """
        self.memory_type = memory_type
        self.max_token_limit = max_token_limit
        self._conversation_history: List[Dict[str, Any]] = []
        self._session_metadata: Dict[str, Any] = {
            "start_time": datetime.now().isoformat(),
            "question_count": 0,
            "csv_file": None
        }
        
        # Initialize LangChain memory
        if memory_type == "summary":
            # Note: This would require an LLM for summarization
            # For now, we'll use buffer memory
            self._langchain_memory = ConversationBufferMemory(
                return_messages=True,
                memory_key="chat_history"
            )
        else:
            self._langchain_memory = ConversationBufferMemory(
                return_messages=True,
                memory_key="chat_history"
            )
    
    def add_interaction(self, human_message: str, ai_response: str, metadata: Optional[Dict[str, Any]] = None) -> None:
        """
        Add a human-AI interaction to memory.
        
        Args:
            human_message (str): The human's question/input
            ai_response (str): The AI's response
            metadata (Optional[Dict[str, Any]]): Additional metadata about the interaction
        """
        # Add to our internal history
        interaction = {
            "timestamp": datetime.now().isoformat(),
            "human_message": human_message,
            "ai_response": ai_response,
            "metadata": metadata or {}
        }
        self._conversation_history.append(interaction)
        
        # Add to LangChain memory
        self._langchain_memory.chat_memory.add_user_message(human_message)
        self._langchain_memory.chat_memory.add_ai_message(ai_response)
        
        # Update session metadata
        self._session_metadata["question_count"] += 1
        
        # Manage memory size
        self._manage_memory_size()
    
    def _manage_memory_size(self) -> None:
        """Manage memory size to prevent it from growing too large."""
        # Simple implementation: keep only last N interactions
        max_interactions = 20
        
        if len(self._conversation_history) > max_interactions:
            # Remove oldest interactions
            removed_count = len(self._conversation_history) - max_interactions
            self._conversation_history = self._conversation_history[removed_count:]
            
            # Also clear and rebuild LangChain memory
            messages = []
            for interaction in self._conversation_history[-10:]:  # Keep last 10 for LangChain
                messages.extend([
                    HumanMessage(content=interaction["human_message"]),
                    AIMessage(content=interaction["ai_response"])
                ])
            
            # Clear and rebuild
            self._langchain_memory.clear()
            for message in messages:
                if isinstance(message, HumanMessage):
                    self._langchain_memory.chat_memory.add_user_message(message.content)
                elif isinstance(message, AIMessage):
                    self._langchain_memory.chat_memory.add_ai_message(message.content)
    
    def get_conversation_context(self) -> str:
        """
        Get the conversation context as a formatted string.
        
        Returns:
            str: Formatted conversation context
        """
        if not self._conversation_history:
            return "No previous conversation."
        
        context_parts = ["Previous conversation:"]
        
        # Include last few interactions
        recent_interactions = self._conversation_history[-5:]  # Last 5 interactions
        
        for i, interaction in enumerate(recent_interactions, 1):
            context_parts.extend([
                f"\nQ{i}: {interaction['human_message']}",
                f"A{i}: {interaction['ai_response'][:200]}..." if len(interaction['ai_response']) > 200 else f"A{i}: {interaction['ai_response']}"
            ])
        
        return "\n".join(context_parts)
    
    def get_langchain_memory(self) -> ConversationBufferMemory:
        """
        Get the LangChain memory object.
        
        Returns:
            ConversationBufferMemory: The LangChain memory instance
        """
        return self._langchain_memory
    
    def get_recent_questions(self, count: int = 3) -> List[str]:
        """
        Get recent questions from the conversation.
        
        Args:
            count (int): Number of recent questions to retrieve
            
        Returns:
            List[str]: List of recent questions
        """
        recent_interactions = self._conversation_history[-count:]
        return [interaction["human_message"] for interaction in recent_interactions]
    
    def set_csv_context(self, csv_file: str, csv_summary: str) -> None:
        """
        Set the current CSV context for the session.
        
        Args:
            csv_file (str): Name of the loaded CSV file
            csv_summary (str): Summary of the CSV data
        """
        self._session_metadata["csv_file"] = csv_file
        self._session_metadata["csv_summary"] = csv_summary
        
        # Add initial context to memory
        context_message = f"I'm now analyzing the CSV file: {csv_file}\n\nData summary:\n{csv_summary}"
        self._langchain_memory.chat_memory.add_ai_message(context_message)
    
    def get_csv_context(self) -> Optional[Dict[str, Any]]:
        """
        Get the current CSV context.
        
        Returns:
            Optional[Dict[str, Any]]: CSV context information or None if no CSV is loaded
        """
        if not self._session_metadata.get("csv_file"):
            return None
        
        return {
            "csv_file": self._session_metadata["csv_file"],
            "csv_summary": self._session_metadata.get("csv_summary", ""),
            "question_count": self._session_metadata["question_count"]
        }
    
    def is_follow_up_question(self, question: str) -> bool:
        """
        Determine if a question is likely a follow-up to previous questions.
        
        Args:
            question (str): The current question
            
        Returns:
            bool: True if it appears to be a follow-up question
        """
        if not self._conversation_history:
            return False
        
        # Simple heuristics for follow-up detection
        follow_up_indicators = [
            "also", "too", "and", "what about", "how about", 
            "can you", "tell me more", "explain", "why",
            "that", "this", "it", "them", "those", "these"
        ]
        
        question_lower = question.lower()
        
        # Check for pronouns and follow-up words
        for indicator in follow_up_indicators:
            if indicator in question_lower:
                return True
        
        # Check if question is short (often indicates follow-up)
        if len(question.split()) < 5:
            return True
        
        return False
    
    def get_memory_summary(self) -> Dict[str, Any]:
        """
        Get a summary of the current memory state.
        
        Returns:
            Dict[str, Any]: Memory summary information
        """
        return {
            "total_interactions": len(self._conversation_history),
            "session_start": self._session_metadata["start_time"],
            "question_count": self._session_metadata["question_count"],
            "csv_file": self._session_metadata.get("csv_file"),
            "memory_type": self.memory_type,
            "has_context": len(self._conversation_history) > 0
        }
    
    def clear_memory(self) -> None:
        """Clear all conversation memory."""
        self._conversation_history.clear()
        self._langchain_memory.clear()
        self._session_metadata = {
            "start_time": datetime.now().isoformat(),
            "question_count": 0,
            "csv_file": None
        }
    
    def export_conversation(self) -> str:
        """
        Export the conversation history as JSON.
        
        Returns:
            str: JSON string of the conversation history
        """
        export_data = {
            "session_metadata": self._session_metadata,
            "conversation_history": self._conversation_history
        }
        return json.dumps(export_data, indent=2)
    
    def import_conversation(self, json_data: str) -> bool:
        """
        Import conversation history from JSON.
        
        Args:
            json_data (str): JSON string containing conversation history
            
        Returns:
            bool: True if import was successful, False otherwise
        """
        try:
            data = json.loads(json_data)
            self._session_metadata = data.get("session_metadata", {})
            self._conversation_history = data.get("conversation_history", [])
            
            # Rebuild LangChain memory
            self._langchain_memory.clear()
            for interaction in self._conversation_history:
                self._langchain_memory.chat_memory.add_user_message(interaction["human_message"])
                self._langchain_memory.chat_memory.add_ai_message(interaction["ai_response"])
            
            return True
        except Exception as e:
            print(f"Error importing conversation: {str(e)}")
            return False 