"""
CSV QA Agent Module (Legacy)

This module provides backward compatibility with the old CSVQAAgent interface.
For new projects, use agents.csv_agent.CSVAgent instead.
"""

import warnings
from typing import Optional, Dict, Any, List
from agents.csv_agent import CSVAgent
from models.config import AgentConfig, LLMConfig

# Issue deprecation warning
warnings.warn(
    "CSVQAAgent is deprecated. Use agents.csv_agent.CSVAgent instead.",
    DeprecationWarning,
    stacklevel=2
)


class CSVQAAgent:
    """
    Legacy CSV Question Answering Agent.
    
    This is a compatibility wrapper around the new CSVAgent.
    For new projects, use agents.csv_agent.CSVAgent directly.
    """
    
    def __init__(
        self,
        openai_api_key: Optional[str] = None,
        model_name: str = "gpt-3.5-turbo",
        temperature: float = 0.1,
        memory_type: str = "buffer"
    ):
        """
        Initialize the CSV QA Agent.
        
        Args:
            openai_api_key (Optional[str]): OpenAI API key
            model_name (str): Name of the LLM model to use
            temperature (float): Temperature setting for the LLM
            memory_type (str): Type of memory to use
        """
        # Create configuration for new agent
        config = AgentConfig(
            llm=LLMConfig(
                model_name=model_name,
                temperature=temperature,
                api_key=openai_api_key
            )
        )
        
        # Initialize new agent
        self._agent = CSVAgent(config)
        
        # Expose components for backward compatibility
        self.csv_loader = self._agent.csv_loader
        self.memory_manager = self._agent.memory_manager
        self.function_router = self._agent.tool_manager  # Note: renamed in new version
    
    def _create_system_prompt(self) -> str:
        """Create the system prompt for the agent."""
        base_prompt = """You are a helpful AI assistant specialized in analyzing CSV data. Your primary role is to answer questions about the currently loaded CSV dataset using only the information available in that dataset.

IMPORTANT RULES:
1. ONLY answer questions related to the loaded CSV data
2. If no CSV is loaded, inform the user they need to load a CSV file first
3. If a question is not related to the CSV data, politely decline and redirect to CSV-related questions
4. Use the available tools to gather information from the CSV before answering
5. Be precise and factual - only state what you can verify from the actual data
6. If you don't have enough information to answer a question, say so and suggest what data would be needed

TOOLS AVAILABLE:
{tool_descriptions}

CONVERSATION GUIDELINES:
- Maintain context from previous questions in the conversation
- If a user asks a follow-up question, consider the previous context
- Provide clear, concise answers with specific data from the CSV
- When appropriate, suggest additional analysis that might be helpful
- Always validate that data exists before making claims about it

Remember: You are an expert data analyst who only works with the provided CSV data. Stay focused on helping users understand their specific dataset."""
        
        # Add tool descriptions
        tool_descriptions = self.function_router.create_tool_usage_prompt()
        
        return base_prompt.format(tool_descriptions=tool_descriptions)
    
    def load_csv(self, file_path: str, **kwargs) -> Dict[str, Any]:
        """Load a CSV file for analysis."""
        result = self._agent.load_csv(file_path, **kwargs)
        return {
            "success": result.success,
            "message": result.message,
            "metadata": result.metadata.__dict__ if result.metadata else None
        }
    
    def ask_question(self, question: str) -> Dict[str, Any]:
        """Ask a question about the CSV data."""
        response = self._agent.ask_question(question)
        return {
            "answer": response.answer,
            "is_csv_related": response.is_csv_related,
            "used_tools": response.used_tools,
            "follow_up": response.follow_up
        }
    
    # Legacy compatibility methods - delegate to new agent
    def get_data_summary(self) -> Optional[str]:
        """Get a summary of the currently loaded data."""
        return self._agent.get_data_summary()
    
    def get_available_tools(self) -> List[str]:
        """Get list of available analysis tools."""
        return self._agent.get_available_tools()
    
    def get_conversation_history(self) -> str:
        """Get the conversation history."""
        return self._agent.get_conversation_history()
    
    def clear_conversation(self) -> None:
        """Clear the conversation history."""
        self._agent.clear_conversation()
    
    def get_agent_status(self) -> Dict[str, Any]:
        """Get the current status of the agent."""
        status = self._agent.get_status()
        return {
            "csv_loaded": status.csv_loaded,
            "csv_file": status.csv_file,
            "memory_summary": status.memory_summary,
            "available_tools": status.available_tools,
            "is_initialized": status.is_initialized
        }
    
    def execute_tool_directly(self, tool_name: str, *args, **kwargs) -> str:
        """Execute a tool directly without going through the agent."""
        return self._agent.execute_tool_directly(tool_name, *args, **kwargs)
    
    def suggest_questions(self) -> List[str]:
        """Suggest relevant questions based on the loaded data."""
        return self._agent.suggest_questions() 