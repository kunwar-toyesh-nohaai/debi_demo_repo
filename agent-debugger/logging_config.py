"""Logging configuration for the debugging agent."""

import logging
import os
from datetime import datetime
from pathlib import Path


def setup_logging(log_dir: str = None) -> logging.Logger:
    """
    Set up logging to both console and file.
    
    Args:
        log_dir: Directory to store log files. Defaults to agent-debugger directory.
        
    Returns:
        Configured logger instance.
    """
    # Get the base directory
    if log_dir is None:
        log_dir = Path(__file__).parent
    
    # Create logs directory if it doesn't exist
    log_dir = Path(log_dir)
    log_dir.mkdir(exist_ok=True)
    
    # Create log file with timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_file = log_dir / f"agent_debugger_{timestamp}.log"
    
    # Create logger
    logger = logging.getLogger("agent_debugger")
    logger.setLevel(logging.DEBUG)
    
    # Remove existing handlers to avoid duplicates
    logger.handlers = []
    
    # Create formatters
    detailed_formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    console_formatter = logging.Formatter(
        '%(levelname)s - %(message)s'
    )
    
    # File handler - logs everything
    file_handler = logging.FileHandler(log_file, encoding='utf-8')
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(detailed_formatter)
    logger.addHandler(file_handler)
    
    # Console handler - logs INFO and above
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(console_formatter)
    logger.addHandler(console_handler)
    
    # Also capture LangChain's verbose output by setting up a handler for it
    # LangChain's verbose output goes to stdout, so we'll capture it via logging
    
    # Log the log file location
    logger.info(f"Logging to file: {log_file}")
    
    return logger

