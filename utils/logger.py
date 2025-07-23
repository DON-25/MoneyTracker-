import logging
import os
from datetime import datetime

def setup_logger():
    """Configure logging for MoneyTracker with file and console output."""
    #Create logs directory if it doesn't exist
    log_dir='logs'
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)

    #Create a logger   
    logger= logging.getlogger("MoneyTracker")
    logger.setlevel(logging.DEBUG)

    #Create file handler with timestamped log file
    log_file = os.path.join(log_dir, f"moneytracker_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log")
    file_handler = logging.FileHandler(log_file)
    file_handler.setLevel(logging.DEBUG)

    # Create console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)

    # Create formatter
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    file_handler.setFormatter(formatter)
    console_handler.setFormatter(formatter)
    
    # Add handlers to logger
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

    return logger

# Initialize logger
logger = setup_logger()


