"""
Test script for the enhanced dataset summary with comprehensive information.
"""

import sys
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add current directory to path
sys.path.insert(0, os.getcwd())

from agents.csv_agent import CSVAgent
from models.config import AgentConfig, LLMConfig
from app.interface import CSVAgentInterface
from rich.console import Console
from rich.panel import Panel

console = Console()

def test_enhanced_summary():
    """Test the enhanced dataset summary display."""
    
    console.print(Panel.fit("📊 Testing Enhanced Dataset Summary", style="bold blue"))
    
    try:
        # Initialize agent configuration
        config = AgentConfig(
            llm=LLMConfig(
                model_name="gpt-3.5-turbo",
                temperature=0.1
            ),
            verbose=False
        )
        
        console.print(f"🔑 Using API key: {config.llm.api_key[:10]}...")
        
        # Initialize interface 
        interface = CSVAgentInterface(config)
        
        # Load CSV file
        console.print("📂 Loading sample CSV data...")
        success = interface.load_csv_file("sample_data.csv")
        
        if success:
            console.print("\n🎉 Enhanced Dataset Summary displayed above!")
            console.print("\n💡 This summary now includes:")
            console.print("  ✅ Dataset overview with dimensions and missing data")
            console.print("  ✅ Analytics classification (measures vs dimensions)")
            console.print("  ✅ Detailed column information with types and sample values")
            console.print("  ✅ Basic statistics for numeric columns")
            console.print("  ✅ Data preview showing actual values")
            console.print("  ✅ Dataset insights and recommendations")
            
            console.print("\n🚀 Ready for visualization commands:")
            console.print("  • Type 'viz' for interactive chart creation")
            console.print("  • Type 'analytics' for detailed classification")
            console.print("  • Ask questions like 'Create a distribution chart for salary'")
            
        else:
            console.print("❌ Failed to load CSV file")
            
    except Exception as e:
        console.print(f"❌ Error in enhanced summary test: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_enhanced_summary() 