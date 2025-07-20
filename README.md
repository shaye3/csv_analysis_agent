# CSV Analysis Agent

A modular, object-oriented LLM-powered agent system for intelligent CSV data analysis with **beautiful web interface**. This system allows users to ask questions about CSV data using natural language and get accurate, data-driven responses.

## 🎯 Features

- **🌐 Beautiful Web Interface**: Modern Streamlit web application with drag & drop CSV upload
- **🤖 Intelligent CSV Analysis**: Ask questions using natural language and get accurate responses
- **🧠 LLM-Powered Analytics**: Automatic measure/dimension classification and intelligent insights
- **💬 Conversational Memory**: Support for follow-up questions with conversation context
- **🔧 Extensible Tool System**: Function calling with data analysis operations
- **📈 Advanced Analytics**: Filtering, sorting, grouping and statistical analysis
- **🎨 Multiple Interfaces**: Both web UI and CLI available

## 🚀 Quick Start

### 1. Installation

```bash
# Clone the repository
git clone <repository-url>
cd csv_analysis_agent

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

### 3. Web Application (Recommended)

#### Start the Web Interface:

```bash
python run_streamlit.py
```

This will open a beautiful web interface in your browser where you can:

- 📁 **Upload CSV files** with drag & drop
- 📊 **View comprehensive dataset summaries** with analytics classification
- 💬 **Chat with your data** using natural language
- 📈 **Get intelligent insights** about measures vs dimensions

#### Web Features:
- ✅ **File Upload**: Drag & drop CSV files
- ✅ **Dataset Overview**: Comprehensive summary with statistics
- ✅ **Analytics Classification**: Automatic measure/dimension identification
- ✅ **Natural Language Chat**: Ask questions about your data
- ✅ **Data Operations**: Filtering, sorting, grouping and aggregation

### 4. Command Line Interface

#### Interactive Mode

```bash
python app/main.py interactive --csv path/to/your/data.csv
```

**New CLI Commands:**
- Type `analytics` to see measures vs dimensions classification
- Ask natural language questions about your data

#### Single Question

```bash
python app/main.py analyze data.csv "What is the average salary per department?"
```

## 📊 Data Analysis Capabilities

### Supported Operations:
1. **📈 Statistical Analysis**: Get comprehensive statistics for numerical data
2. **📊 Data Aggregation**: Group by categories and aggregate measures  
3. **🔍 Data Filtering**: Filter data by column values
4. **📋 Data Sorting**: Sort by multiple columns with custom order

### Example Questions:
- "What is the average salary per department?"
- "Show me employees with the highest performance ratings"
- "Filter employees by Engineering department"
- "Sort employees by salary from highest to lowest"

## 🏗️ Architecture

The system is built with a modular, object-oriented design:

### Core Classes

1. **`CSVAgent`** - Main orchestrator that coordinates all components
2. **`CSVLoader`** - Enhanced CSV loading with LLM-powered analytics classification
3. **`MemoryManager`** - Manages conversation history and context
4. **`ToolManager`** - Handles tool registration and execution
5. **`AgentBuilder`** - Composes LLM, memory, tools and context into working agent
6. **`StreamlitApp`** - Web interface for user interaction

### Available Tools

- `get_data_summary` - Comprehensive dataset overview
- `get_column_info` - Detailed column information with LLM insights
- `sort_data` - Sort data by multiple columns with custom order
- `filter_data` - Filter data by column values
- `group_and_aggregate` - Group by columns and aggregate measures
- `get_basic_stats` - Statistical analysis for numeric columns
- `get_analytics_classification` - Show measures vs dimensions
- `list_measures` - List all numerical fields for aggregation
- `list_dimensions` - List all categorical fields for grouping

## 📋 Programmatic Usage

```python
from agents.csv_agent import CSVAgent
from models.config import AgentConfig, LLMConfig

# Initialize the agent
config = AgentConfig(
    llm=LLMConfig(model_name="gpt-4o-mini")
)
agent = CSVAgent(config)

