"""
Memory Manager Module

This module contains enhanced memory management classes for the CSV Analysis Agent.
"""

from typing import List, Dict, Any, Optional
from langchain.memory import ConversationBufferMemory
from abc import ABC, abstractmethod
from datetime import datetime

from models.config import MemoryConfig, MemoryType
from models.schemas import ConversationEntry


class BaseMemoryManager(ABC):
    """Abstract base class for memory managers."""
    
    @abstractmethod
    def add_interaction(self, human_message: str, ai_response: str, metadata: Optional[Dict[str, Any]] = None) -> None:
        """Add a human-AI interaction to memory."""
        pass
    
    @abstractmethod
    def get_conversation_context(self) -> str:
        """Get conversation context as formatted string."""
        pass
    
    @abstractmethod
    def clear_memory(self) -> None:
        """Clear all memory."""
        pass
    
    @abstractmethod
    def get_langchain_memory(self) -> ConversationBufferMemory:
        """Get LangChain memory object."""
        pass


class BufferMemoryManager(BaseMemoryManager):
    """Buffer-based memory manager that keeps recent interactions."""
    
    def __init__(self, config: MemoryConfig):
        """Initialize buffer memory manager."""
        self.config = config
        self._conversation_history: List[ConversationEntry] = []
        self._session_metadata: Dict[str, Any] = {
            "start_time": datetime.now().isoformat(),
            "question_count": 0,
            "csv_file": None
        }
        
        self._langchain_memory = ConversationBufferMemory(
            return_messages=True,
            memory_key="chat_history"
        )
    
    def add_interaction(self, human_message: str, ai_response: str, metadata: Optional[Dict[str, Any]] = None) -> None:
        """Add interaction to buffer memory."""
        entry = ConversationEntry(
            timestamp=datetime.now(),
            human_message=human_message,
            ai_response=ai_response,
            metadata=metadata or {}
        )
        
        self._conversation_history.append(entry)
        self._langchain_memory.chat_memory.add_user_message(human_message)
        self._langchain_memory.chat_memory.add_ai_message(ai_response)
        
        self._session_metadata["question_count"] += 1
        self._manage_memory_size()
    
    def _manage_memory_size(self) -> None:
        """Manage memory size to prevent overflow."""
        if len(self._conversation_history) > self.config.max_interactions:
            # Remove oldest interactions
            removed_count = len(self._conversation_history) - self.config.max_interactions
            self._conversation_history = self._conversation_history[removed_count:]
            
            # Rebuild LangChain memory with recent interactions
            self._rebuild_langchain_memory()
    
    def _rebuild_langchain_memory(self) -> None:
        """Rebuild LangChain memory from recent interactions."""
        self._langchain_memory.clear()
        
        recent_interactions = self._conversation_history[-10:]  # Keep last 10
        for entry in recent_interactions:
            self._langchain_memory.chat_memory.add_user_message(entry.human_message)
            self._langchain_memory.chat_memory.add_ai_message(entry.ai_response)
    
    def get_conversation_context(self) -> str:
        """Get formatted conversation context."""
        if not self._conversation_history:
            return "No previous conversation."
        
        context_parts = ["Previous conversation:"]
        recent_interactions = self._conversation_history[-5:]
        
        for i, entry in enumerate(recent_interactions, 1):
            context_parts.extend([
                f"\nQ{i}: {entry.human_message}",
                f"A{i}: {entry.ai_response[:200]}..." if len(entry.ai_response) > 200 else f"A{i}: {entry.ai_response}"
            ])
        
        return "\n".join(context_parts)
    
    def get_langchain_memory(self) -> ConversationBufferMemory:
        """Get LangChain memory object."""
        return self._langchain_memory
    
    def clear_memory(self) -> None:
        """Clear all memory."""
        self._conversation_history.clear()
        self._langchain_memory.clear()
        self._session_metadata = {
            "start_time": datetime.now().isoformat(),
            "question_count": 0,
            "csv_file": None
        }
    
    def set_csv_context(self, csv_file: str, csv_summary: str) -> None:
        """Set CSV context."""
        self._session_metadata["csv_file"] = csv_file
        self._session_metadata["csv_summary"] = csv_summary
        
        context_message = f"Analyzing CSV file: {csv_file}\n\nData summary:\n{csv_summary}"
        self._langchain_memory.chat_memory.add_ai_message(context_message)
    
    def get_memory_summary(self) -> Dict[str, Any]:
        """Get memory summary."""
        return {
            "total_interactions": len(self._conversation_history),
            "session_start": self._session_metadata["start_time"],
            "question_count": self._session_metadata["question_count"],
            "csv_file": self._session_metadata.get("csv_file"),
            "memory_type": "buffer",
            "has_context": len(self._conversation_history) > 0
        }
    
    def is_follow_up_question(self, question: str) -> bool:
        """Determine if question is a follow-up."""
        if not self._conversation_history:
            return False
        
        follow_up_indicators = [
            "also", "too", "and", "what about", "how about", 
            "can you", "tell me more", "explain", "why",
            "that", "this", "it", "them", "those", "these"
        ]
        
        question_lower = question.lower()
        
        for indicator in follow_up_indicators:
            if indicator in question_lower:
                return True
        
        return len(question.split()) < 5


class MemoryManagerFactory:
    """Factory for creating memory managers."""
    
    @staticmethod
    def create_memory_manager(config: MemoryConfig) -> BaseMemoryManager:
        """
        Create a memory manager based on configuration.
        
        Args:
            config (MemoryConfig): Memory configuration
            
        Returns:
            BaseMemoryManager: Memory manager instance
        """
        if config.memory_type == MemoryType.BUFFER:
            return BufferMemoryManager(config)
        elif config.memory_type == MemoryType.SUMMARY:
            # For now, return buffer memory - can implement summary later
            return BufferMemoryManager(config)
        else:
            raise ValueError(f"Unsupported memory type: {config.memory_type}")


 