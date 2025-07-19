"""
Main Application Entry Point

This module provides the main entry point and CLI interface for the CSV agent.
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

from agents.csv_agent import CSVAgent
from models.config import AgentConfig, LLMConfig
from app.interface import CSVAgentInterface

# Load environment variables
load_dotenv()

# Initialize Rich console
console = Console()
app = typer.Typer(help="CSV Analysis Agent - Intelligent CSV Analysis Assistant")


@app.command()
def interactive(
    csv_file: Optional[str] = typer.Option(None, "--csv", "-c", help="CSV file to load"),
    api_key: Optional[str] = typer.Option(None, "--api-key", help="OpenAI API key"),
    model: str = typer.Option("gpt-4o-mini", "--model", "-m", help="LLM model to use"),
    temperature: float = typer.Option(0.1, "--temperature", "-t", help="LLM temperature"),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Enable verbose output")
):
    """Start interactive CSV analysis session."""
    console.print(Panel(
        "[bold blue]CSV Analysis Agent[/bold blue]\nIntelligent CSV Analysis Assistant", 
        title="Welcome"
    ))
    
    # Create configuration
    config = AgentConfig(
        llm=LLMConfig(
            model_name=model,
            temperature=temperature,
            api_key=api_key
        ),
        verbose=verbose
    )
    
    # Initialize interface
    try:
        interface = CSVAgentInterface(config)
        
        # Load CSV if provided
        if csv_file:
            if not interface.load_csv_file(csv_file):
                return
        else:
            # Prompt for CSV file
            csv_file = Prompt.ask("Enter path to CSV file")
            if not interface.load_csv_file(csv_file):
                return
        
        # Start interactive mode
        interface.run_interactive_mode()
        
    except ValueError as e:
        console.print(f"[red]Configuration error: {e}[/red]")
        console.print("[yellow]Please check your API key and try again.[/yellow]")
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")


@app.command()
def analyze(
    csv_file: str = typer.Argument(..., help="CSV file to analyze"),
    question: str = typer.Argument(..., help="Question to ask about the data"),
    api_key: Optional[str] = typer.Option(None, "--api-key", help="OpenAI API key"),
    model: str = typer.Option("gpt-4o-mini", "--model", "-m", help="LLM model to use"),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Enable verbose output")
):
    """Analyze CSV file with a single question."""
    config = AgentConfig(
        llm=LLMConfig(
            model_name=model,
            api_key=api_key
        ),
        verbose=verbose
    )
    
    try:
        interface = CSVAgentInterface(config)
        
        # Load CSV
        if not interface.load_csv_file(csv_file):
            return
        
        # Ask question
        interface.ask_question(question)
        
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")


@app.command()
def info(
    csv_file: str = typer.Argument(..., help="CSV file to get info about")
):
    """Get basic information about a CSV file."""
    if not os.path.exists(csv_file):
        console.print(f"[red]File not found: {csv_file}[/red]")
        return
    
    try:
        # Create minimal agent just for file info
        from data_io.csv_loader import CSVLoader
        
        loader = CSVLoader()
        if loader.load_csv(csv_file):
            metadata = loader.get_metadata()
            
            # Display basic info
            table = Table(title="Dataset Information")
            table.add_column("Property", style="cyan")
            table.add_column("Value", style="magenta")
            
            table.add_row("File Name", metadata.file_name)
            table.add_row("Rows", str(metadata.shape[0]))
            table.add_row("Columns", str(metadata.shape[1]))
            table.add_row("Memory Usage", f"{metadata.memory_usage / 1024:.2f} KB")
            
            console.print(table)
            
            # Show column info
            console.print("\n[bold]Columns:[/bold]")
            for i, col in enumerate(metadata.columns[:10], 1):
                column_info = loader.get_column_info(col)
                if column_info:
                    console.print(f"{i:2d}. {col}: {column_info.description}")
            
            if len(metadata.columns) > 10:
                console.print(f"    ... and {len(metadata.columns) - 10} more columns")
                
        else:
            console.print(f"[red]Failed to load CSV file: {csv_file}[/red]")
            
    except Exception as e:
        console.print(f"[red]Error analyzing file: {e}[/red]")


def main():
    """Main entry point."""
    try:
        app()
    except KeyboardInterrupt:
        console.print("\n[yellow]Operation cancelled.[/yellow]")
    except Exception as e:
        console.print(f"[red]Unexpected error: {e}[/red]")


if __name__ == "__main__":
    main() 