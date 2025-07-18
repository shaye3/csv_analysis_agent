"""
Main Application Module

This module contains the main application class and CLI interface
for the CSV QA Agent system.
"""

import os
import sys
from typing import Optional
import typer
from rich.console import Console
from rich.prompt import Prompt, Confirm
from rich.panel import Panel
from rich.markdown import Markdown
from rich.table import Table
from rich import print as rprint
from dotenv import load_dotenv

from csv_qa_agent import CSVQAAgent

# Load environment variables
load_dotenv()

# Initialize Rich console
console = Console()

app = typer.Typer(help="CSV QA Agent - Intelligent CSV Analysis Assistant")


class CSVQAApplication:
    """
    Main application class for the CSV QA Agent system.
    
    This class provides a high-level interface for interacting with
    the CSV analysis agent through various interfaces (CLI, programmatic).
    """
    
    def __init__(self, openai_api_key: Optional[str] = None):
        """
        Initialize the application.
        
        Args:
            openai_api_key (Optional[str]): OpenAI API key
        """
        self.agent: Optional[CSVQAAgent] = None
        self.api_key = openai_api_key
        self._initialize_agent()
    
    def _initialize_agent(self) -> bool:
        """
        Initialize the CSV QA Agent.
        
        Returns:
            bool: True if initialization was successful
        """
        try:
            self.agent = CSVQAAgent(openai_api_key=self.api_key)
            return True
        except ValueError as e:
            console.print(f"[red]Error initializing agent: {e}[/red]")
            console.print("[yellow]Please set your OpenAI API key in the OPENAI_API_KEY environment variable.[/yellow]")
            return False
        except Exception as e:
            console.print(f"[red]Unexpected error initializing agent: {e}[/red]")
            return False
    
    def load_csv_file(self, file_path: str) -> bool:
        """
        Load a CSV file into the agent.
        
        Args:
            file_path (str): Path to the CSV file
            
        Returns:
            bool: True if loading was successful
        """
        if not self.agent:
            console.print("[red]Agent not initialized![/red]")
            return False
        
        if not os.path.exists(file_path):
            console.print(f"[red]File not found: {file_path}[/red]")
            return False
        
        console.print(f"[blue]Loading CSV file: {file_path}[/blue]")
        
        result = self.agent.load_csv(file_path)
        
        if result["success"]:
            metadata = result["metadata"]
            console.print(f"[green]✓ Successfully loaded {metadata['file_name']}[/green]")
            
            # Display summary
            self._display_data_summary(metadata)
            return True
        else:
            console.print(f"[red]✗ Failed to load CSV: {result['message']}[/red]")
            return False
    
    def _display_data_summary(self, metadata: dict) -> None:
        """Display a summary of the loaded data."""
        table = Table(title="Dataset Summary")
        table.add_column("Property", style="cyan")
        table.add_column("Value", style="magenta")
        
        table.add_row("File Name", metadata.get('file_name', 'Unknown'))
        table.add_row("Rows", str(metadata['shape'][0]))
        table.add_row("Columns", str(metadata['shape'][1]))
        table.add_row("Memory Usage", f"{metadata['memory_usage'] / 1024:.2f} KB")
        
        # Show column names
        columns_str = ", ".join(metadata['columns'][:5])
        if len(metadata['columns']) > 5:
            columns_str += f" ... ({len(metadata['columns'])} total)"
        table.add_row("Columns", columns_str)
        
        console.print(table)
    
    def ask_question(self, question: str) -> None:
        """
        Ask a question to the agent and display the response.
        
        Args:
            question (str): The user's question
        """
        if not self.agent:
            console.print("[red]Agent not initialized![/red]")
            return
        
        console.print(f"\n[blue]Question:[/blue] {question}")
        
        with console.status("[bold blue]Thinking..."):
            response = self.agent.ask_question(question)
        
        # Display the answer
        if response["is_csv_related"]:
            # Create a panel for the answer
            answer_panel = Panel(
                Markdown(response["answer"]),
                title="[green]Answer[/green]",
                border_style="green"
            )
            console.print(answer_panel)
            
            # Show metadata if verbose
            if response["used_tools"]:
                console.print(f"[dim]Tools used: {', '.join(response['used_tools'])}[/dim]")
            
            if response["follow_up"]:
                console.print("[dim]💡 This appears to be a follow-up question[/dim]")
        else:
            # Question not related to CSV
            console.print(f"[yellow]ℹ️  {response['answer']}[/yellow]")
    
    def interactive_mode(self) -> None:
        """Start interactive question-answering mode."""
        if not self.agent:
            console.print("[red]Agent not initialized![/red]")
            return
        
        # Check if CSV is loaded
        status = self.agent.get_agent_status()
        if not status["csv_loaded"]:
            console.print("[yellow]No CSV file loaded. Please load a CSV file first.[/yellow]")
            return
        
        console.print(Panel(
            "[bold green]Interactive CSV QA Mode[/bold green]\n\n"
            "Ask questions about your CSV data. Type 'quit' to exit.\n"
            "Type 'help' for suggestions.",
            title="CSV QA Agent"
        ))
        
        while True:
            try:
                question = Prompt.ask("\n[cyan]Your question")
                
                if question.lower() in ['quit', 'exit', 'q']:
                    console.print("[yellow]Goodbye! 👋[/yellow]")
                    break
                elif question.lower() == 'help':
                    self._show_help()
                elif question.lower() == 'suggestions':
                    self._show_suggestions()
                elif question.lower() == 'status':
                    self._show_status()
                elif question.lower() == 'clear':
                    self.agent.clear_conversation()
                    console.print("[green]Conversation history cleared.[/green]")
                else:
                    self.ask_question(question)
                    
            except KeyboardInterrupt:
                console.print("\n[yellow]Goodbye! 👋[/yellow]")
                break
    
    def _show_help(self) -> None:
        """Show help information."""
        help_text = """
**Available Commands:**
- `help` - Show this help message
- `suggestions` - Get question suggestions based on your data
- `status` - Show agent and data status
- `clear` - Clear conversation history
- `quit` or `exit` - Exit the application

**Example Questions:**
- "What is the summary of this dataset?"
- "Tell me about the 'column_name' column"
- "What are the statistics for numeric columns?"
- "Search for rows containing 'search_term'"
- "What are the unique values in 'column_name'?"
        """
        console.print(Panel(Markdown(help_text), title="Help"))
    
    def _show_suggestions(self) -> None:
        """Show question suggestions."""
        if not self.agent:
            return
        
        suggestions = self.agent.suggest_questions()
        
        console.print("[bold]💡 Suggested Questions:[/bold]")
        for i, suggestion in enumerate(suggestions, 1):
            console.print(f"  {i}. {suggestion}")
    
    def _show_status(self) -> None:
        """Show agent status."""
        if not self.agent:
            return
        
        status = self.agent.get_agent_status()
        
        table = Table(title="Agent Status")
        table.add_column("Property", style="cyan")
        table.add_column("Value", style="magenta")
        
        table.add_row("CSV Loaded", "✓" if status["csv_loaded"] else "✗")
        table.add_row("CSV File", status.get("csv_file", "None"))
        table.add_row("Questions Asked", str(status["memory_summary"]["question_count"]))
        table.add_row("Available Tools", str(len(status["available_tools"])))
        
        console.print(table)


