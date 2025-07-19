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
        """Display a comprehensive summary of the loaded data."""
        
        # Basic dataset information
        basic_table = Table(title="📊 Dataset Overview")
        basic_table.add_column("Property", style="cyan", width=20)
        basic_table.add_column("Value", style="magenta")
        
        basic_table.add_row("📁 File Name", metadata.file_name)
        basic_table.add_row("📏 Dimensions", f"{metadata.shape[0]} rows × {metadata.shape[1]} columns")
        basic_table.add_row("💾 Memory Usage", f"{metadata.memory_usage / 1024:.2f} KB")
        
        # Calculate missing data summary
        total_cells = metadata.shape[0] * metadata.shape[1]
        total_missing = sum(metadata.null_counts.values())
        missing_percentage = (total_missing / total_cells * 100) if total_cells > 0 else 0
        
        basic_table.add_row("❌ Missing Data", f"{total_missing} cells ({missing_percentage:.1f}%)")
        
        self.console.print(basic_table)
        
        # Get analytics classification
        try:
            analytics_result = self.agent.execute_tool_directly('get_analytics_classification')
            
            # Extract measures and dimensions from the result
            measures_section = analytics_result.split("📈 MEASURES")[1].split("📂 DIMENSIONS")[0] if "📈 MEASURES" in analytics_result else ""
            dimensions_section = analytics_result.split("📂 DIMENSIONS")[1].split("💡")[0] if "📂 DIMENSIONS" in analytics_result else ""
            
            # Analytics classification table
            analytics_table = Table(title="🎯 Analytics Classification")
            analytics_table.add_column("Type", style="cyan", width=12)
            analytics_table.add_column("Count", style="magenta", width=8)
            analytics_table.add_column("Fields", style="white")
            
            measures_count = measures_section.count("•") if measures_section else 0
            dimensions_count = dimensions_section.count("•") if dimensions_section else 0
            
            measures_list = [col.strip() for col in measures_section.replace("•", "").split(",") if col.strip()] if measures_section else []
            dimensions_list = [col.strip() for col in dimensions_section.replace("•", "").split(",") if col.strip()] if dimensions_section else []
            
            analytics_table.add_row("📈 Measures", str(measures_count), ", ".join(measures_list[:5]) + ("..." if len(measures_list) > 5 else ""))
            analytics_table.add_row("📂 Dimensions", str(dimensions_count), ", ".join(dimensions_list[:5]) + ("..." if len(dimensions_list) > 5 else ""))
            
            self.console.print(analytics_table)
            
        except Exception as e:
            self.console.print(f"[yellow]⚠️  Could not get analytics classification: {str(e)}[/yellow]")
        
        # Detailed column information
        columns_table = Table(title="📋 Column Details")
        columns_table.add_column("Column", style="cyan", width=20)
        columns_table.add_column("Type", style="blue", width=12)
        columns_table.add_column("Classification", style="green", width=12)
        columns_table.add_column("Unique", style="magenta", width=8)
        columns_table.add_column("Missing", style="red", width=8)
        columns_table.add_column("Sample Values", style="white")
        
        for column in metadata.columns:
            try:
                # Get detailed column info
                column_info = self.agent.csv_loader.get_column_info(column)
                if column_info:
                    # Format sample values
                    sample_values = [str(val) for val in column_info.sample_values[:3]]
                    sample_str = ", ".join(sample_values)
                    if len(column_info.sample_values) > 3:
                        sample_str += "..."
                    
                    # Classification emoji
                    classification_icon = "📈" if column_info.column_type.value == "measure" else "📂"
                    classification = f"{classification_icon} {column_info.column_type.value.title()}"
                    
                    # Missing data
                    missing_count = column_info.null_count
                    missing_pct = (missing_count / metadata.shape[0] * 100) if metadata.shape[0] > 0 else 0
                    missing_str = f"{missing_count} ({missing_pct:.1f}%)" if missing_count > 0 else "0"
                    
                    columns_table.add_row(
                        column,
                        column_info.dtype,
                        classification,
                        str(column_info.unique_count),
                        missing_str,
                        sample_str
                    )
                else:
                    # Fallback if column info not available
                    dtype = str(metadata.dtypes.get(column, "unknown"))
                    missing_count = metadata.null_counts.get(column, 0)
                    missing_pct = (missing_count / metadata.shape[0] * 100) if metadata.shape[0] > 0 else 0
                    missing_str = f"{missing_count} ({missing_pct:.1f}%)" if missing_count > 0 else "0"
                    
                    columns_table.add_row(
                        column,
                        dtype,
                        "❓ Unknown",
                        "N/A",
                        missing_str,
                        "N/A"
                    )
                    
            except Exception as e:
                # Error fallback
                columns_table.add_row(
                    column,
                    "Error",
                    "❌ Error",
                    "N/A",
                    "N/A",
                    f"Error: {str(e)[:30]}..."
                )
        
        self.console.print(columns_table)
        
        # Basic statistics for numeric columns
        try:
            stats_result = self.agent.execute_tool_directly('get_basic_stats')
            if stats_result and "No numeric columns" not in stats_result:
                self.console.print(Panel(
                    stats_result,
                    title="📊 Numeric Statistics",
                    border_style="blue"
                ))
        except Exception as e:
            self.console.print(f"[yellow]⚠️  Could not get basic statistics: {str(e)}[/yellow]")
        
        # Sample data preview
        if metadata.sample_data:
            sample_table = Table(title="👀 Data Preview (First 3 Rows)")
            
            # Add columns
            for column in metadata.columns:
                sample_table.add_column(column, style="white", overflow="fold", max_width=15)
            
            # Add sample data rows
            for row_data in metadata.sample_data:
                row_values = [str(row_data.get(col, "N/A"))[:20] for col in metadata.columns]
                sample_table.add_row(*row_values)
            
            self.console.print(sample_table)
        
        # Summary insights
        insights = []
        if total_missing > 0:
            insights.append(f"⚠️  Dataset has {total_missing} missing values ({missing_percentage:.1f}%)")
        
        if len(metadata.columns) > 10:
            insights.append(f"📊 Large dataset with {len(metadata.columns)} columns")
        
        numeric_cols = sum(1 for dtype in metadata.dtypes.values() if 'int' in str(dtype) or 'float' in str(dtype))
        if numeric_cols > 0:
            insights.append(f"🔢 {numeric_cols} numeric columns available for analysis")
        
        if insights:
            insights_text = "\n".join([f"• {insight}" for insight in insights])
            self.console.print(Panel(
                insights_text,
                title="💡 Dataset Insights",
                border_style="yellow"
            ))
    
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
                elif question.lower() in ['viz', 'visualize', 'chart']:
                    self._show_visualization_menu()
                elif question.lower() == 'analytics':
                    self._show_analytics_classification()
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
- `analytics` - Show measures vs dimensions classification
- `viz`, `visualize`, or `chart` - Interactive visualization menu
- `clear` - Clear conversation history
- `quit` or `exit` - Exit the application

