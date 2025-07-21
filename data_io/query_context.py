"""
Query Context Module

This module manages context and suggestions for CSV queries.
"""

from typing import List, Optional, Dict, Any
from langchain_core.language_models.base import BaseLanguageModel
from data_io.csv_loader import CSVLoader


class QueryContext:
    """
    Manages query context and provides intelligent suggestions.
    
    This class helps build context for LLM queries and suggests relevant questions.
    """
    
    def __init__(self, csv_loader: CSVLoader, llm: Optional[BaseLanguageModel] = None):
        """
        Initialize query context manager.
        
        Args:
            csv_loader (CSVLoader): CSV loader instance
            llm (Optional[BaseLanguageModel]): LLM instance for intelligent question generation
        """
        self.csv_loader = csv_loader
        self.llm = llm
    
    def get_context_for_classification(self) -> str:
        """
        Get context string for question classification.
        
        Returns:
            str: Context string describing the current dataset
        """
        if not self.csv_loader.is_loaded():
            return "No CSV data is currently loaded."
        
        metadata = self.csv_loader.get_metadata()
        if not metadata:
            return "CSV loaded but metadata unavailable."
        
        context_parts = [
            f"Currently loaded CSV file: {metadata.file_name}",
            f"Number of rows: {metadata.shape[0]}",
            f"Number of columns: {metadata.shape[1]}",
            f"Column names: {', '.join(metadata.columns)}",
        ]
        
        # Add sample data types (first 5 columns)
        sample_dtypes = list(metadata.dtypes.items())[:5]
        if sample_dtypes:
            dtype_info = ', '.join([f"{col}({dtype})" for col, dtype in sample_dtypes])
            context_parts.append(f"Sample data types: {dtype_info}")
        
        return "\n".join(context_parts)
    
    def suggest_questions(self) -> List[str]:
        """
        Suggest relevant questions based on the loaded data using LLM intelligence.
        
        Returns:
            List[str]: List of 10 intelligent suggested questions
        """
        if not self.csv_loader.is_loaded():
            return ["Please load a CSV file first to get question suggestions."]
        
        # If no LLM available, fall back to basic suggestions
        if not self.llm:
            return self._generate_basic_suggestions()
        
        metadata = self.csv_loader.get_metadata()
        if not metadata:
            return ["Dataset loaded but unable to generate suggestions."]
        
        try:
            # Get analytics classification for better context
            analytics_summary = self.csv_loader.get_analytics_summary()
            
            # Get sample data for context
            df = self.csv_loader.get_dataframe()
            sample_data = df.head(3).to_string() if df is not None else "No sample data available"
            
            # Create comprehensive prompt for question generation
            prompt = f"""You are a data analyst helping users explore their CSV dataset. Generate exactly 10 simple, insightful questions that can be answered with the data.

DATASET INFORMATION:
File: {metadata.file_name}
Rows: {metadata.shape[0]:,}
Columns: {metadata.shape[1]}

COLUMNS AND TYPES:
{chr(10).join([f"- {col} ({dtype})" for col, dtype in metadata.dtypes.items()])}

MEASURES (numerical fields): {', '.join(analytics_summary.get('measures', []))}
DIMENSIONS (categorical fields): {', '.join(analytics_summary.get('dimensions', []))}

SAMPLE DATA (first 3 rows):
{sample_data}

QUESTION REQUIREMENTS:
1. Each item must contain exactly ONE simple question
2. Use actual column names from the dataset
3. Questions should be direct and actionable
4. Focus on insights users would want to know
5. Mix different types of analysis: averages, distributions, top/bottom values, comparisons, counts

QUESTION PATTERNS TO FOLLOW:
- "What is the average [measure] by [dimension]?"
- "Who has the highest/lowest [measure]?"
- "What is the [measure] distribution by [dimension]?"
- "How many [dimension] are there?"
- "What are the top 5 [dimension] by [measure]?"

EXAMPLES OF GOOD QUESTIONS:
- What is the average salary by department?
- Who has the highest performance rating?
- What is the age distribution by city?
- How many employees are in each department?

Generate exactly 10 questions as a numbered list. Each line should contain only ONE question:

1. [Single question using actual column names]
2. [Single question using actual column names]
...and so on"""

            # Get LLM response
            response = self.llm.invoke(prompt)
            
            # Parse the response to extract questions
            questions = self._parse_llm_questions(response.content if hasattr(response, 'content') else str(response))
            
            # Ensure we have exactly 10 questions
            if len(questions) == 10:
                return questions
            else:
                # If parsing failed, fall back to basic suggestions
                return self._generate_basic_suggestions()
                
        except Exception as e:
            # If LLM fails, fall back to basic suggestions
            print(f"Warning: LLM question generation failed: {e}")
            return self._generate_basic_suggestions()
    
    def _parse_llm_questions(self, response: str) -> List[str]:
        """Parse LLM response to extract questions."""
        questions = []
        lines = response.strip().split('\n')
        
        for line in lines:
            line = line.strip()
            # Look for numbered questions (1. 2. etc.)
            if line and (line[0].isdigit() or line.startswith('- ')):
                # Remove number and clean up
                if '. ' in line:
                    question = line.split('. ', 1)[1].strip()
                elif line.startswith('- '):
                    question = line[2:].strip()
                else:
                    continue
                
                # Clean up the question - remove any extra text after the question mark
                if '?' in question:
                    question = question.split('?')[0] + '?'
                
                # Ensure it's a real question and not too long
                if question and len(question) > 10 and len(question) < 200 and question.endswith('?'):
                    questions.append(question)
        
        return questions[:10]  # Return max 10 questions
    
    def _generate_basic_suggestions(self) -> List[str]:
        """Generate basic suggestions when LLM is not available."""
        if not self.csv_loader.is_loaded():
            return ["Please load a CSV file first to get question suggestions."]
            
        metadata = self.csv_loader.get_metadata()
        if not metadata:
            return ["Dataset loaded but unable to generate suggestions."]
        
        suggestions = [
            "What is the summary of this dataset?",
            "How many rows and columns are in the data?",
            "What are the column names and their data types?",
        ]
        
        # Add column-specific suggestions
        if metadata.columns:
            first_col = metadata.columns[0]
            suggestions.extend([
                f"Tell me about the '{first_col}' column",
                f"What are the unique values in '{first_col}'?",
            ])
        
        # Add suggestions for numeric columns
        numeric_columns = [
            col for col, dtype in metadata.dtypes.items() 
            if 'int' in dtype.lower() or 'float' in dtype.lower()
        ]
        
        if numeric_columns:
            suggestions.append(f"What are the statistics for '{numeric_columns[0]}'?")
        
        # Add suggestions for categorical columns
        categorical_columns = [
            col for col, dtype in metadata.dtypes.items() 
            if dtype.lower() == 'object'
        ]
        
        if categorical_columns:
            suggestions.append(f"What are the value counts for '{categorical_columns[0]}'?")
        
        # Add search suggestion if we have text columns
        if categorical_columns:
            suggestions.append("Search for specific data in the dataset")
        
        return suggestions[:10]
    
    def get_column_suggestions(self, column_name: str) -> List[str]:
        """
        Get suggestions specific to a column.
        
        Args:
            column_name (str): Name of the column
            
        Returns:
            List[str]: Column-specific suggestions
        """
        if not self.csv_loader.is_loaded():
            return []
        
        column_info = self.csv_loader.get_column_info(column_name)
        if not column_info:
            return []
        
        suggestions = [
            f"Tell me about the '{column_name}' column",
            f"What are the unique values in '{column_name}'?",
        ]
        
        # Type-specific suggestions
        if 'int' in column_info.dtype.lower() or 'float' in column_info.dtype.lower():
            suggestions.extend([
                f"What are the statistics for '{column_name}'?",
                f"What is the average value of '{column_name}'?",
                f"What is the range of values in '{column_name}'?"
            ])
        elif column_info.dtype.lower() == 'object':
            suggestions.extend([
                f"What are the most common values in '{column_name}'?",
                f"How many unique values are in '{column_name}'?",
                f"Search for specific values in '{column_name}'"
            ])
        
        return suggestions
    
    def get_dataset_overview(self) -> Dict[str, Any]:
        """
        Get a comprehensive overview of the dataset for context building.
        
        Returns:
            Dict[str, Any]: Dataset overview information
        """
        if not self.csv_loader.is_loaded():
            return {"status": "no_data_loaded"}
        
        metadata = self.csv_loader.get_metadata()
        if not metadata:
            return {"status": "metadata_unavailable"}
        
        # Categorize columns by type
        numeric_columns = []
        text_columns = []
        datetime_columns = []
        
        for col, dtype in metadata.dtypes.items():
            if 'int' in dtype.lower() or 'float' in dtype.lower():
                numeric_columns.append(col)
            elif 'datetime' in dtype.lower():
                datetime_columns.append(col)
            else:
                text_columns.append(col)
        
        return {
            "status": "loaded",
            "file_name": metadata.file_name,
            "shape": metadata.shape,
            "total_missing_values": sum(metadata.null_counts.values()),
            "memory_usage_kb": metadata.memory_usage / 1024,
            "column_types": {
                "numeric": numeric_columns,
                "text": text_columns,
                "datetime": datetime_columns
            },
            "sample_data_available": len(metadata.sample_data) > 0
        } 