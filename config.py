import os
from dotenv import load_dotenv

load_dotenv()

# API Keys & IDs
PLATE_REC_API_KEY = os.getenv("PLATE_REC_API_KEY")
DRIVE_FOLDER_ID = os.getenv("DRIVE_FOLDER_ID")
FIREBASE_BUCKET = os.getenv("FIREBASE_BUCKET")

# Dynamic Paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
FIREBASE_KEY_PATH = os.path.join(BASE_DIR, "keys", "firebase_key.json")
DRIVE_KEY_PATH = os.path.join(BASE_DIR, "keys", "google_drive_key.json")

# System Settings
CHECK_INTERVAL = int(os.getenv("CHECK_INTERVAL", 60))

API_RATE_LIMIT_DELAY = 0.2  # 0.2s ensures we stay well under 8 calls/sec