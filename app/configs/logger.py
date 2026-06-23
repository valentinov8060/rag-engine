import os
import sys
from loguru import logger

# Make directory for logs if it doesn't exist
LOG_DIR = "logs"
os.makedirs(LOG_DIR, exist_ok=True)

# Remove any existing loggers to avoid duplicate logs
logger.remove()

# 1. Show logs in the console with a custom format
logger.add(
    sys.stdout,
    format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
    level="INFO",
)

# 2. Save logs to a file (automatically rotate when file size reaches 10 MB)
logger.add(
    os.path.join(LOG_DIR, "app.log"),
    format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
    level="DEBUG",
    rotation="10 MB",
    retention="10 days",
    compression="zip",
)