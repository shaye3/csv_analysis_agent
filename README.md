# CSV Analysis Agent

A modular, object-oriented LLM-powered agent system for intelligent CSV data analysis with **beautiful web interface and interactive visualizations**. This system allows users to ask questions about CSV data using natural language, create stunning visualizations, and get accurate, data-driven responses.

## 🎯 Features

- **🌐 Beautiful Web Interface**: Modern Streamlit web application with drag & drop CSV upload
- **📊 Interactive Visualizations**: Create charts with natural language or point-and-click interface
- **🤖 Intelligent CSV Analysis**: Ask questions using natural language and get accurate responses
- **🧠 LLM-Powered Analytics**: Automatic measure/dimension classification and intelligent insights
- **💬 Conversational Memory**: Support for follow-up questions with conversation context
- **🔧 Extensible Tool System**: Function calling with data analysis operations
- **📈 Advanced Analytics**: Distribution, aggregation, and statistical analysis
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
- 🎨 **Create interactive visualizations** with point-and-click interface
- 💬 **Chat with your data** using natural language
- 📈 **Get intelligent insights** about measures vs dimensions

#### Web Features:
- ✅ **File Upload**: Drag & drop CSV files
- ✅ **Dataset Overview**: Comprehensive summary with statistics
- ✅ **Analytics Classification**: Automatic measure/dimension identification
- ✅ **Interactive Charts**: Distribution, sum, average, count visualizations  
- ✅ **Natural Language Chat**: Ask questions about your data
- ✅ **Quick Actions**: One-click access to common operations

### 4. Command Line Interface

#### Interactive Mode

```bash
python app/main.py interactive --csv path/to/your/data.csv
```

**New CLI Commands:**
- Type `viz` or `chart` for interactive visualization menu
- Type `analytics` to see measures vs dimensions classification
- Ask natural language questions like "Create a distribution chart for salary"

#### Single Question

```bash
python app/main.py analyze data.csv "What is the average salary per department?"
```

## 📊 Visualization Capabilities

### Supported Chart Types:
1. **📈 Distribution Charts**: Histograms and box plots for numerical data
2. **📊 Aggregation Charts**: Bar charts for sum/average by categories  
3. **🥧 Count Charts**: Pie charts and bar charts for frequency analysis
4. **📋 Statistical Summaries**: Comprehensive statistical insights

### Example Questions:
- "What is the average salary per department?"
- "Create a distribution chart for performance ratings"
- "Show me count by education level"
- "Display sum of sales by region"

## 🏗️ Architecture

The system is built with a modular, object-oriented design:

### Core Classes

1. **`CSVAgent`** - Main orchestrator that coordinates all components
2. **`CSVLoader`** - Enhanced CSV loading with LLM-powered analytics classification
3. **`MemoryManager`** - Manages conversation history and context
4. **`ToolManager`** - Handles tool registration and execution
5. **`CSVVisualizer`** - Creates beautiful charts and visualizations
6. **`StreamlitApp`** - Web interface for user interaction

### Available Tools

- `get_data_summary` - Comprehensive dataset overview
- `get_column_info` - Detailed column information with LLM insights
- `search_data` - Search for specific data (now works with numeric IDs!)
- `get_basic_stats` - Statistical analysis for numeric columns
- `get_value_counts` - Frequency distribution for categorical data
- `get_analytics_classification` - Show measures vs dimensions
- `list_measures` - List all numerical fields for aggregation
- `list_dimensions` - List all categorical fields for grouping
- `create_visualization` - Generate interactive charts

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
    
    # Create visualizations
    viz_result = agent.execute_tool_directly(
        'create_visualization',
        analysis_type='average',
        measure='salary',
        dimension='department'
    )
    print(viz_result)
```

## 🔧 Advanced Usage

### Custom Visualizations

The system supports four types of analysis:

```python
# Distribution analysis
agent.execute_tool_directly('create_visualization', 
                          analysis_type='distribution', 
                          measure='salary')

# Aggregation analysis  
agent.execute_tool_directly('create_visualization',
                          analysis_type='average',
                          measure='salary', 
                          dimension='department')

# Count analysis
agent.execute_tool_directly('create_visualization',
                          analysis_type='count',
                          dimension='department')
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
5. Create visualizations or chat with your data

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

[Interactive chart displayed]

💬 Ask a question: viz

🎨 Visualization Menu:
1. Distribution - Show distribution of a measure
2. Sum - Sum of measure by dimension  
3. Average - Average of measure by dimension
4. Count - Count by dimension

Select: 2
Measure: salary
Dimension: department
✅ Chart created and displayed!
```

## 🧪 Testing

The project includes comprehensive tests:

```bash
# Test basic functionality
python test_agent.py

# Test analytics classification
python test_analytics_classification.py

# Test visualization system  
python test_visualization.py

# Test web integration
python test_integrated_visualization.py

# Test enhanced dataset summary
python test_enhanced_summary.py
```

## 📦 Dependencies

### Core Dependencies:
- **LangChain**: LLM integration and tool calling
- **Pandas**: Data processing and analysis
- **Pydantic**: Configuration and data validation
- **Python-dotenv**: Environment variable management

### Visualization Dependencies:
- **Matplotlib & Seaborn**: Static chart generation
- **Plotly**: Interactive web charts  
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
- ✅ **Interactive Visualizations**: Point-and-click chart creation
- ✅ **LLM-Powered Analytics**: Automatic measure/dimension classification
- ✅ **Enhanced Search**: Now finds numeric IDs and values correctly
- ✅ **Multi-parameter Tools**: Natural language visualization requests
- ✅ **Comprehensive Summaries**: Rich dataset overviews with statistics

### Recent Fixes:
- 🐛 Fixed search functionality for numeric columns (employee IDs now work!)
- 🐛 Fixed multi-parameter visualization tools 
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