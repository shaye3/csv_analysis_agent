"""
Agent Builder Module

This module contains the AgentBuilder class that composes the full agent
from LLM + tools + memory components.
"""

from typing import Optional
from langchain.agents import create_openai_tools_agent, AgentExecutor
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder

from models.config import AgentConfig
from models.schemas import AgentStatus, QueryResponse
from core.llm_manager import LLMManager
from core.memory_manager import MemoryManagerFactory, BaseMemoryManager
from core.tool_manager import ToolManager
from data_io.csv_loader import CSVLoader
from data_io.query_context import QueryContext


class AgentBuilder:
    """
    Builds and manages the complete CSV agent system.
    
    This class composes LLM, memory, tools, and context into a working agent.
    """
    
    def __init__(self, config: AgentConfig):
        """
        Initialize the agent builder.
        
        Args:
            config (AgentConfig): Complete agent configuration
        """
        self.config = config
        
        # Initialize core components
        self.llm_manager = LLMManager(config.llm)
        self.csv_loader = CSVLoader()
        self.memory_manager = MemoryManagerFactory.create_memory_manager(config.memory)
        self.tool_manager = ToolManager(config.tools, self.csv_loader)
        self.query_context = QueryContext(self.csv_loader)
        
        # Agent components
        self.agent = None
        self.agent_executor = None
        
        self._initialize_agent()
    
    def _initialize_agent(self) -> None:
        """Initialize the LangChain agent with all components."""
        # Create system prompt
        system_prompt = self._create_system_prompt()
        
        # Create prompt template
        prompt = ChatPromptTemplate.from_messages([
            ("system", system_prompt),
            MessagesPlaceholder(variable_name="chat_history"),
            ("human", "{input}"),
            MessagesPlaceholder(variable_name="agent_scratchpad"),
        ])
        
        # Get tools
        tools = self.tool_manager.get_langchain_tools()
        
        # Create agent
        self.agent = create_openai_tools_agent(
            llm=self.llm_manager.get_llm(),
            tools=tools,
            prompt=prompt
        )
        
        # Create agent executor
        self.agent_executor = AgentExecutor(
            agent=self.agent,
            tools=tools,
            memory=self.memory_manager.get_langchain_memory(),
            verbose=self.config.verbose,
            return_intermediate_steps=True,
            max_iterations=self.config.max_iterations
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
        tool_descriptions = self._create_tool_usage_prompt()
        
        return base_prompt.format(tool_descriptions=tool_descriptions)
    
    def _create_tool_usage_prompt(self) -> str:
        """Create a prompt describing available tools."""
        tools = self.tool_manager.get_available_tools()
        if not tools:
            return "No tools are currently available."
        
        prompt_parts = [
            "You have access to the following tools for analyzing CSV data:",
            ""
        ]
        
        tool_descriptions = {}
        for tool_name in tools:
            if tool_name in self.tool_manager._tools:
                tool = self.tool_manager._tools[tool_name]
                tool_descriptions[tool_name] = tool.description
        
        for tool_name, description in tool_descriptions.items():
            prompt_parts.append(f"- {tool_name}: {description}")
        
        prompt_parts.extend([
            "",
            "Use these tools to answer questions about the CSV data.",
            "Only use tools when you need specific information from the dataset.",
            "Always base your answers on the actual data, not assumptions."
        ])
        
        return "\n".join(prompt_parts)
    
    def query(self, question: str) -> QueryResponse:
        """
        Process a query using the complete agent system.
        
        Args:
            question (str): User's question
            
        Returns:
            QueryResponse: Complete response with metadata
        """
        # Check if CSV is loaded
        if not self.csv_loader.is_loaded():
            return QueryResponse(
                answer="No CSV file is currently loaded. Please load a CSV file first.",
                is_csv_related=False,
                used_tools=[],
                follow_up=False
            )
        
        # Check if question is CSV-related
        csv_context = self.query_context.get_context_for_classification()
        classification = self.llm_manager.classify_question(question, csv_context)
        
        if not classification.is_csv_related:
            return QueryResponse(
                answer="I can only answer questions about the loaded CSV data. Please ask questions related to your dataset, such as asking about columns, statistics, or searching for specific data.",
                is_csv_related=False,
                used_tools=[],
                follow_up=False,
                metadata={"classification_reasoning": classification.reasoning}
            )
        
        # Detect follow-up
        is_follow_up = self.memory_manager.is_follow_up_question(question)
        
        try:
            # Execute query through agent
            response = self.agent_executor.invoke({
                "input": question,
                "chat_history": self.memory_manager.get_langchain_memory().chat_memory.messages
            })
            
            answer = response.get("output", "I couldn't generate a response.")
            
            # Extract used tools
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
                    "classification_reasoning": classification.reasoning
                }
            )
            
            return QueryResponse(
                answer=answer,
                is_csv_related=True,
                used_tools=used_tools,
                follow_up=is_follow_up,
                metadata={
                    "classification_reasoning": classification.reasoning,
                    "execution_metadata": response
                }
            )
            
        except Exception as e:
            error_message = f"Error processing question: {str(e)}"
            return QueryResponse(
                answer=error_message,
                is_csv_related=True,
                used_tools=[],
                follow_up=is_follow_up,
                metadata={"error": str(e)}
            )
    
    def get_status(self) -> AgentStatus:
        """Get current agent status."""
        return AgentStatus(
            csv_loaded=self.csv_loader.is_loaded(),
            csv_file=self.csv_loader.get_current_file(),
            memory_summary=self.memory_manager.get_memory_summary(),
            available_tools=self.tool_manager.get_available_tools(),
            is_initialized=self.agent is not None
        )
    
    def clear_conversation(self) -> None:
        """Clear conversation memory."""
        self.memory_manager.clear_memory()
    
    def suggest_questions(self) -> list[str]:
        """Suggest relevant questions based on loaded data."""
        if not self.csv_loader.is_loaded():
            return ["Please load a CSV file first to get question suggestions."]
        
        return self.query_context.suggest_questions() 