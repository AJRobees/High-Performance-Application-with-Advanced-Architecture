"""
Shared logging configuration for the  High-Performance Application with Advanced Architecture.

This module creates and configures named loggers that write application
events to module-specific log files in the project's logs directory.
"""
from pathlib import Path
import logging

def get_logger(source):
    """
    Create and configure a logger that writes to a module-specific file.

    Args:
        source: The logger name, also used as the log filename.

    Creates the project's logs directory if it does not exist, configures
    the logger at INFO level, and attaches a file handler with a formatter
    that records the timestamp, severity level, logger name, and message.

    Returns:
        logging.Logger: The configured logger instance.
    """
    project_dir = Path(__file__).parents[1]  
    log_dir = project_dir/"logs"

    log_file = log_dir/f"{source}.log"

    if not log_dir.exists():
        log_dir.mkdir(exist_ok=True)

    logger = logging.getLogger(source)
    logger.setLevel(logging.INFO)

    handler = logging.FileHandler(log_file)
    formatter = logging.Formatter("%(asctime)s | %(levelname)s | %(name)s | %(message)s")

    handler.setFormatter(formatter)
    
    if not logger.handlers:
        logger.addHandler(handler)

    return logger
