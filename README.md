# Katana AI - Google Drive Indexer

This project provides a system for scanning, analyzing, and indexing documents from a shared Google Drive folder to enable intelligent search.

## Setup

1.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

2.  **Google Drive API Credentials:**
    - Enable the Google Drive API in the Google Cloud Console.
    - Create credentials for a "Desktop application".
    - Download the credentials file and save it as `config/credentials.json`.
    - The first time you run the application, you will be prompted to authorize access to your Google Account. A `config/token.json` file will be created to store the authorization token for future runs.
