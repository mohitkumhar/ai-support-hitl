import os
import logging
from logging.handlers import RotatingFileHandler

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# 2. Point to the logs folder (going up one level from 'app')
# Result: C:\...\ai_chatbot_with_memory_and_tools\logs\app.log
LOG_FILE = os.path.join(BASE_DIR, "..", "logs", "app.log")
# LOG_FILE = "../logs/app.log"
# LOG_FILE = "logs/app.log"


handler = RotatingFileHandler(
        LOG_FILE,
        maxBytes=5*1024*1024,
        backupCount=10
    )

formatter = logging.Formatter(
    fmt='%(asctime)s - %(name)s - %(levelname)s - %(filename)s:%(lineno)d - %(funcName)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)


handler.setFormatter(formatter)

logging.basicConfig(
    level=logging.INFO,
    handlers=[handler]
)

logger = logging.getLogger("ai-support-hitl")
