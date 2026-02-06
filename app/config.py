"""Application configuration"""
import logging
import sys

# Database settings
DATABASE_NAME = "shortener.db"

# URL settings
BASE_URL = "http://localhost:8000"
SHORT_CODE_LENGTH = 6

# Logging configuration
def setup_logging():
    """Configure application logging"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(sys.stdout),
            logging.FileHandler('app.log')
        ]
    )
    return logging.getLogger(__name__)

logger = setup_logging()