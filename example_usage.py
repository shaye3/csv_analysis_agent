"""
Example Usage of CSV QA Agent

This script demonstrates how to use the CSV QA Agent programmatically
for automated CSV analysis.
"""

import os
import pandas as pd
from csv_qa_agent import CSVQAAgent

def create_sample_csv():
    """Create a sample CSV file for testing."""
    data = {
        'name': ['Alice', 'Bob', 'Charlie', 'Diana', 'Eve'],
        'age': [25, 30, 35, 28, 32],
        'city': ['New York', 'London', 'Paris', 'Tokyo', 'Sydney'],
        'salary': [50000, 60000, 70000, 55000, 65000],
        'department': ['Engineering', 'Marketing', 'Engineering', 'Sales', 'Marketing']
    }
    
    df = pd.DataFrame(data)
    df.to_csv('sample_employees.csv', index=False)
    print("Created sample_employees.csv")
    return 'sample_employees.csv'

def main():
    """Main example function."""
    # Note: You need to set your OpenAI API key in environment variables
    # or pass it directly to the agent
    
    # Create sample data
    csv_file = create_sample_csv()
    
    try:
        # Initialize the agent
        print("Initializing CSV QA Agent...")
        agent = CSVQAAgent()
        
        # Load CSV file
        print(f"Loading CSV file: {csv_file}")
        result = agent.load_csv(csv_file)
        
        if not result["success"]:
            print(f"Failed to load CSV: {result['message']}")
            return
        
        print(f"Successfully loaded: {result['message']}")
        
        # Example questions to ask
        questions = [
            "What is the summary of this dataset?",
            "How many employees are in each department?",
            "What are the statistics for the salary column?",
            "Tell me about the age column",
            "Search for employees in Engineering department",
            "What is the average salary by department?"
        ]
        
        print("\n" + "="*60)
        print("ASKING QUESTIONS")
        print("="*60)
        
        for i, question in enumerate(questions, 1):
            print(f"\nQuestion {i}: {question}")
            print("-" * 50)
            
            response = agent.ask_question(question)
            print(f"Answer: {response['answer']}")
            
            if response['used_tools']:
                print(f"Tools used: {', '.join(response['used_tools'])}")
            
            if response['follow_up']:
                print("(This was detected as a follow-up question)")
        
        # Show conversation history
        print("\n" + "="*60)
        print("CONVERSATION HISTORY")
        print("="*60)
        print(agent.get_conversation_history())
        
        # Show agent status
        print("\n" + "="*60)
        print("AGENT STATUS")
        print("="*60)
        status = agent.get_agent_status()
        for key, value in status.items():
            print(f"{key}: {value}")
        
        # Test direct tool execution
        print("\n" + "="*60)
        print("DIRECT TOOL EXECUTION")
        print("="*60)
        
        # Execute tools directly
        tools_to_test = [
            ('get_data_summary', []),
            ('get_column_info', ['salary']),
            ('get_basic_stats', ['age']),
            ('get_value_counts', ['department']),
            ('search_data', ['Engineering'])
        ]
        
        for tool_name, args in tools_to_test:
            print(f"\nExecuting {tool_name} with args {args}:")
            result = agent.execute_tool_directly(tool_name, *args)
            print(result)
        
    except ValueError as e:
        print(f"Error: {e}")
        print("Please set your OpenAI API key in the OPENAI_API_KEY environment variable")
    except Exception as e:
        print(f"Unexpected error: {e}")
    finally:
        # Clean up
        if os.path.exists(csv_file):
            os.remove(csv_file)
            print(f"\nCleaned up {csv_file}")

if __name__ == "__main__":
    main() 