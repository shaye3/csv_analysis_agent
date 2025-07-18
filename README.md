# CSV QA Agent

A modular, object-oriented LLM-powered agent system for intelligent CSV data analysis. This system allows users to ask questions about CSV data using natural language and get accurate, data-driven responses.

## 🎯 Features

- **Intelligent CSV Analysis**: Load CSV files and ask questions using natural language
- **Conversational Memory**: Support for follow-up questions with conversation context
- **Function Calling**: Extensible tool system for data analysis operations
- **CSV-Only Responses**: Strict focus on loaded CSV data, rejecting unrelated questions
- **Interactive CLI**: Beautiful command-line interface with Rich formatting
- **Modular Architecture**: Clean, object-oriented design with clear separation of concerns

## 🏗️ Architecture

The system is built with a modular, object-oriented design:

### Core Classes

1. **`CSVLoader`** - Handles CSV file loading, parsing, and data management
2. **`MemoryManager`** - Manages conversation history and follow-up question detection
3. **`FunctionRouter`** - Manages tool registration and function calling
4. **`CSVQAAgent`** - Main agent that orchestrates all components
5. **`CSVQAApplication`** - High-level application interface and CLI

### Available Tools

- `get_data_summary` - Get comprehensive dataset overview
- `get_column_info` - Detailed information about specific columns
- `search_data` - Search for specific data in the CSV
- `get_basic_stats` - Statistical analysis for numeric columns
- `get_value_counts` - Frequency distribution for categorical data

## 🚀 Quick Start

### 1. Installation

```bash
# Clone the repository
git clone <repository-url>
cd csv_qa_agent

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Configuration

Set your OpenAI API key:

```bash
export OPENAI_API_KEY="your-api-key-here"
```

Or create a `.env` file:

```bash
cp .env.example .env
# Edit .env and add your API key
```

### 3. Usage

#### Interactive Mode

```bash
python main.py interactive --csv path/to/your/data.csv
```

#### Single Question

```bash
python main.py analyze data.csv "What is the summary of this dataset?"
```

#### File Information

```bash
python main.py info data.csv
```

## 📋 Programmatic Usage

```python
from csv_qa_agent import CSVQAAgent

# Initialize the agent
agent = CSVQAAgent()

# Load CSV file
result = agent.load_csv("data.csv")
if result["success"]:
    print(f"Loaded: {result['message']}")
    
    # Ask questions
    response = agent.ask_question("What are the column names in this dataset?")
    print(response["answer"])
    
    # Follow-up question
    response = agent.ask_question("Tell me more about the first column")
    print(response["answer"])
```

## 🔧 Advanced Usage

### Custom Tools

You can extend the system by creating custom analysis tools:

```python
from function_router import CSVAnalysisTool

class CustomAnalysisTool(CSVAnalysisTool):
    name: str = "custom_analysis"
    description: str = "Performs custom analysis on the data"
    
    def execute(self, parameter: str) -> str:
        # Your custom analysis logic
        return "Analysis result"

# Register the tool
agent.function_router.register_tool(CustomAnalysisTool(csv_loader=agent.csv_loader))
```

### Memory Management

```python
# Clear conversation history
agent.clear_conversation()

# Get conversation context
context = agent.get_conversation_history()

# Export conversation
conversation_json = agent.memory_manager.export_conversation()
```

### Direct Tool Execution

```python
# Execute tools directly without the LLM
result = agent.execute_tool_directly("get_data_summary")
result = agent.execute_tool_directly("get_column_info", "column_name")
```

## 📖 Example Session

```
$ python main.py interactive --csv employees.csv

┌─────────────────────────────────────────────────────────────────────────────────┐
│                                     Welcome                                     │
├─────────────────────────────────────────────────────────────────────────────────┤
│                               CSV QA Agent                                     │
│                        Intelligent CSV Analysis Assistant                      │
└─────────────────────────────────────────────────────────────────────────────────┘

Loading CSV file: employees.csv
✓ Successfully loaded employees.csv

┏━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃ Property       ┃ Value                                   ┃
┡━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┩
│ File Name      │ employees.csv                           │
│ Rows           │ 1000                                    │
│ Columns        │ 6                                       │
│ Memory Usage   │ 48.5 KB                                 │
│ Columns        │ name, age, department, salary, city ... │
└────────────────┴─────────────────────────────────────────────┘

Your question: What is the summary of this dataset?

┌─────────────────────────────────────────────────────────────────────────────────┐
│                                     Answer                                      │
├─────────────────────────────────────────────────────────────────────────────────┤
│ This dataset contains employee information with 1000 rows and 6 columns:       │
│                                                                                 │
│ • **name**: Employee names (text)                                              │
│ • **age**: Employee ages (numeric, range: 22-65)                               │
│ • **department**: Department names (5 unique departments)                      │
│ • **salary**: Annual salaries (numeric, range: $35,000-$120,000)               │
│ • **city**: Employee cities (15 unique cities)                                 │
│ • **hire_date**: Hiring dates (datetime)                                       │
│                                                                                 │
│ The dataset appears complete with no missing values.                           │
└─────────────────────────────────────────────────────────────────────────────────┘

Your question: What about the salary distribution?

┌─────────────────────────────────────────────────────────────────────────────────┐
│                                     Answer                                      │
├─────────────────────────────────────────────────────────────────────────────────┤
│ The salary distribution shows:                                                 │
│                                                                                 │
│ • **Mean**: $72,450                                                            │
│ • **Median**: $71,000                                                          │
│ • **Standard Deviation**: $18,200                                              │
│ • **Range**: $35,000 - $120,000                                                │
│                                                                                 │
│ The distribution appears relatively normal with salaries concentrated around   │
│ the $70K mark.                                                                 │
└─────────────────────────────────────────────────────────────────────────────────┘

💡 This appears to be a follow-up question
```

## 🧪 Testing

Run the example script to test the system:

```bash
python example_usage.py
```

This will create sample data and demonstrate all the agent's capabilities.

## 🎯 Key Design Principles

1. **CSV-Only Focus**: The agent strictly answers questions about the loaded CSV data
2. **Modular Architecture**: Clear separation of concerns with dedicated classes
3. **Extensible Tools**: Easy to add new analysis capabilities
4. **Conversation Memory**: Maintains context for natural follow-up questions
5. **Error Handling**: Graceful handling of invalid questions and data issues

## 🔒 Security & Privacy

- No data is sent to external services except for LLM processing
- CSV data remains local to your system
- API keys are handled securely through environment variables

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Add tests for new functionality
4. Submit a pull request

## 📄 License

MIT License - see LICENSE file for details.

## 🆘 Troubleshooting

### Common Issues

1. **API Key Error**: Make sure your OpenAI API key is set correctly
2. **Import Errors**: Ensure all dependencies are installed with `pip install -r requirements.txt`
3. **CSV Loading Issues**: Check file permissions and format
4. **Memory Issues**: Large CSV files may require adjusting memory settings

### Getting Help

- Check the example scripts for usage patterns
- Review the docstrings in each module
- Create an issue for bugs or feature requests 