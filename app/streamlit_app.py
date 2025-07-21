"""
Streamlit Web Application for CSV Analysis Agent

A beautiful web interface for intelligent CSV data analysis with LLM-powered insights.
"""

import streamlit as st
import pandas as pd
import os
import sys
from io import StringIO

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agents.csv_agent import CSVAgent
from models.config import AgentConfig, LLMConfig, OpenAIModel

def init_session_state():
    """Initialize session state variables."""
    if 'agent' not in st.session_state:
        st.session_state.agent = None
    if 'messages' not in st.session_state:
        st.session_state.messages = []
    if 'csv_uploaded' not in st.session_state:
        st.session_state.csv_uploaded = False
    if 'selected_model' not in st.session_state:
        st.session_state.selected_model = OpenAIModel.GPT_4O_MINI.value
    if 'suggested_questions' not in st.session_state:
        st.session_state.suggested_questions = []

def display_dataset_summary():
    """Display basic dataset information."""
    st.header("📊 Dataset Overview")
    
    try:
        # Get basic metadata
        metadata = st.session_state.agent.csv_loader.get_metadata()
        df = st.session_state.agent.csv_loader.get_dataframe()
        
        if df is None or df.empty:
            st.warning("No data available to display.")
            return
        
        # Basic statistics in columns
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("📏 Rows", f"{metadata.shape[0]:,}")
        with col2:
            st.metric("📋 Columns", metadata.shape[1])
        with col3:
            missing_total = sum(metadata.null_counts.values())
            st.metric("❌ Missing Values", f"{missing_total:,}")
        with col4:
            memory_mb = metadata.memory_usage / (1024**2)
            st.metric("💾 Size", f"{memory_mb:.1f} MB")
        
        # Column information
        st.subheader("📋 Column Information")
        
        # Create column info table
        column_info = []
        for col_name in metadata.columns:
            try:
                col_info = st.session_state.agent.csv_loader.get_column_info(col_name)
                if col_info:
                    column_info.append({
                        'Column': col_name,
                        'Type': col_info.dtype,
                        'Description': col_info.description,
                        'Unique Values': col_info.unique_count,
                        'Missing': col_info.null_count
                    })
                else:
                    # Fallback if get_column_info fails
                    column_info.append({
                        'Column': col_name,
                        'Type': metadata.dtypes.get(col_name, 'unknown'),
                        'Description': 'No description available',
                        'Unique Values': df[col_name].nunique() if col_name in df.columns else 0,
                        'Missing': metadata.null_counts.get(col_name, 0)
                    })
            except Exception as e:
                # Fallback for any errors
                column_info.append({
                    'Column': col_name,
                    'Type': metadata.dtypes.get(col_name, 'unknown'),
                    'Description': 'Error loading description',
                    'Unique Values': df[col_name].nunique() if col_name in df.columns else 0,
                    'Missing': metadata.null_counts.get(col_name, 0)
                })
        
        if column_info:
            info_df = pd.DataFrame(column_info)
            st.dataframe(info_df, use_container_width=True)
        
        # Sample data preview
        st.subheader("👀 Data Preview")
        st.dataframe(df.head(10), use_container_width=True)
                
    except Exception as e:
        st.error(f"Error displaying dataset summary: {str(e)}")

def display_model_selection():
    """Display model selection interface."""
    st.header("🤖 Choose Your AI Model")
    
    # Get available models and their display names
    models = list(OpenAIModel)
    display_names = OpenAIModel.get_display_names()
    model_options = [display_names[model.value] for model in models]
    
    # Model selection
    selected_display_name = st.selectbox(
        "Select OpenAI Model:",
        model_options,
        index=model_options.index(display_names[OpenAIModel.GPT_4O_MINI.value]),  # Default to GPT-4o mini
        help="Choose the AI model for analyzing your data. GPT-4o mini offers good performance at lower cost."
    )
    
    # Find the corresponding model enum value
    selected_model = None
    for model in models:
        if display_names[model.value] == selected_display_name:
            selected_model = model
            break
    
    # Store selected model in session state
    st.session_state.selected_model = selected_model.value if selected_model else OpenAIModel.GPT_4O_MINI.value
    
    # Show model info
    model_info = {
        OpenAIModel.GPT_4O.value: "🚀 Most capable model with excellent reasoning",
        OpenAIModel.GPT_4O_MINI.value: "⚡ Fast and cost-effective, great for most tasks",
        OpenAIModel.GPT_4_TURBO.value: "🎯 High performance for complex analysis",
        OpenAIModel.GPT_4_PREVIEW.value: "🔬 Preview version with latest features"
    }
    
    if selected_model:
        st.info(f"**{selected_display_name}**: {model_info.get(selected_model.value, 'Advanced AI model for data analysis')}")

