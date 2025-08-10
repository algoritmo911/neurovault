import os

# --- General Settings ---
# Base directory of the project
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))

# --- Google Drive Settings ---
# The ID of the Google Drive folder to index.
# Replace "YOUR_GOOGLE_DRIVE_FOLDER_ID" with your actual folder ID.
GOOGLE_DRIVE_FOLDER_ID = os.environ.get("GOOGLE_DRIVE_FOLDER_ID", "YOUR_GOOGLE_DRIVE_FOLDER_ID")

# Path to the Google API credentials file.
CREDENTIALS_PATH = os.path.join(BASE_DIR, "config", "credentials.json")

# Path to the Google API token file.
TOKEN_PATH = os.path.join(BASE_DIR, "config", "token.json")

# --- Synchronization Settings ---
# Local directory to store downloaded files.
DOWNLOAD_DIR = os.path.join(BASE_DIR, "downloaded_files")

# Path to the synchronization state file.
SYNC_STATE_PATH = os.path.join(BASE_DIR, "config", "sync_state.json")

# --- Indexer Settings ---
# Directory to store the Whoosh index.
INDEX_DIR = os.path.join(BASE_DIR, "indexdir")

# --- API Settings ---
# Host and port for the FastAPI application.
API_HOST = "0.0.0.0"
API_PORT = 8000

# --- Logging Settings ---
LOG_FILE = os.path.join(BASE_DIR, "katana.log")
LOG_LEVEL = "INFO"
