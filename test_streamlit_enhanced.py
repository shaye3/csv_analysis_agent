"""
Test script to demonstrate the enhanced Streamlit application
with automatic visualizations when CSV is uploaded.
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import sys
import os
from pathlib import Path

def create_sample_data():
    """Create a comprehensive sample dataset for demonstration."""
    
    np.random.seed(42)
    n_samples = 500
    
    # Create sample data with good variety for visualizations
    data = {
        # Dimensions (categorical)
        'employee_id': range(1001, 1001 + n_samples),
        'department': np.random.choice(['Engineering', 'Marketing', 'Sales', 'HR', 'Finance', 'Operations'], n_samples),
        'city': np.random.choice(['New York', 'San Francisco', 'Chicago', 'Austin', 'Seattle', 'Boston', 'Denver'], n_samples),
        'education_level': np.random.choice(['Bachelor', 'Master', 'PhD', 'High School'], n_samples, p=[0.5, 0.3, 0.1, 0.1]),
        'employment_type': np.random.choice(['Full-time', 'Part-time', 'Contract'], n_samples, p=[0.8, 0.15, 0.05]),
        
        # Measures (numerical)
        'salary': np.random.normal(75000, 20000, n_samples).astype(int),
        'years_experience': np.random.exponential(5, n_samples).astype(int),
        'performance_rating': np.random.normal(3.5, 0.8, n_samples),
        'hours_per_week': np.random.normal(42, 8, n_samples),
        'vacation_days': np.random.poisson(15, n_samples),
        
        # Mixed data
        'age': np.random.normal(35, 10, n_samples).astype(int),
    }
    
    # Add some realistic constraints
    data['salary'] = np.clip(data['salary'], 35000, 150000)
    data['years_experience'] = np.clip(data['years_experience'], 0, 40)
    data['performance_rating'] = np.clip(data['performance_rating'], 1.0, 5.0)
    data['hours_per_week'] = np.clip(data['hours_per_week'], 20, 60)
    data['vacation_days'] = np.clip(data['vacation_days'], 5, 30)
    data['age'] = np.clip(data['age'], 22, 65)
    
    # Add correlations for interesting analysis
    # Higher education -> higher salary
    education_bonus = {'High School': 0, 'Bachelor': 10000, 'Master': 20000, 'PhD': 35000}
    for i, edu in enumerate(data['education_level']):
        data['salary'][i] += education_bonus[edu]
    
    # Experience correlates with salary
    for i in range(n_samples):
        data['salary'][i] += data['years_experience'][i] * 1000
    
    # Add some missing values for realistic data
    missing_indices = np.random.choice(n_samples, size=int(n_samples * 0.02), replace=False)
    for idx in missing_indices:
        data['performance_rating'][idx] = np.nan
    
    # Create hire dates
    start_date = datetime(2018, 1, 1)
    data['hire_date'] = [
        (start_date + timedelta(days=np.random.randint(0, 2000))).strftime('%Y-%m-%d')
        for _ in range(n_samples)
    ]
    
    # Create names
    first_names = ['Alice', 'Bob', 'Carol', 'David', 'Eve', 'Frank', 'Grace', 'Henry', 'Ivy', 'Jack']
    last_names = ['Smith', 'Johnson', 'Williams', 'Brown', 'Jones', 'Garcia', 'Miller', 'Davis', 'Rodriguez', 'Martinez']
    data['name'] = [
        f"{np.random.choice(first_names)} {np.random.choice(last_names)}"
        for _ in range(n_samples)
    ]
    
    return pd.DataFrame(data)

def main():
    """Create sample data and provide instructions for testing."""
    
    print("🚀 Creating Enhanced Sample Data for Streamlit Testing")
    print("=" * 60)
    
    # Create sample data
    df = create_sample_data()
    
    # Save to CSV
    csv_file = "enhanced_sample_data.csv"
    df.to_csv(csv_file, index=False)
    
    print(f"✅ Created {csv_file} with {len(df)} rows and {len(df.columns)} columns")
    print()
    
    # Show data preview
    print("📊 Data Preview:")
    print(df.head())
    print()
    
    # Show column info
    print("📋 Column Information:")
    for col in df.columns:
        dtype = df[col].dtype
        unique_vals = df[col].nunique()
        missing = df[col].isnull().sum()
        print(f"  • {col}: {dtype}, {unique_vals} unique values, {missing} missing")
    print()
    
    print("🎨 This dataset includes:")
    print("✅ Multiple measures for distribution analysis (salary, performance, etc.)")
    print("✅ Categorical dimensions for grouping (department, education, etc.)")  
    print("✅ Correlated variables for correlation analysis")
    print("✅ Some missing values for data quality insights")
    print("✅ Realistic business data structure")
    print()
    
    print("🌐 To test the enhanced Streamlit app:")
    print("1. Run: python run_streamlit.py")
    print("2. Open http://localhost:8501 in your browser")
    print("3. Enter your OpenAI API key")
    print("4. Upload the generated enhanced_sample_data.csv file")
    print("5. Enjoy the automatic visualizations! 📊✨")
    print()
    
    print("📈 Expected automatic visualizations:")
    print("  📊 Distribution tab: Histograms for salary, performance_rating, etc.")
    print("  🔗 Correlation tab: Correlation matrix showing relationships")
    print("  📂 Categorical tab: Pie/bar charts for department, education, etc.")
    print("  📋 Summary tab: Statistical summaries and data quality insights")

if __name__ == "__main__":
    main() 