**Example Questions:**
- "What is the summary of this dataset?"
- "Tell me about the 'column_name' column"
- "What are the statistics for numeric columns?"
- "Search for rows containing 'search_term'"
- "What are the unique values in 'column_name'?"
- "Create a distribution chart for salary"
- "Show me average sales by department" 
- "Visualize count by category"

**Tips:**
- Ask follow-up questions naturally
- Reference previous answers with "it", "that", etc.
- Be specific about column names for better results
- Use 'viz' for interactive chart creation menu
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
            "get_value_counts": "Get frequency distribution for categorical columns",
            "get_analytics_classification": "Show measures vs dimensions classification",
            "list_measures": "List all available measures (numerical fields)",
            "list_dimensions": "List all available dimensions (categorical fields)",
            "create_visualization": "Create data visualizations and charts"
        }
        
        for tool in tools:
            description = tool_descriptions.get(tool, "Analysis tool")
            usage_count = usage_stats.get(tool, 0)
            table.add_row(tool, str(usage_count), description)
        
        self.console.print(table)

    def _show_analytics_classification(self) -> None:
        """Show analytics classification summary."""
        try:
            result = self.agent.execute_tool_directly('get_analytics_classification')
            self.console.print(Panel(result, title="[green]Analytics Classification[/green]", border_style="green"))
        except Exception as e:
            self.console.print(f"[red]Error getting analytics classification: {e}[/red]")

    def _show_visualization_menu(self) -> None:
        """Show interactive visualization menu."""
        try:
            # Get available measures and dimensions
            measures_result = self.agent.execute_tool_directly('list_measures') 
            dimensions_result = self.agent.execute_tool_directly('list_dimensions')
            
            self.console.print(Panel(
                "[bold blue]📊 Interactive Visualization Menu[/bold blue]\n\n"
                "Choose from the analysis types below:",
                title="Data Visualization"
            ))
            
            # Show analysis type options
            self.console.print("[bold cyan]Available Analysis Types:[/bold cyan]")
            self.console.print("1. [green]Distribution[/green] - Show distribution of a measure (histogram + box plot)")
            self.console.print("2. [blue]Sum[/blue] - Sum of measure grouped by dimension") 
            self.console.print("3. [yellow]Average[/yellow] - Average of measure grouped by dimension")
            self.console.print("4. [magenta]Count[/magenta] - Count occurrences by dimension")
            self.console.print("5. [dim]Back to main menu[/dim]")
            
            choice = Prompt.ask("\nSelect analysis type", choices=["1", "2", "3", "4", "5"], default="5")
            
            if choice == "5":
                return
            
            analysis_types = {
                "1": "distribution",
                "2": "sum", 
                "3": "average",
                "4": "count"
            }
            
            analysis_type = analysis_types[choice]
            
            # Get user selections based on analysis type
            if analysis_type == "distribution":
                self._create_distribution_chart(measures_result)
            elif analysis_type == "count":
                self._create_count_chart(dimensions_result)
            else:  # sum or average
                self._create_aggregation_chart(analysis_type, measures_result, dimensions_result)
                
        except Exception as e:
            self.console.print(f"[red]Error in visualization menu: {e}[/red]")

    def _create_distribution_chart(self, measures_result: str) -> None:
        """Create a distribution chart."""
        self.console.print(Panel(measures_result, title="Available Measures"))
        
        measure = Prompt.ask("Enter the measure name for distribution analysis")
        
        if measure:
            with self.console.status("[bold blue]Creating distribution chart..."):
                result = self.agent.execute_tool_directly('create_visualization', 
                                                       analysis_type='distribution', 
                                                       measure=measure)
            self.console.print(Panel(result, title="[green]Distribution Chart Created[/green]", border_style="green"))

    def _create_count_chart(self, dimensions_result: str) -> None:
        """Create a count chart."""
        self.console.print(Panel(dimensions_result, title="Available Dimensions"))
        
        dimension = Prompt.ask("Enter the dimension name for count analysis")
        
        if dimension:
            with self.console.status("[bold blue]Creating count chart..."):
                result = self.agent.execute_tool_directly('create_visualization',
                                                       analysis_type='count',
                                                       dimension=dimension)
            self.console.print(Panel(result, title="[green]Count Chart Created[/green]", border_style="green"))

    def _create_aggregation_chart(self, analysis_type: str, measures_result: str, dimensions_result: str) -> None:
        """Create an aggregation chart (sum or average)."""
        self.console.print(Panel(measures_result, title="Available Measures"))
        measure = Prompt.ask("Enter the measure name")
        
        if not measure:
            return
            
        self.console.print(Panel(dimensions_result, title="Available Dimensions"))
        dimension = Prompt.ask("Enter the dimension name for grouping")
        
        if dimension:
            with self.console.status(f"[bold blue]Creating {analysis_type} chart..."):
                result = self.agent.execute_tool_directly('create_visualization',
                                                       analysis_type=analysis_type,
                                                       measure=measure,
                                                       dimension=dimension)
            self.console.print(Panel(result, title=f"[green]{analysis_type.title()} Chart Created[/green]", border_style="green")) 