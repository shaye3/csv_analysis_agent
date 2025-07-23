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
git clone https://github.com/shaye3/csv_analysis_agent.git
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

1. **Upload** a CSV file (try the included `sample_data.csv` or `sales_data.csv`)
2. **Review** the automatic dataset summary and column analysis
3. **Click** on AI-generated questions like:

**For Employee Data (`sample_data.csv`):**
   - *"What is the average salary by department?"*
   - *"Who has the highest performance rating?"*
   - *"What is the age distribution by city?"*

**For Sales Data (`sales_data.csv`):**
   - *"What is the total revenue by sales region?"*
   - *"Which product category has the highest average order value?"*
   - *"Who are the top 5 sales reps by revenue?"*

4. **Ask custom questions** like:
   - *"Show me all orders above $5000"*
   - *"What's the monthly sales trend?"*
   - *"Compare Enterprise vs SMB customer segments"*


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

🚀 **Happy Data Analysis!** 📊 