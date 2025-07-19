#!/usr/bin/env python3
"""
Test script to demonstrate LLM-powered measure/dimension classification
"""

import sys
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Add current directory to path
sys.path.insert(0, os.getcwd())

def test_analytics_classification():
    """Test the new measure/dimension classification functionality."""
    print("🧪 Testing Analytics Classification (Measures vs Dimensions)")
    print("=" * 80)
    
    try:
        from agents.csv_agent import CSVAgent
        from models.config import AgentConfig, LLMConfig
        from models.schemas import ColumnType
        
        # Create agent configuration
        config = AgentConfig(
            llm=LLMConfig(
                model_name="gpt-3.5-turbo",
                temperature=0.1,
                api_key=os.getenv("OPENAI_API_KEY")
            ),
            verbose=False
        )
        
        # Check if API key is available
        if not config.llm.api_key:
            print("❌ No OpenAI API key found. Please set OPENAI_API_KEY in your .env file")
            return False
        
        print(f"🔑 Using API key: {config.llm.api_key[:10]}...")
        
        # Initialize agent with LLM
        agent = CSVAgent(config)
        
        # Load sample data
        print(f"\n📊 Loading sample data...")
        result = agent.load_csv("sample_data.csv")
        
        if not result.success:
            print(f"❌ Failed to load CSV: {result.message}")
            return False
        
        print(f"✅ Successfully loaded: {result.metadata.file_name}")
        print(f"📈 Dataset: {result.metadata.shape[0]} rows × {result.metadata.shape[1]} columns")
        
        # Get analytics summary
        print(f"\n📊 Analytics Classification Summary:")
        print("-" * 60)
        
        analytics_summary = agent.csv_loader.get_analytics_summary()
        print(f"📈 {analytics_summary['summary']}")
        print(f"🔢 Measures: {analytics_summary['measures']}")
        print(f"📂 Dimensions: {analytics_summary['dimensions']}")
        
        # Test detailed classification for all columns
        print(f"\n🤖 Detailed Column Classification:")
        print("-" * 80)
        
        for column in result.metadata.columns:
            try:
                # Get column info with classification
                column_info = agent.csv_loader.get_column_info(column)
                
                if column_info:
                    # Determine emoji based on classification
                    type_emoji = "📈" if column_info.column_type == ColumnType.MEASURE else "📂"
                    
                    print(f"{type_emoji} {column} ({column_info.column_type.value.upper()})")
                    print(f"   📝 Description: {column_info.description}")
                    print(f"   📊 Data: {column_info.dtype}, {column_info.unique_count} unique values")
                    print(f"   🔍 Sample: {', '.join(map(str, column_info.sample_values[:3]))}")
                    print()
                else:
                    print(f"❌ Could not analyze column: {column}")
                    
            except Exception as e:
                print(f"❌ Error analyzing {column}: {e}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error in test: {e}")
        return False

def test_analytics_usage():
    """Test how the analytics classification could be used."""
    print("\n💡 Analytics Usage Examples")
    print("=" * 60)
    
    try:
        from agents.csv_agent import CSVAgent
        from models.config import AgentConfig, LLMConfig
        
        config = AgentConfig(
            llm=LLMConfig(api_key=os.getenv("OPENAI_API_KEY")),
            verbose=False
        )
        
        agent = CSVAgent(config)
        agent.load_csv("sample_data.csv")
        
        # Get measures and dimensions
        measures = agent.csv_loader.get_measures()
        dimensions = agent.csv_loader.get_dimensions()
        
        print(f"📈 Available Measures for Aggregation:")
        for measure in measures:
            print(f"   • {measure} - can be summed, averaged, analyzed")
        
        print(f"\n📂 Available Dimensions for Grouping:")
        for dimension in dimensions:
            print(f"   • {dimension} - can be used to group, filter, slice data")
        
        print(f"\n🎯 Example Analysis Queries You Could Ask:")
        if measures and dimensions:
            example_measure = measures[0]
            example_dimension = dimensions[0]
            
            examples = [
                f"What is the average {example_measure} by {example_dimension}?",
                f"Show me the total {example_measure} for each {example_dimension}",
                f"Which {example_dimension} has the highest {example_measure}?",
                f"What is the distribution of {example_measure}?",
                f"How does {example_measure} vary across different {example_dimension}?"
            ]
            
            for i, example in enumerate(examples, 1):
                print(f"   {i}. {example}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error in usage test: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Testing Enhanced CSV Loader with Analytics Classification")
    print("\n" + "=" * 80)
    
    # Check for API key
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("❌ No OpenAI API key found!")
        print("💡 Please create a .env file with: OPENAI_API_KEY=your_key_here")
        print("📚 See ENV_SETUP.md for detailed instructions")
        sys.exit(1)
    
    print(f"🔑 API Key found: {api_key[:10]}...")
    
    # Run tests
    success1 = test_analytics_classification()
    
    if success1:
        success2 = test_analytics_usage()
    else:
        success2 = False
    
    print("\n" + "=" * 80)
    if success1 and success2:
        print("🎉 All tests passed! Analytics classification is working!")
        print("\n💡 Key Benefits:")
        print("   ✅ Automatic measure/dimension classification")
        print("   ✅ Context-aware business intelligence insights")
        print("   ✅ Ready for advanced analytics and aggregations") 
        print("   ✅ Intelligent query suggestions based on data types")
    else:
        print("⚠️  Some tests failed. Check the output above.")
    
    print(f"\n🚀 Your CSV Agent is now ready for advanced analytics!") 