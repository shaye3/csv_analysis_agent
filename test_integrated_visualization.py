"""
Test script for integrated visualization capabilities in the main CSV agent.
"""

import os
from pathlib import Path
import pandas as pd
from rich.console import Console
from rich.panel import Panel

# Import our modules
from agents.csv_agent import CSVAgent
from models.config import AgentConfig, LLMConfig

console = Console()

def test_integrated_visualization():
    """Test the integrated visualization capabilities in the main agent."""
    
    console.print(Panel.fit("🎨 Testing Integrated CSV Agent Visualization", style="bold blue"))
    
    try:
        # Initialize agent with LLM
        config = AgentConfig(
            llm=LLMConfig(
                model_name="gpt-3.5-turbo",
                temperature=0.1
            ),
            verbose=False
        )
        
        console.print(f"🔑 Using API key: {config.llm.api_key[:10]}...")
        
        # Initialize CSV agent
        agent = CSVAgent(config)
        
        # Load sample data
        console.print("📊 Loading sample data...")
        result = agent.load_csv("sample_data.csv")
        
        if not result.success:
            console.print("❌ Failed to load CSV data")
            return
        
        console.print("✅ Successfully loaded: sample_data.csv")
        
        # Test new visualization tools
        console.print(Panel.fit("📊 Testing Analytics Classification Tool", style="green"))
        
        analytics_result = agent.execute_tool_directly('get_analytics_classification')
        console.print(analytics_result)
        
        console.print(Panel.fit("📈 Testing List Measures Tool", style="green"))
        
        measures_result = agent.execute_tool_directly('list_measures')
        console.print(measures_result)
        
        console.print(Panel.fit("📂 Testing List Dimensions Tool", style="green"))
        
        dimensions_result = agent.execute_tool_directly('list_dimensions')
        console.print(dimensions_result)
        
        console.print(Panel.fit("🎯 Testing Direct Visualization Creation", style="green"))
        
        # Test distribution visualization
        console.print("Creating distribution chart for 'salary'...")
        viz_result1 = agent.execute_tool_directly(
            'create_visualization',
            analysis_type='distribution',
            measure='salary'
        )
        console.print(viz_result1)
        
        # Test sum visualization
        console.print("\nCreating sum chart for 'salary' by 'department'...")
        viz_result2 = agent.execute_tool_directly(
            'create_visualization', 
            analysis_type='sum',
            measure='salary',
            dimension='department'
        )
        console.print(viz_result2)
        
        # Test count visualization
        console.print("\nCreating count chart for 'department'...")
        viz_result3 = agent.execute_tool_directly(
            'create_visualization',
            analysis_type='count', 
            dimension='department'
        )
        console.print(viz_result3)
        
        console.print(Panel.fit("🤖 Testing LLM-Powered Visualization Requests", style="yellow"))
        
        # Test natural language visualization requests
        test_questions = [
            "Show me the analytics classification for this dataset",
            "What measures are available in this data?", 
            "Create a distribution chart for salary",
            "Show me average salary by department",
            "Create a count visualization for department"
        ]
        
        for question in test_questions:
            console.print(f"\n[cyan]Question:[/cyan] {question}")
            response = agent.ask_question(question)
            console.print(f"[green]Answer:[/green] {response.answer}")
            if response.used_tools:
                console.print(f"[dim]Tools used: {', '.join(response.used_tools)}[/dim]")
        
        console.print(Panel.fit("🎉 Integrated visualization testing complete!", style="bold green"))
        
        console.print("\n[bold yellow]💡 Interactive Mode Available:[/bold yellow]")
        console.print("Run 'python app/main.py interactive --csv sample_data.csv' and use:")
        console.print("• Type 'viz' or 'chart' for interactive visualization menu")
        console.print("• Type 'analytics' to see measures vs dimensions")
        console.print("• Ask natural language questions like:")
        console.print("  - 'Create a distribution chart for salary'")
        console.print("  - 'Show me average performance by department'")
        console.print("  - 'Visualize count by education level'")
        
    except Exception as e:
        console.print(f"❌ Error in integration test: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_integrated_visualization() 