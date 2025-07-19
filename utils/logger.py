"""
Logger Utility Module

This module provides logging utilities for the CSV agent system.
"""

import logging
import sys
from typing import Optional
from pathlib import Path
from datetime import datetime


class CSVAgentLogger:
    """
    Logger for the CSV agent system.
    
    Provides structured logging with different levels and output options.
    """
    
    def __init__(
        self,
        name: str = "csv_agent",
        level: str = "INFO",
        log_file: Optional[str] = None,
        console_output: bool = True
    ):
        """
        Initialize the logger.
        
        Args:
            name (str): Logger name
            level (str): Logging level
            log_file (Optional[str]): Path to log file
            console_output (bool): Whether to output to console
        """
        self.logger = logging.getLogger(name)
        self.logger.setLevel(getattr(logging, level.upper()))
        
        # Clear existing handlers
        self.logger.handlers.clear()
        
        # Create formatter
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        
        # Console handler
        if console_output:
            console_handler = logging.StreamHandler(sys.stdout)
            console_handler.setFormatter(formatter)
            self.logger.addHandler(console_handler)
        
        # File handler
        if log_file:
            file_handler = logging.FileHandler(log_file)
            file_handler.setFormatter(formatter)
            self.logger.addHandler(file_handler)
    
    def info(self, message: str, **kwargs) -> None:
        """Log info message."""
        self.logger.info(message, **kwargs)
    
    def warning(self, message: str, **kwargs) -> None:
        """Log warning message."""
        self.logger.warning(message, **kwargs)
    
    def error(self, message: str, **kwargs) -> None:
        """Log error message."""
        self.logger.error(message, **kwargs)
    
    def debug(self, message: str, **kwargs) -> None:
        """Log debug message."""
        self.logger.debug(message, **kwargs)
    
    def log_csv_load(self, file_path: str, success: bool, metadata: dict = None) -> None:
        """Log CSV loading event."""
        if success:
            self.info(f"Successfully loaded CSV: {file_path}")
            if metadata:
                self.debug(f"CSV metadata: {metadata}")
        else:
            self.error(f"Failed to load CSV: {file_path}")
    
    def log_query(self, question: str, response_time: float, success: bool) -> None:
        """Log query execution."""
        if success:
            self.info(f"Query processed in {response_time:.2f}s: {question[:100]}...")
        else:
            self.error(f"Query failed after {response_time:.2f}s: {question[:100]}...")
    
    def log_tool_execution(self, tool_name: str, execution_time: float, success: bool) -> None:
        """Log tool execution."""
        if success:
            self.debug(f"Tool '{tool_name}' executed in {execution_time:.3f}s")
        else:
            self.warning(f"Tool '{tool_name}' failed after {execution_time:.3f}s")


def get_logger(
    name: str = "csv_agent",
    level: str = "INFO",
    log_to_file: bool = False
) -> CSVAgentLogger:
    """
    Get a configured logger instance.
    
    Args:
        name (str): Logger name
        level (str): Logging level
        log_to_file (bool): Whether to log to file
        
    Returns:
        CSVAgentLogger: Configured logger
    """
    log_file = None
    if log_to_file:
        log_dir = Path("logs")
        log_dir.mkdir(exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        log_file = str(log_dir / f"csv_agent_{timestamp}.log")
    
    return CSVAgentLogger(
        name=name,
        level=level,
        log_file=log_file,
        console_output=True
    ) 