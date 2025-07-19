"""
CSV Data Visualizer Module

This module provides visualization capabilities for CSV analytics with
support for different chart types and analysis methods.
"""

import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
from typing import Optional, List, Dict, Any, Literal
from pathlib import Path
import warnings

# Set style for better-looking plots
plt.style.use('default')
sns.set_palette("husl")
warnings.filterwarnings('ignore', category=FutureWarning)

AnalysisType = Literal["distribution", "sum", "average", "count"]


class CSVVisualizer:
    """
    Provides visualization capabilities for CSV data analytics.
    
    Supports various chart types including bar charts, histograms, 
    pie charts, and distribution plots.
    """
    
    def __init__(self, figsize: tuple = (12, 8)):
        """
        Initialize the visualizer.
        
        Args:
            figsize (tuple): Default figure size for plots
        """
        self.figsize = figsize
        self.colors = sns.color_palette("husl", 12)
    
    def analyze_and_plot(
        self, 
        dataframe: pd.DataFrame, 
        dimension: str, 
        measure: str, 
        analysis_type: AnalysisType,
        title: Optional[str] = None,
        save_path: Optional[str] = None,
        show_plot: bool = True
    ) -> Dict[str, Any]:
        """
        Analyze data and create visualization based on user preferences.
        
        Args:
            dataframe (pd.DataFrame): The data to analyze
            dimension (str): Column name for grouping/categorizing
            measure (str): Column name for the metric to analyze
            analysis_type (AnalysisType): Type of analysis (distribution, sum, average, count)
            title (Optional[str]): Custom title for the plot
            save_path (Optional[str]): Path to save the plot image
            show_plot (bool): Whether to display the plot
            
        Returns:
            Dict[str, Any]: Analysis results and statistics
        """
        
        # Validate inputs
        # For distribution analysis, dimension can be empty
        if analysis_type != "distribution" and analysis_type != "count" and dimension not in dataframe.columns:
            raise ValueError(f"Dimension '{dimension}' not found in dataframe columns: {list(dataframe.columns)}")
        
        # For count analysis, measure can be empty  
        if analysis_type != "count" and measure not in dataframe.columns:
            raise ValueError(f"Measure '{measure}' not found in dataframe columns: {list(dataframe.columns)}")
        
        # Specific validation for count analysis
        if analysis_type == "count" and dimension not in dataframe.columns:
            raise ValueError(f"Dimension '{dimension}' not found in dataframe columns: {list(dataframe.columns)}")
        
        # Specific validation for distribution analysis
        if analysis_type == "distribution" and measure not in dataframe.columns:
            raise ValueError(f"Measure '{measure}' not found in dataframe columns: {list(dataframe.columns)}")
        
        # Perform analysis based on type
        if analysis_type == "distribution":
            return self._plot_distribution(dataframe, measure, title, save_path, show_plot)
        elif analysis_type == "sum":
            return self._plot_aggregation(dataframe, dimension, measure, "sum", title, save_path, show_plot)
        elif analysis_type == "average":
            return self._plot_aggregation(dataframe, dimension, measure, "mean", title, save_path, show_plot)
        elif analysis_type == "count":
            return self._plot_count(dataframe, dimension, title, save_path, show_plot)
        else:
            raise ValueError(f"Unsupported analysis type: {analysis_type}")
    
    def _plot_distribution(
        self, 
        dataframe: pd.DataFrame, 
        measure: str, 
        title: Optional[str] = None,
        save_path: Optional[str] = None,
        show_plot: bool = True
    ) -> Dict[str, Any]:
        """Plot distribution of a measure."""
        
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=self.figsize)
        
        # Histogram
        ax1.hist(dataframe[measure].dropna(), bins=20, alpha=0.7, color=self.colors[0], edgecolor='black')
        ax1.set_title(f'Distribution of {measure}')
        ax1.set_xlabel(measure)
        ax1.set_ylabel('Frequency')
        ax1.grid(True, alpha=0.3)
        
        # Box plot
        ax2.boxplot(dataframe[measure].dropna(), patch_artist=True, 
                   boxprops=dict(facecolor=self.colors[1], alpha=0.7))
        ax2.set_title(f'Box Plot of {measure}')
        ax2.set_ylabel(measure)
        ax2.grid(True, alpha=0.3)
        
        if title:
            fig.suptitle(title, fontsize=16, fontweight='bold')
        
        plt.tight_layout()
        
        # Calculate statistics
        stats = {
            'mean': dataframe[measure].mean(),
            'median': dataframe[measure].median(),
            'std': dataframe[measure].std(),
            'min': dataframe[measure].min(),
            'max': dataframe[measure].max(),
            'count': dataframe[measure].count()
        }
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
        
        if show_plot:
            plt.show()
        else:
            plt.close()
        
        return {
            'analysis_type': 'distribution',
            'measure': measure,
            'statistics': stats,
            'plot_type': 'histogram_boxplot'
        }
    
    def _plot_aggregation(
        self, 
        dataframe: pd.DataFrame, 
        dimension: str, 
        measure: str, 
        agg_func: str,
        title: Optional[str] = None,
        save_path: Optional[str] = None,
        show_plot: bool = True
    ) -> Dict[str, Any]:
        """Plot aggregated data (sum/average) by dimension."""
        
        # Perform aggregation
        agg_data = dataframe.groupby(dimension)[measure].agg(agg_func).reset_index()
        agg_data = agg_data.sort_values(measure, ascending=False)
        
        # Create plot
        fig, ax = plt.subplots(figsize=self.figsize)
        
        # Choose plot type based on number of categories
        n_categories = len(agg_data)
        
        if n_categories <= 10:
            # Bar chart for <= 10 categories
            bars = ax.bar(agg_data[dimension], agg_data[measure], 
                         color=self.colors[:n_categories], alpha=0.8, edgecolor='black')
            
            # Add value labels on bars
            for bar in bars:
                height = bar.get_height()
                ax.text(bar.get_x() + bar.get_width()/2., height,
                       f'{height:.2f}', ha='center', va='bottom')
            
            plt.xticks(rotation=45, ha='right')
            
        else:
            # Horizontal bar chart for > 10 categories (top 15)
            top_data = agg_data.head(15)
            bars = ax.barh(top_data[dimension], top_data[measure], 
                          color=self.colors[0], alpha=0.8)
            
            # Add value labels
            for i, bar in enumerate(bars):
                width = bar.get_width()
                ax.text(width, bar.get_y() + bar.get_height()/2.,
                       f'{width:.2f}', ha='left', va='center')
            
            ax.set_title(f'Top 15 {dimension} by {agg_func.title()} {measure}')
        
        ax.set_xlabel(measure if n_categories <= 10 else f'{agg_func.title()} of {measure}')
        ax.set_ylabel(dimension if n_categories <= 10 else dimension)
        
        if not title and n_categories <= 10:
            title = f'{agg_func.title()} of {measure} by {dimension}'
        
        if title:
            ax.set_title(title, fontweight='bold')
        
        ax.grid(True, alpha=0.3)
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
        
        if show_plot:
            plt.show()
        else:
            plt.close()
        
        return {
            'analysis_type': agg_func,
            'dimension': dimension,
            'measure': measure,
            'data': agg_data.to_dict('records'),
            'summary': {
                'total_categories': n_categories,
                'highest_value': agg_data[measure].max(),
                'lowest_value': agg_data[measure].min(),
                'average_value': agg_data[measure].mean()
            }
        }
    
    def _plot_count(
        self, 
        dataframe: pd.DataFrame, 
        dimension: str, 
        title: Optional[str] = None,
        save_path: Optional[str] = None,
        show_plot: bool = True
    ) -> Dict[str, Any]:
        """Plot count of occurrences by dimension."""
        
        # Count occurrences
        count_data = dataframe[dimension].value_counts().reset_index()
        count_data.columns = [dimension, 'count']
        
        # Create plot
        fig, ax = plt.subplots(figsize=self.figsize)
        
        n_categories = len(count_data)
        
        if n_categories <= 8:
            # Pie chart for <= 8 categories
            wedges, texts, autotexts = ax.pie(count_data['count'], labels=count_data[dimension], 
                                             autopct='%1.1f%%', startangle=90,
                                             colors=self.colors[:n_categories])
            
            # Enhance text appearance
            for autotext in autotexts:
                autotext.set_color('white')
                autotext.set_fontweight('bold')
            
            ax.set_title(f'Distribution of {dimension}', fontweight='bold')
            
        else:
            # Bar chart for > 8 categories (top 15)
            top_data = count_data.head(15)
            bars = ax.bar(range(len(top_data)), top_data['count'], 
                         color=self.colors[0], alpha=0.8, edgecolor='black')
            
            # Add value labels
            for i, bar in enumerate(bars):
                height = bar.get_height()
                ax.text(bar.get_x() + bar.get_width()/2., height,
                       f'{int(height)}', ha='center', va='bottom')
            
            ax.set_xticks(range(len(top_data)))
            ax.set_xticklabels(top_data[dimension], rotation=45, ha='right')
            ax.set_xlabel(dimension)
            ax.set_ylabel('Count')
            ax.set_title(f'Top 15 {dimension} by Count' if n_categories > 15 else f'Count by {dimension}', 
                        fontweight='bold')
            ax.grid(True, alpha=0.3)
        
        if title:
            ax.set_title(title, fontweight='bold')
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
        
        if show_plot:
            plt.show()
        else:
            plt.close()
        
        return {
            'analysis_type': 'count',
            'dimension': dimension,
            'data': count_data.to_dict('records'),
            'summary': {
                'total_categories': n_categories,
                'total_records': count_data['count'].sum(),
                'most_frequent': count_data.iloc[0][dimension],
                'most_frequent_count': count_data.iloc[0]['count']
            }
        }
    
    def interactive_analysis_menu(
        self, 
        dataframe: pd.DataFrame, 
        measures: List[str], 
        dimensions: List[str]
    ) -> None:
        """
        Interactive menu for choosing analysis parameters.
        
        Args:
            dataframe (pd.DataFrame): The data to analyze
            measures (List[str]): Available measure columns
            dimensions (List[str]): Available dimension columns
        """
        
        print("\n🎨 CSV Data Visualization Menu")
        print("=" * 50)
        
        # Display available options
        print(f"\n📊 Available Measures: {', '.join(measures)}")
        print(f"📂 Available Dimensions: {', '.join(dimensions)}")
        
        print(f"\n📈 Analysis Types:")
        print("1. distribution - Show distribution of a measure")
        print("2. sum - Sum of measure by dimension")
        print("3. average - Average of measure by dimension") 
        print("4. count - Count occurrences by dimension")
        
        try:
            # Get user input
            analysis_type = input(f"\n🔍 Choose analysis type (distribution/sum/average/count): ").strip().lower()
            
            if analysis_type not in ["distribution", "sum", "average", "count"]:
                print("❌ Invalid analysis type!")
                return
            
            if analysis_type == "distribution":
                print(f"\n📊 Choose a measure to analyze: {', '.join(measures)}")
                measure = input("📊 Measure: ").strip()
                if measure not in measures:
                    print(f"❌ Invalid measure! Choose from: {measures}")
                    return
                
                result = self.analyze_and_plot(dataframe, "", measure, analysis_type)
                
            elif analysis_type == "count":
                print(f"\n📂 Choose a dimension to analyze: {', '.join(dimensions)}")
                dimension = input("📂 Dimension: ").strip()
                if dimension not in dimensions:
                    print(f"❌ Invalid dimension! Choose from: {dimensions}")
                    return
                
                result = self.analyze_and_plot(dataframe, dimension, "", analysis_type)
                
            else:  # sum or average
                print(f"\n📂 Choose a dimension to group by: {', '.join(dimensions)}")
                dimension = input("📂 Dimension: ").strip()
                if dimension not in dimensions:
                    print(f"❌ Invalid dimension! Choose from: {dimensions}")
                    return
                
                print(f"\n📊 Choose a measure to analyze: {', '.join(measures)}")
                measure = input("📊 Measure: ").strip()
                if measure not in measures:
                    print(f"❌ Invalid measure! Choose from: {measures}")
                    return
                
                result = self.analyze_and_plot(dataframe, dimension, measure, analysis_type)
            
            # Display results summary
            print(f"\n✅ Analysis complete!")
            if 'summary' in result:
                print(f"📊 Summary: {result['summary']}")
                
        except KeyboardInterrupt:
            print(f"\n👋 Visualization cancelled by user.")
        except Exception as e:
            print(f"❌ Error during visualization: {e}")


def create_sample_plots(dataframe: pd.DataFrame, measures: List[str], dimensions: List[str]) -> None:
    """
    Create sample plots to demonstrate visualization capabilities.
    
    Args:
        dataframe (pd.DataFrame): The data to visualize
        measures (List[str]): Available measure columns  
        dimensions (List[str]): Available dimension columns
    """
    
    visualizer = CSVVisualizer()
    
    print(f"\n🎨 Creating Sample Visualizations...")
    print("=" * 50)
    
    # Sample 1: Distribution of first measure
    if measures:
        print(f"📊 1. Distribution of {measures[0]}")
        visualizer.analyze_and_plot(dataframe, "", measures[0], "distribution", show_plot=True)
    
    # Sample 2: Sum by first dimension  
    if measures and dimensions:
        print(f"📊 2. Sum of {measures[0]} by {dimensions[0]}")
        visualizer.analyze_and_plot(dataframe, dimensions[0], measures[0], "sum", show_plot=True)
    
    # Sample 3: Count by first dimension
    if dimensions:
        print(f"📊 3. Count by {dimensions[0]}")
        visualizer.analyze_and_plot(dataframe, dimensions[0], "", "count", show_plot=True)