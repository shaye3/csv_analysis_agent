#!/usr/bin/env python3
"""
Quick test script for the CSV Agent
"""

import sys
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Add current directory to path
sys.path.insert(0, os.getcwd())

def test_csv_loader():
    """Test the CSV loader functionality."""
    print("🧪 Testing CSV Loader...")
    
    from data_io.csv_loader import CSVLoader
    
    loader = CSVLoader()
    
    # Test loading the sample data
    success = loader.load_csv("sample_data.csv")
    
    if success:
        print("✅ CSV loading successful!")
        
        # Test metadata
        metadata = loader.get_metadata()
        print(f"📊 Dataset: {metadata.shape[0]} rows, {metadata.shape[1]} columns")
        print(f"📁 Columns: {', '.join(metadata.columns[:5])}...")
        
        # Test data summary
        summary = loader.get_data_summary()
        print(f"📋 Summary length: {len(summary)} characters")
        
        # Test column info
        column_info = loader.get_column_info('salary')
        if column_info:
            print(f"💰 Salary column: {column_info.dtype}, {column_info.unique_count} unique values")
        
        # Test search
        search_results = loader.search_data('Engineering')
        print(f"🔍 Search for 'Engineering': {len(search_results)} results")
        
        return True
    else:
        print("❌ CSV loading failed!")
        return False

def test_tool_manager():
    """Test the tool manager."""
    print("\n🧪 Testing Tool Manager...")
    
    from core.tool_manager import ToolManager
    from data_io.csv_loader import CSVLoader
    from models.config import ToolConfig
    
    # Load CSV first
    loader = CSVLoader()
    loader.load_csv("sample_data.csv")
    
    # Test tool manager
    config = ToolConfig()
    tool_manager = ToolManager(config, loader)
    
    tools = tool_manager.get_available_tools()
    print(f"🔧 Available tools: {', '.join(tools)}")
    
    # Test direct tool execution
    result = tool_manager.execute_tool('get_data_summary')
    if result.success:
        print(f"✅ Tool execution successful! Result length: {len(result.result)} chars")
        return True
    else:
        print(f"❌ Tool execution failed: {result.error}")
        return False

def test_agent_without_llm():
    """Test agent components without LLM."""
    print("\n🧪 Testing Agent Components...")
    
    try:
        from agents.csv_agent import CSVAgent
        from models.config import AgentConfig, LLMConfig
        
        # This will fail without API key, but we can test the structure
        print("✅ Agent imports successful!")
        
        # Test configuration with environment variables
        config = AgentConfig()  # Should use defaults from environment
        print("✅ Configuration creation successful!")
        print(f"📝 Model from config: {config.llm.model_name}")
        print(f"🌡️  Temperature from config: {config.llm.temperature}")
        
        # Check if API key is loaded from environment
        api_key_loaded = config.llm.api_key is not None
        print(f"🔑 API key loaded from environment: {'✅' if api_key_loaded else '❌'}")
        
        if api_key_loaded:
            print(f"🔑 API key preview: {config.llm.api_key[:10]}..." if len(config.llm.api_key) > 10 else "🔑 API key is set")
        else:
            print("💡 To test with API key, create a .env file with OPENAI_API_KEY=your_key")
        
        return True
        
    except Exception as e:
        print(f"❌ Agent test failed: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Testing the new modular CSV Agent")
    print("=" * 50)
    
    all_tests_passed = True
    
    # Test each component
    tests = [
        test_csv_loader,
        test_tool_manager, 
        test_agent_without_llm
    ]
    
    for test in tests:
        try:
            result = test()
            all_tests_passed = all_tests_passed and result
        except Exception as e:
            print(f"❌ Test {test.__name__} failed with exception: {e}")
            all_tests_passed = False
    
    print("\n" + "=" * 50)
    if all_tests_passed:
        print("🎉 All tests passed! The new modular agent is working!")
    else:
        print("⚠️  Some tests failed. Check the output above.")
    
    print("\n💡 To use with real LLM:")
    print("   1. Create a .env file with:")
    print("      OPENAI_API_KEY=your_actual_key_here")
    print("   2. Or export directly:")
    print("      export OPENAI_API_KEY='your-key-here'")
    print("   3. Then run:")
    print("      python app/main.py interactive --csv sample_data.csv")
    print("\n📚 See ENV_SETUP.md for detailed instructions") 