# Load CSV file
result = agent.load_csv("data.csv")
if result.success:
    print(f"Loaded: {result.message}")
    
    # Get analytics classification
    classification = agent.execute_tool_directly('get_analytics_classification')
    print(classification)
    
    # Ask questions
    response = agent.ask_question("What is the average salary by department?")
    print(response.answer)
    
    # Group and aggregate data
    result = agent.execute_tool_directly(
        'group_and_aggregate',
        group_by_columns='department',
        aggregations='salary:average'
    )
    print(result)
```

## 🔧 Advanced Usage

### Data Operations

The system supports comprehensive data analysis operations:

```python
# Sort data by multiple columns
agent.execute_tool_directly('sort_data', 
                          sort_columns='department,salary', 
                          sort_orders='asc,desc')

# Filter data by values
agent.execute_tool_directly('filter_data',
                          column_name='department',
                          values='Engineering,Sales')

# Group and aggregate data
agent.execute_tool_directly('group_and_aggregate',
                          group_by_columns='department',
                          aggregations='salary:average,years_experience:sum')
```

### Analytics Classification

Get intelligent insights about your data structure:

```python
# Get measures (numerical fields for aggregation)
measures = agent.csv_loader.get_measures()

# Get dimensions (categorical fields for grouping)  
dimensions = agent.csv_loader.get_dimensions()

# Get full analytics summary
summary = agent.csv_loader.get_analytics_summary()
```

## 📖 Example Session

### Web Interface:
1. Open `http://localhost:8501` 
2. Enter your OpenAI API key
3. Upload a CSV file
4. View automatic dataset summary and analytics classification
5. Chat with your data using natural language

### CLI Interface:
```
$ python app/main.py interactive --csv employees.csv

📊 CSV Analysis Agent
Successfully loaded employees.csv (1000 rows × 8 columns)

🎯 Analytics Classification:
📈 Measures: salary, performance_rating, years_experience  
📂 Dimensions: employee_id, name, department, city, education_level

💬 Ask a question: What is the average salary per department?

📊 The average salary per department:
- Engineering: $85,420
- Marketing: $72,350  
- Sales: $68,750
- HR: $71,200

💬 Ask a question: Show me employees in Engineering department

🔍 Found 250 employees in Engineering department:
- Average salary: $85,420
- Average experience: 6.2 years
- Performance rating range: 3.2 - 4.9
- Education levels: 60% Master, 35% Bachelor, 5% PhD
```

## 🧪 Testing

The project includes comprehensive tests:

```bash
# Test basic functionality
python test_agent.py

# Test analytics classification
python test_analytics_classification.py
```

## 📦 Dependencies

### Core Dependencies:
- **LangChain**: LLM integration and tool calling
- **Pandas**: Data processing and analysis
- **Pydantic**: Configuration and data validation
- **Python-dotenv**: Environment variable management

### Web Dependencies:
- **Streamlit**: Web application framework

### CLI Dependencies:
- **Rich**: Beautiful CLI formatting
- **Typer**: Command-line interface

## 🔐 Security Notes

- Never commit your `.env` file to version control
- Keep your API key secure and rotate it regularly  
- The web app only stores data in memory during the session

## 🚀 What's New

### Latest Features:
- ✅ **Streamlit Web Interface**: Beautiful drag & drop CSV upload
- ✅ **LLM-Powered Analytics**: Automatic measure/dimension classification
- ✅ **Enhanced Search**: Now finds numeric IDs and values correctly
- ✅ **Multi-parameter Tools**: Sorting, filtering and grouping operations
- ✅ **Comprehensive Summaries**: Rich dataset overviews with statistics
- ✅ **Follow-up Questions**: Intelligent conversation context handling

### Recent Fixes:
- 🐛 Fixed search functionality for numeric columns (employee IDs now work!)
- 🐛 Fixed multi-parameter tool registration for filtering, sorting and grouping
- 🐛 Resolved structured output warnings
- 🐛 Enhanced error handling and validation

---

**Ready to explore your data? Start with the web interface:**

```bash
python run_streamlit.py
```

**Or use the CLI for power users:**

```bash  
python app/main.py interactive --csv your_data.csv
```

🎯 **Your CSV Analysis Agent is ready for intelligent business intelligence!** 📊🚀 