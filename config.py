import os
from dotenv import load_dotenv

load_dotenv()

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
LOG_FILE = "logs/logs.csv"
DATA_PATH = "data/"