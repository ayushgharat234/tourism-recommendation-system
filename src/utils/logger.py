import os
import logging
from logging.handlers import RotatingFileHandler
from datetime import datetime

def setup_logger(name: str, log_level=logging.INFO):
    """Setup a logger with file and console handlers."""
    # Create logs directory if it doesn't exist
    log_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'logs')
    os.makedirs(log_dir, exist_ok=True)
    
    # Create logger
    logger = logging.getLogger(name)
    logger.setLevel(log_level)
    
    # Create formatters
    file_formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    console_formatter = logging.Formatter(
        '%(levelname)s - %(message)s'
    )
    
    # Create file handler
    timestamp = datetime.now().strftime('%Y%m%d')
    file_handler = RotatingFileHandler(
        os.path.join(log_dir, f'{name}_{timestamp}.log'),
        maxBytes=10*1024*1024,  # 10MB
        backupCount=5
    )
    file_handler.setLevel(log_level)
    file_handler.setFormatter(file_formatter)
    
    # Create console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(log_level)
    console_handler.setFormatter(console_formatter)
    
    # Add handlers to logger
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    
    return logger

# Create loggers for different components
app_logger = setup_logger('app')
db_logger = setup_logger('database')
ai_logger = setup_logger('ai')
osm_logger = setup_logger('osm') 