# CLI Commands

@app.command()
def interactive(
    csv_file: Optional[str] = typer.Option(None, "--csv", "-c", help="CSV file to load"),
    api_key: Optional[str] = typer.Option(None, "--api-key", help="OpenAI API key")
):
    """Start interactive CSV QA session."""
    console.print(Panel("[bold blue]CSV QA Agent[/bold blue]\nIntelligent CSV Analysis Assistant", 
                       title="Welcome"))
    
    # Initialize application
    app_instance = CSVQAApplication(openai_api_key=api_key)
    
    if not app_instance.agent:
        return
    
    # Load CSV if provided
    if csv_file:
        if not app_instance.load_csv_file(csv_file):
            return
    else:
        # Prompt for CSV file
        csv_file = Prompt.ask("Enter path to CSV file")
        if not app_instance.load_csv_file(csv_file):
            return
    
    # Start interactive mode
    app_instance.interactive_mode()


@app.command()
def analyze(
    csv_file: str = typer.Argument(..., help="CSV file to analyze"),
    question: str = typer.Argument(..., help="Question to ask about the data"),
    api_key: Optional[str] = typer.Option(None, "--api-key", help="OpenAI API key")
):
    """Analyze CSV file with a single question."""
    app_instance = CSVQAApplication(openai_api_key=api_key)
    
    if not app_instance.agent:
        return
    
    # Load CSV
    if not app_instance.load_csv_file(csv_file):
        return
    
    # Ask question
    app_instance.ask_question(question)


@app.command()
def info(
    csv_file: str = typer.Argument(..., help="CSV file to get info about")
):
    """Get basic information about a CSV file."""
    if not os.path.exists(csv_file):
        console.print(f"[red]File not found: {csv_file}[/red]")
        return
    
    # Create a simple loader to get metadata
    from csv_loader import CSVLoader
    loader = CSVLoader()
    
    if loader.load_csv(csv_file):
        metadata = loader.get_metadata()
        app_instance = CSVQAApplication()
        app_instance._display_data_summary(metadata)
        
        # Show column details
        console.print("\n[bold]Column Details:[/bold]")
        for col in metadata['columns'][:10]:  # Show first 10 columns
            info = loader.get_column_info(col)
            if info:
                console.print(f"• {col}: {info['description']}")
    else:
        console.print(f"[red]Failed to load CSV file: {csv_file}[/red]")


def main():
    """Main entry point for the application."""
    try:
        app()
    except KeyboardInterrupt:
        console.print("\n[yellow]Operation cancelled.[/yellow]")
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")


if __name__ == "__main__":
    main() 