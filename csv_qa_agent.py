"""
CSV QA Agent Module

This module contains the CSVQAAgent class which serves as the main agent
that orchestrates all components for CSV-based question answering.
"""

import os
from typing import Optional, Dict, Any, List
from langchain.agents import create_openai_tools_agent, AgentExecutor
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage

from csv_loader import CSVLoader
from memory_manager import MemoryManager
from function_router import FunctionRouter


class CSVQAAgent:
    """
    Main CSV Question Answering Agent.
    
    This class orchestrates all components (CSVLoader, MemoryManager, FunctionRouter)
    to provide an intelligent agent capable of answering questions about CSV data.
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
            openai_api_key (Optional[str]): OpenAI API key. If None, will try to get from environment
            model_name (str): Name of the LLM model to use
            temperature (float): Temperature setting for the LLM
            memory_type (str): Type of memory to use ("buffer" or "summary")
        """
        # Initialize API key
        self.api_key = openai_api_key or os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("OpenAI API key is required. Set OPENAI_API_KEY environment variable or pass it directly.")
        
        # Initialize components
        self.csv_loader = CSVLoader()
        self.memory_manager = MemoryManager(memory_type=memory_type)
        self.function_router = FunctionRouter(self.csv_loader)
        
        # Initialize LLM
        self.llm = ChatOpenAI(
            api_key=self.api_key,
            model=model_name,
            temperature=temperature
        )
        
        # Initialize agent
        self.agent = None
        self.agent_executor = None
        self._initialize_agent()
        
        # State
        self._current_csv_file = None
        self._is_initialized = False
    
    def _initialize_agent(self) -> None:
        """Initialize the LangChain agent with tools and prompts."""
        # Create the system prompt
        system_prompt = self._create_system_prompt()
        
        # Create the prompt template
        prompt = ChatPromptTemplate.from_messages([
            ("system", system_prompt),
            MessagesPlaceholder(variable_name="chat_history"),
            ("human", "{input}"),
            MessagesPlaceholder(variable_name="agent_scratchpad"),
        ])
        
        # Get tools from function router
        tools = self.function_router.get_langchain_tools()
        
        # Create the agent
        self.agent = create_openai_tools_agent(
            llm=self.llm,
            tools=tools,
            prompt=prompt
        )
        
        # Create the agent executor
        self.agent_executor = AgentExecutor(
            agent=self.agent,
            tools=tools,
            memory=self.memory_manager.get_langchain_memory(),
            verbose=True,
            return_intermediate_steps=True,
            max_iterations=5
        )
    
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
        """
        Load a CSV file for analysis.
        
        Args:
            file_path (str): Path to the CSV file
            **kwargs: Additional arguments for pandas.read_csv()
            
        Returns:
            Dict[str, Any]: Status and metadata about the loaded file
        """
        try:
            # Load the CSV
            success = self.csv_loader.load_csv(file_path, **kwargs)
            
            if not success:
                return {
                    "success": False,
                    "message": "Failed to load CSV file",
                    "metadata": None
                }
            
            # Update memory with CSV context
            metadata = self.csv_loader.get_metadata()
            summary = self.csv_loader.get_data_summary()
            
            self.memory_manager.set_csv_context(
                csv_file=metadata['file_name'],
                csv_summary=summary
            )
            
            self._current_csv_file = file_path
            self._is_initialized = True
            
            return {
                "success": True,
                "message": f"Successfully loaded {metadata['file_name']}",
                "metadata": metadata
            }
            
        except Exception as e:
            return {
                "success": False,
                "message": f"Error loading CSV: {str(e)}",
                "metadata": None
            }
    
    def ask_question(self, question: str) -> Dict[str, Any]:
        """
        Ask a question about the CSV data.
        
        Args:
            question (str): The user's question
            
        Returns:
            Dict[str, Any]: Response with answer and metadata
        """
        if not self._is_initialized:
            return {
                "answer": "No CSV file is currently loaded. Please load a CSV file first using the load_csv() method.",
                "is_csv_related": False,
                "used_tools": [],
                "follow_up": False
            }
        
        # Check if question is CSV-related
        if not self._is_csv_related_question(question):
            return {
                "answer": "I can only answer questions about the loaded CSV data. Please ask questions related to your dataset, such as asking about columns, statistics, or searching for specific data.",
                "is_csv_related": False,
                "used_tools": [],
                "follow_up": False
            }
        
        # Detect if this is a follow-up question
        is_follow_up = self.memory_manager.is_follow_up_question(question)
        
        try:
            # Use the agent to answer the question
            response = self.agent_executor.invoke({
                "input": question,
                "chat_history": self.memory_manager.get_langchain_memory().chat_memory.messages
            })
            
            answer = response.get("output", "I couldn't generate a response.")
            
            # Extract used tools from intermediate steps
            used_tools = []
            if "intermediate_steps" in response:
                for step in response["intermediate_steps"]:
                    if hasattr(step[0], 'tool') and step[0].tool:
                        used_tools.append(step[0].tool)
            
            # Add to memory
            self.memory_manager.add_interaction(
                human_message=question,
                ai_response=answer,
                metadata={
                    "used_tools": used_tools,
                    "is_follow_up": is_follow_up,
                    "csv_file": self._current_csv_file
                }
            )
            
            return {
                "answer": answer,
                "is_csv_related": True,
                "used_tools": used_tools,
                "follow_up": is_follow_up
            }
            
        except Exception as e:
            error_message = f"Error processing question: {str(e)}"
            return {
                "answer": error_message,
                "is_csv_related": True,
                "used_tools": [],
                "follow_up": is_follow_up
            }
    
    def _is_csv_related_question(self, question: str) -> bool:
        """
        Determine if a question is related to CSV data analysis.
        
        Args:
            question (str): The user's question
            
        Returns:
            bool: True if the question appears to be CSV-related
        """
        question_lower = question.lower()
        
        # CSV-related keywords
        csv_keywords = [
            'data', 'column', 'row', 'field', 'dataset', 'table',
            'statistics', 'values', 'count', 'average', 'mean',
            'median', 'sum', 'maximum', 'minimum', 'distribution',
            'search', 'find', 'filter', 'contains', 'records',
            'summary', 'overview', 'describe', 'analyze', 'analysis',
            'missing', 'null', 'unique', 'duplicate', 'total'
        ]
        
        # Check for CSV-related keywords
        for keyword in csv_keywords:
            if keyword in question_lower:
                return True
        
        # Check for column names if CSV is loaded
        if self.csv_loader.is_loaded():
            metadata = self.csv_loader.get_metadata()
            columns = [col.lower() for col in metadata.get('columns', [])]
            
            for column in columns:
                if column in question_lower:
                    return True
        
        # Check for follow-up indicators (assuming previous questions were CSV-related)
        if self.memory_manager.is_follow_up_question(question):
            return True
        
        # If none of the above, likely not CSV-related
        return False
    
    def get_data_summary(self) -> Optional[str]:
        """
        Get a summary of the currently loaded data.
        
        Returns:
            Optional[str]: Data summary or None if no data is loaded
        """
        if not self.csv_loader.is_loaded():
            return None
        
        return self.csv_loader.get_data_summary()
    
    def get_available_tools(self) -> List[str]:
        """
        Get list of available analysis tools.
        
        Returns:
            List[str]: List of available tool names
        """
        return self.function_router.get_available_tools()
    
    def get_conversation_history(self) -> str:
        """
        Get the conversation history.
        
        Returns:
            str: Formatted conversation history
        """
        return self.memory_manager.get_conversation_context()
    
    def clear_conversation(self) -> None:
        """Clear the conversation history."""
        self.memory_manager.clear_memory()
    
    def get_agent_status(self) -> Dict[str, Any]:
        """
        Get the current status of the agent.
        
        Returns:
            Dict[str, Any]: Agent status information
        """
        return {
            "csv_loaded": self.csv_loader.is_loaded(),
            "csv_file": self._current_csv_file,
            "memory_summary": self.memory_manager.get_memory_summary(),
            "available_tools": self.get_available_tools(),
            "is_initialized": self._is_initialized
        }
    
    def execute_tool_directly(self, tool_name: str, *args, **kwargs) -> str:
        """
        Execute a tool directly without going through the agent.
        
        Args:
            tool_name (str): Name of the tool to execute
            *args: Positional arguments for the tool
            **kwargs: Keyword arguments for the tool
            
        Returns:
            str: Tool execution result
        """
        return self.function_router.execute_tool(tool_name, *args, **kwargs)
    
    def suggest_questions(self) -> List[str]:
        """
        Suggest relevant questions based on the loaded data.
        
        Returns:
            List[str]: List of suggested questions
        """
        if not self.csv_loader.is_loaded():
            return ["Please load a CSV file first to get question suggestions."]
        
        metadata = self.csv_loader.get_metadata()
        columns = metadata.get('columns', [])
        
        suggestions = [
            "What is the summary of this dataset?",
            "How many rows and columns are in the data?",
            "What are the column names and their data types?",
        ]
        
        # Add column-specific suggestions
        if columns:
            suggestions.extend([
                f"Tell me about the '{columns[0]}' column",
                f"What are the unique values in '{columns[0]}'?",
            ])
            
            # Add suggestions for numeric columns
            numeric_columns = [col for col in columns if 'int' in str(metadata.get('dtypes', {}).get(col, '')) or 'float' in str(metadata.get('dtypes', {}).get(col, ''))]
            if numeric_columns:
                suggestions.append(f"What are the statistics for '{numeric_columns[0]}'?")
        
        return suggestions 