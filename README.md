# 📊 CSV Analysis Agent

A powerful, AI-driven application for intelligent CSV data analysis with natural language queries. Upload your CSV files and chat with your data using OpenAI's latest models through a beautiful web interface or command-line interface.

## 🌟 What This Application Does

The CSV Analysis Agent transforms how you interact with spreadsheet data by letting you:

- **🤖 Ask questions in plain English** about your CSV data
- **📊 Get instant insights** with AI-powered analytics
- **🔍 Filter, sort, and analyze** data using natural language
- **💡 Discover patterns** with intelligent question suggestions
- **📈 Generate statistics** and summaries automatically
- **💬 Have conversations** with follow-up questions and context

**Example**: Instead of writing complex formulas, just ask *"What is the average salary by department?"* or *"Who are the top 5 performers in Engineering?"*

## 🚀 Quick Start Guide

### 1. Prerequisites

- **Python 3.8+** installed on your system
- **OpenAI API Key** (get one at [platform.openai.com](https://platform.openai.com))

### 2. Installation

```bash
# Clone or download this repository
git clone <repository-url>
cd csv_analysis_agent

# Create a virtual environment (recommended)
python -m venv venv

# Activate the virtual environment
# On macOS/Linux:
source venv/bin/activate
# On Windows:
venv\Scripts\activate

# Install required packages
pip install -r requirements.txt
```

### 3. API Key Setup

**Option A: Create a .env file (Recommended)**

1. Create a file named `.env` in the project root directory
2. Add your OpenAI API key:

```env
OPENAI_API_KEY=your_openai_api_key_here
```

**Option B: Set environment variable**

```bash
# On macOS/Linux:
export OPENAI_API_KEY="your_openai_api_key_here"

# On Windows Command Prompt:
set OPENAI_API_KEY=your_openai_api_key_here

# On Windows PowerShell:
$env:OPENAI_API_KEY="your_openai_api_key_here"
```

> ⚠️ **Security Note**: Never share your API key or commit the `.env` file to version control. Keep your API key secure!

### 4. Running the Application

#### 🌐 Web Interface (Recommended)

```bash
python run_streamlit.py
```

This opens a beautiful web application in your browser where you can:

1. **Select your preferred AI model** (GPT-4o, GPT-4o mini, GPT-4 Turbo, GPT-4 Preview)
2. **Upload CSV files** with drag & drop
3. **View automatic dataset analysis** with intelligent insights
4. **Get AI-generated question suggestions** tailored to your data
5. **Chat with your data** using natural language

#### 💻 Command Line Interface

```bash
# Interactive mode
python app/main.py interactive --csv your_data.csv

# Single question mode
python app/main.py analyze your_data.csv "What is the average salary by department?"
```

## 🎯 Key Features

### 🤖 **AI-Powered Analysis**
- **Multiple OpenAI Models**: Choose from GPT-4o, GPT-4o mini, GPT-4 Turbo, or GPT-4 Preview
- **Intelligent Question Suggestions**: AI generates insightful questions based on your specific dataset
- **Natural Language Processing**: Ask questions in plain English and get accurate answers
- **Context-Aware Conversations**: Follow-up questions remember previous context

### 📊 **Comprehensive Data Operations**
- **Statistical Analysis**: Automatic calculation of means, medians, distributions
- **Data Filtering**: Find specific subsets of your data
- **Multi-Column Sorting**: Sort by multiple criteria with custom order
- **Grouping & Aggregation**: Group data by categories and calculate aggregates
- **Missing Data Analysis**: Identify and analyze incomplete data

### 🎨 **Beautiful User Interface**
- **Modern Web Design**: Clean, intuitive Streamlit interface
- **Drag & Drop Upload**: Easy CSV file handling
- **Real-time Chat**: Interactive conversation with your data
- **Clickable Suggestions**: One-click to ask AI-generated questions
- **Visual Data Summary**: Comprehensive dataset overview

### 🔧 **Developer-Friendly**
- **Modular Architecture**: Clean, extensible codebase
- **Multiple Interfaces**: Web UI, CLI, and programmatic API
- **Comprehensive Testing**: Reliable and well-tested components
- **Easy Configuration**: Simple setup with environment variables

## 📝 Example Usage

### Web Interface Example:

1. **Upload** a CSV file (e.g., employee data, sales data, survey results)
2. **Review** the automatic dataset summary and column analysis
3. **Click** on AI-generated questions like:
   - *"What is the average salary by department?"*
   - *"Who has the highest performance rating?"*
   - *"What is the age distribution by city?"*
4. **Ask custom questions** like:
   - *"Show me all engineers with more than 5 years experience"*
   - *"What's the correlation between education level and salary?"*

### CLI Example:

```bash
$ python app/main.py interactive --csv employees.csv

📊 CSV Analysis Agent
✅ Successfully loaded employees.csv (500 rows × 10 columns)

🤖 AI Model: GPT-4o mini
📈 Dataset Summary:
   - Numerical columns: salary, age, years_experience, performance_rating
   - Categorical columns: department, city, education_level

💬 Ask a question: What is the average salary by department?

📊 Analysis Results:
Department-wise Average Salary:
• Engineering: $85,420
• Marketing: $72,350
• Sales: $68,750
• HR: $71,200

💬 Ask a question: Show me the top 3 highest paid employees

🔍 Top 3 Highest Paid Employees:
1. Frank Miller (Engineering): $95,000
2. Uma Clark (Engineering): $92,000
3. Paul Anderson (Sales): $88,000
```

## 🛠️ Advanced Configuration

### Model Selection

Choose your preferred OpenAI model based on your needs:

- **GPT-4o mini** (Default): Fast and cost-effective, great for most analyses
- **GPT-4o**: More powerful reasoning for complex queries
- **GPT-4 Turbo**: Enhanced performance for large datasets
- **GPT-4 Preview**: Latest features and capabilities

### Programmatic Usage

```python
from agents.csv_agent import CSVAgent
from models.config import AgentConfig, LLMConfig, OpenAIModel

# Configure the agent
config = AgentConfig(
    llm=LLMConfig(
        model_name=OpenAIModel.GPT_4O_MINI.value,
        api_key="your_api_key_here"  # or use environment variable
    )
)

# Initialize and use the agent
agent = CSVAgent(config)
result = agent.load_csv("your_data.csv")

if result.success:
    # Ask questions
    response = agent.ask_question("What is the summary of this data?")
    print(response.answer)
    
    # Get intelligent question suggestions
    suggestions = agent.suggest_questions()
    for question in suggestions:
        print(f"💡 {question}")
```

## 🔧 Available Data Operations

| Operation | Description | Example Question |
|-----------|-------------|------------------|
| **Statistical Analysis** | Calculate means, medians, std dev | *"What are the basic statistics for salary?"* |
| **Filtering** | Find specific data subsets | *"Show me all employees in Engineering"* |
| **Sorting** | Order data by columns | *"Sort employees by salary, highest first"* |
| **Grouping** | Group and aggregate data | *"Average salary by department and city"* |
| **Top/Bottom Analysis** | Find extremes | *"Who are the top 5 performers?"* |
| **Distribution Analysis** | Understand data spread | *"What's the age distribution?"* |
| **Missing Data** | Identify incomplete records | *"How much data is missing?"* |

## 🧪 Testing Your Setup

Test the installation with the included sample data:

```bash
# Test web interface
python run_streamlit.py
# Then upload sample_data.csv in the web interface

# Test CLI
python app/main.py analyze sample_data.csv "How many employees are there?"
```

## 🔐 Security & Privacy

- **Local Processing**: Your CSV data is processed locally and not stored permanently
- **API Security**: Only question text is sent to OpenAI, not your raw data
- **Environment Variables**: Keep API keys secure using `.env` files
- **Session-Based**: Web interface data is cleared when you close the browser

## 🚨 Troubleshooting

### Common Issues:

**"OpenAI API key not found"**
- Ensure your `.env` file exists and contains `OPENAI_API_KEY=your_key`
- Check that the `.env` file is in the project root directory

**"Module not found" errors**
- Make sure you activated your virtual environment
- Run `pip install -r requirements.txt` again

**"Permission denied" on macOS/Linux**
- You might need to use `python3` instead of `python`

**CSV upload issues**
- Ensure your CSV file has headers
- Check for special characters or encoding issues
- Try saving your file as UTF-8 encoded CSV

## 📦 Dependencies

### Core Requirements:
- `openai` - OpenAI API integration
- `langchain` - LLM framework and tools
- `pandas` - Data manipulation and analysis
- `streamlit` - Web interface framework
- `typer` - Command-line interface
- `pydantic` - Data validation and settings
- `python-dotenv` - Environment variable management

## 🤝 Contributing

This project uses a modular architecture that's easy to extend:

- **Add new tools**: Create new analysis functions in `core/tool_manager.py`
- **Enhance UI**: Modify the Streamlit interface in `app/streamlit_app.py`
- **Improve prompts**: Update AI prompts in respective manager classes
- **Add model support**: Extend model options in `models/config.py`

## 📚 Learn More

- **OpenAI API Documentation**: [platform.openai.com/docs](https://platform.openai.com/docs)
- **Streamlit Documentation**: [docs.streamlit.io](https://docs.streamlit.io)
- **LangChain Documentation**: [python.langchain.com](https://python.langchain.com)

---

## 🎉 Ready to Get Started?

1. **Get your OpenAI API key** from [platform.openai.com](https://platform.openai.com)
2. **Follow the setup instructions** above
3. **Run the web interface**: `python run_streamlit.py`
4. **Upload a CSV file** and start chatting with your data!

**Need help?** Check the troubleshooting section or create an issue on GitHub.

🚀 **Happy Data Analysis!** 📊 