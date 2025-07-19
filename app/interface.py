"""
Application Interface Module

This module provides the user interface layer for the CSV agent application.
"""

import os
from typing import Optional
from rich.console import Console
from rich.prompt import Prompt, Confirm
from rich.panel import Panel
from rich.markdown import Markdown
from rich.table import Table
from rich import print as rprint

from agents.csv_agent import CSVAgent
from models.config import AgentConfig
from models.schemas import DatasetMetadata


class CSVAgentInterface:
    """
    User interface for the CSV agent application.
    
    Provides CLI interactions and display formatting.
    """
    
    def __init__(self, config: AgentConfig):
        """
        Initialize the interface.
        
        Args:
            config (AgentConfig): Agent configuration
        """
        self.console = Console()
        self.agent = CSVAgent(config)
    
    def load_csv_file(self, file_path: str) -> bool:
        """
        Load a CSV file with user feedback.
        
        Args:
            file_path (str): Path to CSV file
            
        Returns:
            bool: True if successful
        """
        if not os.path.exists(file_path):
            self.console.print(f"[red]File not found: {file_path}[/red]")
            return False
        
        self.console.print(f"[blue]Loading CSV file: {file_path}[/blue]")
        
        result = self.agent.load_csv(file_path)
        
        if result.success:
            self.console.print(f"[green]✓ Successfully loaded {result.metadata.file_name}[/green]")
            self._display_data_summary(result.metadata)
            return True
        else:
            self.console.print(f"[red]✗ Failed to load CSV: {result.message}[/red]")
            return False
    
    def _display_data_summary(self, metadata: DatasetMetadata) -> None:
        """Display a summary of the loaded data."""
        table = Table(title="Dataset Summary")
        table.add_column("Property", style="cyan")
        table.add_column("Value", style="magenta")
        
        table.add_row("File Name", metadata.file_name)
        table.add_row("Rows", str(metadata.shape[0]))
        table.add_row("Columns", str(metadata.shape[1]))
        table.add_row("Memory Usage", f"{metadata.memory_usage / 1024:.2f} KB")
        
        # Show column names (first 5)
        columns_str = ", ".join(metadata.columns[:5])
        if len(metadata.columns) > 5:
            columns_str += f" ... ({len(metadata.columns)} total)"
        table.add_row("Columns", columns_str)
        
        self.console.print(table)
    
    def ask_question(self, question: str) -> None:
        """
        Ask a question and display the response.
        
        Args:
            question (str): User's question
        """
        self.console.print(f"\n[blue]Question:[/blue] {question}")
        
        with self.console.status("[bold blue]Thinking..."):
            response = self.agent.ask_question(question)
        
        if response.is_csv_related:
            # Create panel for the answer
            answer_panel = Panel(
                Markdown(response.answer),
                title="[green]Answer[/green]",
                border_style="green"
            )
            self.console.print(answer_panel)
            
            # Show metadata if available
            if response.used_tools:
                self.console.print(f"[dim]Tools used: {', '.join(response.used_tools)}[/dim]")
            
            if response.follow_up:
                self.console.print("[dim]💡 This appears to be a follow-up question[/dim]")
        else:
            # Question not related to CSV
            self.console.print(f"[yellow]ℹ️  {response.answer}[/yellow]")
    
    def run_interactive_mode(self) -> None:
        """Run interactive question-answering session."""
        # Check if CSV is loaded
        status = self.agent.get_status()
        if not status.csv_loaded:
            self.console.print("[yellow]No CSV file loaded. Please load a CSV file first.[/yellow]")
            return
        
        self.console.print(Panel(
            "[bold green]Interactive CSV Analysis Mode[/bold green]\n\n"
            "Ask questions about your CSV data. Type 'quit' to exit.\n"
            "Type 'help' for available commands.",
            title="CSV Analysis Agent"
        ))
        
        while True:
            try:
                question = Prompt.ask("\n[cyan]Your question")
                
                if question.lower() in ['quit', 'exit', 'q']:
                    self.console.print("[yellow]Goodbye! 👋[/yellow]")
                    break
                elif question.lower() == 'help':
                    self._show_help()
                elif question.lower() == 'suggestions':
                    self._show_suggestions()
                elif question.lower() == 'status':
                    self._show_status()
                elif question.lower() == 'clear':
                    self.agent.clear_conversation()
                    self.console.print("[green]Conversation history cleared.[/green]")
                elif question.lower() == 'tools':
                    self._show_tools()
                else:
                    self.ask_question(question)
                    
            except KeyboardInterrupt:
                self.console.print("\n[yellow]Goodbye! 👋[/yellow]")
                break
            except Exception as e:
                self.console.print(f"[red]Error: {e}[/red]")
    
    def _show_help(self) -> None:
        """Show help information."""
        help_text = """
**Available Commands:**
- `help` - Show this help message
- `suggestions` - Get question suggestions based on your data
- `status` - Show agent and data status
- `tools` - Show available analysis tools
- `clear` - Clear conversation history
- `quit` or `exit` - Exit the application

**Example Questions:**
- "What is the summary of this dataset?"
- "Tell me about the 'column_name' column"
- "What are the statistics for numeric columns?"
- "Search for rows containing 'search_term'"
- "What are the unique values in 'column_name'?"

**Tips:**
- Ask follow-up questions naturally
- Reference previous answers with "it", "that", etc.
- Be specific about column names for better results
        """
        self.console.print(Panel(Markdown(help_text), title="Help"))
    
    def _show_suggestions(self) -> None:
        """Show question suggestions."""
        suggestions = self.agent.suggest_questions()
        
        self.console.print("[bold]💡 Suggested Questions:[/bold]")
        for i, suggestion in enumerate(suggestions, 1):
            self.console.print(f"  {i}. {suggestion}")
    
    def _show_status(self) -> None:
        """Show agent status."""
        status = self.agent.get_status()
        
        table = Table(title="Agent Status")
        table.add_column("Property", style="cyan")
        table.add_column("Value", style="magenta")
        
        table.add_row("CSV Loaded", "✓" if status.csv_loaded else "✗")
        table.add_row("CSV File", status.csv_file or "None")
        table.add_row("Questions Asked", str(status.memory_summary.get("question_count", 0)))
        table.add_row("Available Tools", str(len(status.available_tools)))
        table.add_row("Memory Type", status.memory_summary.get("memory_type", "Unknown"))
        
        self.console.print(table)
    
    def _show_tools(self) -> None:
        """Show available tools."""
        tools = self.agent.get_available_tools()
        usage_stats = self.agent.get_tool_usage_stats()
        
        table = Table(title="Available Analysis Tools")
        table.add_column("Tool Name", style="cyan")
        table.add_column("Usage Count", style="magenta")
        table.add_column("Description", style="white")
        
        # Get tool descriptions from the tool manager
        tool_descriptions = {
            "get_data_summary": "Get comprehensive dataset summary",
            "get_column_info": "Get detailed column information", 
            "search_data": "Search for specific data in the dataset",
            "get_basic_stats": "Get statistical information for numeric columns",
            "get_value_counts": "Get frequency distribution for categorical columns"
        }
        
        for tool in tools:
            description = tool_descriptions.get(tool, "Analysis tool")
            usage_count = usage_stats.get(tool, 0)
            table.add_row(tool, str(usage_count), description)
        
        self.console.print(table) 