"""
Tests for CSV Loader Module
"""

import pytest
import pandas as pd
import tempfile
import os
from pathlib import Path

from data_io.csv_loader import CSVLoader
from models.config import CSVLoaderConfig


class TestCSVLoader:
    """Test cases for CSVLoader class."""
    
    @pytest.fixture
    def sample_csv_file(self):
        """Create a temporary CSV file for testing."""
        data = {
            'name': ['Alice', 'Bob', 'Charlie'],
            'age': [25, 30, 35],
            'city': ['New York', 'London', 'Paris'],
            'salary': [50000, 60000, 70000]
        }
        df = pd.DataFrame(data)
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            df.to_csv(f.name, index=False)
            yield f.name
        
        # Cleanup
        os.unlink(f.name)
    
    @pytest.fixture
    def csv_loader(self):
        """Create a CSVLoader instance."""
        return CSVLoader()
    
    def test_load_csv_success(self, csv_loader, sample_csv_file):
        """Test successful CSV loading."""
        result = csv_loader.load_csv(sample_csv_file)
        
        assert result is True
        assert csv_loader.is_loaded()
        assert csv_loader.get_dataframe() is not None
        assert len(csv_loader.get_dataframe()) == 3
    
    def test_load_csv_file_not_found(self, csv_loader):
        """Test loading non-existent file."""
        result = csv_loader.load_csv("nonexistent.csv")
        assert result is False
        assert not csv_loader.is_loaded()
    
    def test_load_csv_wrong_extension(self, csv_loader):
        """Test loading file with wrong extension."""
        with tempfile.NamedTemporaryFile(suffix='.txt') as f:
            result = csv_loader.load_csv(f.name)
            assert result is False
    
    def test_get_metadata(self, csv_loader, sample_csv_file):
        """Test metadata generation."""
        csv_loader.load_csv(sample_csv_file)
        metadata = csv_loader.get_metadata()
        
        assert metadata is not None
        assert metadata.shape == (3, 4)
        assert set(metadata.columns) == {'name', 'age', 'city', 'salary'}
        assert metadata.file_name.endswith('.csv')
    
    def test_get_column_info(self, csv_loader, sample_csv_file):
        """Test column information retrieval."""
        csv_loader.load_csv(sample_csv_file)
        
        # Test existing column
        column_info = csv_loader.get_column_info('age')
        assert column_info is not None
        assert column_info.name == 'age'
        assert column_info.unique_count == 3
        
        # Test non-existent column
        column_info = csv_loader.get_column_info('nonexistent')
        assert column_info is None
    
    def test_search_data(self, csv_loader, sample_csv_file):
        """Test data searching."""
        csv_loader.load_csv(sample_csv_file)
        
        # Search for existing data
        results = csv_loader.search_data('Alice')
        assert len(results) == 1
        assert results.iloc[0]['name'] == 'Alice'
        
        # Search for non-existent data
        results = csv_loader.search_data('NonExistent')
        assert len(results) == 0
    
    def test_clear(self, csv_loader, sample_csv_file):
        """Test clearing loaded data."""
        csv_loader.load_csv(sample_csv_file)
        assert csv_loader.is_loaded()
        
        csv_loader.clear()
        assert not csv_loader.is_loaded()
        assert csv_loader.get_dataframe() is None
        assert csv_loader.get_metadata() is None


class TestCSVLoaderConfig:
    """Test cases for CSVLoaderConfig."""
    
    def test_default_config(self):
        """Test default configuration."""
        config = CSVLoaderConfig()
        
        assert config.max_file_size_mb == 100.0
        assert config.encoding == "utf-8"
        assert config.delimiter == ","
        assert config.enable_type_inference is True
    
    def test_custom_config(self):
        """Test custom configuration."""
        config = CSVLoaderConfig(
            max_file_size_mb=50.0,
            encoding="latin-1",
            delimiter=";",
            enable_type_inference=False
        )
        
        assert config.max_file_size_mb == 50.0
        assert config.encoding == "latin-1"
        assert config.delimiter == ";"
        assert config.enable_type_inference is False 