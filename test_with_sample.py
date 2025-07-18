#!/usr/bin/env python3
"""
Test Script for CSV QA Agent with Sample Data

This script demonstrates the CSV QA Agent capabilities using the provided sample data.
Make sure to set your OPENAI_API_KEY environment variable before running.
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def check_requirements():
    """Check if all requirements are met."""
    # Check for API key
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key or api_key == "your_openai_api_key_here":
        print("❌ Error: OPENAI_API_KEY not set!")
        print("💡 Please set your OpenAI API key:")
        print("   export OPENAI_API_KEY='your-api-key-here'")
        print("   or run: python setup_env.py")
        return False
    
    # Check for sample data
    if not Path("sample_data.csv").exists():
        print("❌ Error: sample_data.csv not found!")
        print("💡 Make sure the sample data file exists in the current directory.")
        return False
    
    print("✅ Requirements check passed!")
    return True

def run_interactive_demo():
    """Run an interactive demonstration."""
    try:
        from csv_qa_agent import CSVQAAgent
        
        print("\n🚀 Initializing CSV QA Agent...")
        agent = CSVQAAgent()
        
        print("📊 Loading sample employee data...")
        result = agent.load_csv("sample_data.csv")
        
        if not result["success"]:
            print(f"❌ Failed to load CSV: {result['message']}")
            return
        
        print(f"✅ {result['message']}")
        
        # Demo questions
        demo_questions = [
            "What is the summary of this dataset?",
            "How many employees are in each department?",
            "What are the statistics for the salary column?",
            "Who are the highest-paid employees?",
            "Tell me about employees in the Engineering department",
            "What is the average age by department?",
            "Show me employees with Master's degree",
            "Which cities have the most employees?"
        ]
        
        print("\n" + "="*60)
        print("🎯 DEMO: Asking Questions About Employee Data")
        print("="*60)
        
        for i, question in enumerate(demo_questions, 1):
            print(f"\n💬 Question {i}: {question}")
            print("-" * 50)
            
            try:
                response = agent.ask_question(question)
                
                if response["is_csv_related"]:
                    print(f"🤖 Answer: {response['answer']}")
                    
                    if response['used_tools']:
                        print(f"🔧 Tools used: {', '.join(response['used_tools'])}")
                    
                    if response['follow_up']:
                        print("💡 (Detected as follow-up question)")
                else:
                    print(f"⚠️  {response['answer']}")
                    
            except Exception as e:
                print(f"❌ Error: {e}")
            
            # Pause between questions for readability
            if i < len(demo_questions):
                input("\nPress Enter to continue to next question...")
        
        # Show conversation summary
        print("\n" + "="*60)
        print("📋 CONVERSATION SUMMARY")
        print("="*60)
        
        status = agent.get_agent_status()
        print(f"Questions asked: {status['memory_summary']['question_count']}")
        print(f"Tools available: {len(status['available_tools'])}")
        
        print("\n🎉 Demo completed successfully!")
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("💡 Make sure to install requirements: pip install -r requirements.txt")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")

def run_specific_analysis():
    """Run specific analysis examples."""
    try:
        from csv_qa_agent import CSVQAAgent
        
        print("\n🔬 Running Specific Analysis Examples...")
        agent = CSVQAAgent()
        
        # Load data
        result = agent.load_csv("sample_data.csv")
        if not result["success"]:
            print(f"❌ Failed to load CSV: {result['message']}")
            return
        
        # Direct tool execution examples
        print("\n🛠️  Direct Tool Execution Examples:")
        print("-" * 40)
        
        tools_to_demo = [
            ("get_data_summary", [], "Dataset Overview"),
            ("get_column_info", ["salary"], "Salary Column Analysis"),
            ("get_basic_stats", ["age"], "Age Statistics"),
            ("get_value_counts", ["department"], "Department Distribution"),
            ("search_data", ["Engineering"], "Engineering Employees")
        ]
        
        for tool_name, args, description in tools_to_demo:
            print(f"\n📊 {description}:")
            result = agent.execute_tool_directly(tool_name, *args)
            print(result)
            print("-" * 40)
        
    except Exception as e:
        print(f"❌ Error in specific analysis: {e}")

def main():
    """Main function."""
    print("🎯 CSV QA Agent Test with Sample Data")
    print("="*50)
    
    if not check_requirements():
        return
    
    print("\nChoose test mode:")
    print("1. Interactive Demo (Q&A with explanations)")
    print("2. Specific Analysis (Direct tool execution)")
    print("3. Both")
    
    choice = input("\nEnter choice (1-3): ").strip()
    
    if choice == "1":
        run_interactive_demo()
    elif choice == "2":
        run_specific_analysis()
    elif choice == "3":
        run_interactive_demo()
        print("\n" + "="*60)
        run_specific_analysis()
    else:
        print("❌ Invalid choice. Running interactive demo...")
        run_interactive_demo()

if __name__ == "__main__":
    main() 