def handle_csv_upload():
    """Handle CSV file upload and agent initialization."""
    st.header("📁 Upload Your CSV File")
    
    uploaded_file = st.file_uploader(
        "Choose a CSV file", 
        type="csv",
        help="Upload a CSV file to start analyzing your data"
    )
    
    if uploaded_file is not None:
        try:
            # Show loading spinner
            with st.spinner("🔄 Processing your CSV file..."):
                # Convert uploaded file to string
                stringio = StringIO(uploaded_file.getvalue().decode("utf-8"))
                
                # Create temporary file
                temp_filename = f"temp_{uploaded_file.name}"
                with open(temp_filename, 'w', encoding='utf-8') as f:
                    f.write(stringio.getvalue())
                
                # Initialize agent and load CSV with selected model
                selected_model = getattr(st.session_state, 'selected_model', OpenAIModel.GPT_4O_MINI.value)
                config = AgentConfig(
                    llm=LLMConfig(model_name=selected_model)
                )
                st.session_state.agent = CSVAgent(config)
                
                # Load the CSV file
                result = st.session_state.agent.load_csv(temp_filename)
                
                if result.success:
                    st.session_state.csv_uploaded = True
                    st.session_state.messages = []  # Reset chat history
                    st.session_state.suggested_questions = []  # Reset questions for new dataset
                    
                    # Clean up temporary file
                    os.remove(temp_filename)
                    
                    st.success(f"✅ Successfully loaded: **{uploaded_file.name}**")
                    st.balloons()
                    
                    # Force page refresh to show new content
                    st.rerun()
                else:
                    st.error(f"Failed to load CSV: {result.error_message}")
                    st.session_state.agent = None
                    
                    # Clean up temporary file
                    os.remove(temp_filename)
            
        except Exception as e:
            st.error(f"❌ Error processing file: {str(e)}")
            st.info("Please ensure your file is a valid CSV format.")

def display_chat_interface():
    """Display the chat interface for Q&A."""
    st.header("💬 Ask Questions About Your Data")
    st.markdown("*Ask any question about your dataset in natural language*")
    
    # Display chat messages
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
    
    # Chat input
    if prompt := st.chat_input("What would you like to know about your data?"):
        # Add user message to chat history
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)
        
        # Generate assistant response
        with st.chat_message("assistant"):
            with st.spinner("🤔 Analyzing your question..."):
                try:
                    # Get response from agent
                    query_response = st.session_state.agent.ask_question(prompt)
                    response = query_response.answer
                    st.markdown(response)
                    
                    # Add assistant response to chat history
                    st.session_state.messages.append({"role": "assistant", "content": response})
                    
                except Exception as e:
                    error_msg = f"❌ Sorry, I encountered an error: {str(e)}"
                    st.error(error_msg)
                    st.session_state.messages.append({"role": "assistant", "content": error_msg})

def display_suggested_questions():
    """Display LLM-generated intelligent questions for the loaded dataset."""
    st.subheader("💡 Intelligent Questions You Can Ask")
    st.markdown("*AI-generated questions based on your dataset structure and content*")
    
    # Generate questions if not already available
    if st.session_state.agent and st.session_state.csv_uploaded and not st.session_state.suggested_questions:
        try:
            with st.spinner("🤖 Generating intelligent questions..."):
                st.session_state.suggested_questions = st.session_state.agent.suggest_questions()
        except Exception as e:
            st.warning(f"Could not generate intelligent questions: {str(e)}")
            st.info("You can still ask questions manually in the chat interface below.")
            return
    
    # Display LLM-generated questions if available
    if st.session_state.suggested_questions:
        # Display in two columns for better layout
        col1, col2 = st.columns(2)
        
        for i, question in enumerate(st.session_state.suggested_questions, 1):
            # Alternate between columns
            with col1 if i % 2 == 1 else col2:
                if st.button(f"**{i}.** {question}", key=f"suggestion_{i}", use_container_width=True):
                    # Add question to chat
                    st.session_state.messages.append({"role": "user", "content": question})
                    
                    # Generate response
                    with st.spinner("🤔 Analyzing your question..."):
                        query_response = st.session_state.agent.ask_question(question)
                        response = query_response.answer
                        st.session_state.messages.append({"role": "assistant", "content": response})
                    
                    # Rerun to show the new chat
                    st.rerun()
    else:
        st.info("Unable to generate intelligent questions. You can ask questions manually in the chat interface below.")



def main():
    """Main Streamlit application."""
    # Page configuration
    st.set_page_config(
        page_title="CSV Analysis Agent",
        page_icon="📊",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # Initialize session state
    init_session_state()
    
    # Header
    st.title("📊 CSV Analysis Agent")
    st.markdown("### *Upload your CSV and ask questions in natural language*")
    
    # Sidebar information
    with st.sidebar:
        st.header("ℹ️ About")
        st.markdown("""
        This application allows you to:
        
        📁 **Upload CSV files**  
        📊 **View dataset summary**  
        💬 **Ask questions in natural language**  
        🔍 **Get instant answers about your data**
        
        ---
        
        ### 🚀 How to Use:
        1. Upload your CSV file
        2. Review the dataset summary
        3. Ask questions about your data
        4. Get AI-powered insights
        
        ---
        
        ### 💡 Tips:
        - Ask specific questions for better results
        - Include column names in your questions
        - Try questions about statistics, counts, and filtering
        """)
        
        if st.session_state.csv_uploaded:
            st.success("✅ CSV file loaded!")
            
            # Quick stats in sidebar
            try:
                metadata = st.session_state.agent.csv_loader.get_metadata()
                st.metric("Rows", f"{metadata.shape[0]:,}")
                st.metric("Columns", metadata.shape[1])
            except:
                pass
    
    # Main content area
    if not st.session_state.csv_uploaded:
        # Show model selection
        display_model_selection()
        
        st.markdown("---")
        
        # Show upload interface
        handle_csv_upload()
        
    else:
        # Show dataset summary
        display_dataset_summary()
        
        st.markdown("---")
        
        # Show intelligent questions for the dataset
        display_suggested_questions()
        
        st.markdown("---")
        
        # Show chat interface
        display_chat_interface()
        
        # Option to upload a new file
        st.markdown("---")
        if st.button("📁 Upload New CSV File"):
            st.session_state.csv_uploaded = False
            st.session_state.agent = None
            st.session_state.messages = []
            st.session_state.suggested_questions = []
            st.rerun()

if __name__ == "__main__":
    main() 