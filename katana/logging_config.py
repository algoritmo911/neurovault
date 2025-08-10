import logging
import sys
from config import settings

def setup_logging():
    """
    Configures the logging for the application.
    """
    logging.basicConfig(
        level=settings.LOG_LEVEL,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[
            logging.FileHandler(settings.LOG_FILE),
            logging.StreamHandler(sys.stdout)
        ]
    )

def get_logger(name: str):
    """
    Returns a logger instance.
    """
    return logging.getLogger(name)
