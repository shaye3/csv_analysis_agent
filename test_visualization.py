"""
Test script for CSV data visualization capabilities.
"""

import os
from pathlib import Path
import pandas as pd
from rich.console import Console
from rich.panel import Panel

# Import our modules
from data_io.csv_loader import CSVLoader
from core.llm_manager import LLMManager
from models.config import LLMConfig
from utils.visualizer import CSVVisualizer, create_sample_plots

console = Console()

def test_csv_visualization():
    """Test the enhanced CSV visualization capabilities."""
    
    console.print(Panel.fit("🎨 Testing CSV Data Visualization", style="bold blue"))
    
    try:
        # Initialize LLM
        llm_config = LLMConfig()
        llm_manager = LLMManager(llm_config)
        
        console.print(f"🔑 Using API key: {llm_config.api_key[:10]}...")
        
        # Initialize CSV loader with LLM
        csv_loader = CSVLoader(llm=llm_manager.get_llm())
        
        # Load sample data
        console.print("📊 Loading sample data...")
        success = csv_loader.load_csv("sample_data.csv")
        
        if not success:
            console.print("❌ Failed to load CSV data")
            return
        
        console.print("✅ Successfully loaded: sample_data.csv")
        
        # Get dataframe and analytics info
        df = csv_loader.get_dataframe()
        analytics_summary = csv_loader.get_analytics_summary()
        
        console.print(f"📈 Dataset: {df.shape[0]} rows × {df.shape[1]} columns")
        
        measures = analytics_summary['measures']
        dimensions = analytics_summary['dimensions']
        
        console.print(f"🔢 Measures: {measures}")
        console.print(f"📂 Dimensions: {dimensions}")
        
        # Initialize visualizer
        visualizer = CSVVisualizer()
        
        # Demo 1: Distribution analysis
        console.print(Panel.fit("📊 Demo 1: Distribution Analysis", style="green"))
        if measures:
            result1 = visualizer.analyze_and_plot(
                df, "", measures[0], "distribution", 
                title=f"Distribution Analysis of {measures[0]}"
            )
            console.print(f"✅ Distribution stats: {result1['statistics']}")
        
        # Demo 2: Sum analysis
        console.print(Panel.fit("📊 Demo 2: Sum Analysis", style="green"))
        if measures and dimensions:
            result2 = visualizer.analyze_and_plot(
                df, dimensions[0], measures[0], "sum",
                title=f"Sum of {measures[0]} by {dimensions[0]}"
            )
            console.print(f"✅ Sum analysis: {result2['summary']}")
        
        # Demo 3: Average analysis  
        console.print(Panel.fit("📊 Demo 3: Average Analysis", style="green"))
        if len(measures) > 1 and len(dimensions) > 1:
            result3 = visualizer.analyze_and_plot(
                df, dimensions[1], measures[0], "average",
                title=f"Average {measures[0]} by {dimensions[1]}"
            )
            console.print(f"✅ Average analysis: {result3['summary']}")
        
        # Demo 4: Count analysis
        console.print(Panel.fit("📊 Demo 4: Count Analysis", style="green"))
        if dimensions:
            result4 = visualizer.analyze_and_plot(
                df, dimensions[0], "", "count",
                title=f"Count Distribution by {dimensions[0]}"
            )
            console.print(f"✅ Count analysis: {result4['summary']}")
        
        # Interactive menu
        console.print(Panel.fit("🎯 Interactive Visualization Menu", style="yellow"))
        console.print("You can now use the interactive menu to create custom visualizations!")
        
        # Uncomment the line below to enable interactive mode
        # visualizer.interactive_analysis_menu(df, measures, dimensions)
        
        console.print(Panel.fit("🎉 Visualization testing complete!", style="bold green"))
        
    except Exception as e:
        console.print(f"❌ Error in visualization test: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_csv_visualization()