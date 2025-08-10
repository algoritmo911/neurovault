# Katana AI - Setup and Deployment Guide

This guide provides detailed instructions for setting up, configuring, running, and deploying the Katana AI document indexing system.

## 1. Prerequisites

- Python 3.10+
- `pip` for package management

## 2. Installation

### 2.1. Clone the Repository
```bash
git clone https://github.com/algoritmo911/katana-ai.git
cd katana-ai
```

### 2.2. Create a Virtual Environment (Recommended)
```bash
python3 -m venv venv
source venv/bin/activate
# On Windows, use: venv\Scripts\activate
```

### 2.3. Install Dependencies
Install all required Python libraries using the `requirements.txt` file.
```bash
pip install -r requirements.txt
```

## 3. Configuration

Configuration is managed in the `config/settings.py` file. You can edit this file directly or set environment variables for the specified values.

### 3.1. Google Drive API Credentials

This is the most critical setup step. The application needs OAuth 2.0 credentials to access your Google Drive data securely.

1.  **Go to the Google Cloud Console:** [https://console.cloud.google.com/](https://console.cloud.google.com/)
2.  **Create a new project** or select an existing one.
3.  **Enable the Google Drive API:**
    - In the navigation menu, go to `APIs & Services > Library`.
    - Search for "Google Drive API" and click **Enable**.
4.  **Configure the OAuth Consent Screen:**
    - Go to `APIs & Services > OAuth consent screen`.
    - Choose **External** and click **Create**.
    - Fill in the required fields (App name, User support email, Developer contact information). You can leave most fields blank for testing. Click **Save and Continue**.
    - On the Scopes page, click **Add or Remove Scopes**. Find the scope `.../auth/drive.readonly`, check the box, and click **Update**.
    - On the Test users page, click **Add Users** and add the Google account you will use to authenticate.
5.  **Create Credentials:**
    - Go to `APIs & Services > Credentials`.
    - Click **Create Credentials > OAuth client ID**.
    - Select **Desktop app** as the Application type.
    - Give it a name (e.g., "Katana AI Client").
    - Click **Create**. A pop-up will show your Client ID and Client Secret. Click **Download JSON**.
6.  **Save the Credentials File:**
    - Rename the downloaded file to `credentials.json`.
    - Place this file inside the `config/` directory at the root of the project. The final path should be `config/credentials.json`.

### 3.2. Application Settings (`config/settings.py`)

- **`GOOGLE_DRIVE_FOLDER_ID`**: The ID of the Google Drive folder you want to index. You can get this from the folder's URL. For `https://drive.google.com/drive/folders/1a2b3c_4d5e`, the ID is `1a2b3c_4d5e`.
- **`DOWNLOAD_DIR`**: The local directory where files will be downloaded. Defaults to `downloaded_files`.
- **`INDEX_DIR`**: The directory where the Whoosh search index will be stored. Defaults to `indexdir`.
- **`LOG_FILE`**: Path to the log file. Defaults to `katana.log`.
- **`LOG_LEVEL`**: The logging level (e.g., "INFO", "DEBUG", "WARNING").

## 4. Running the Application

### 4.1. First-Time Authentication

The very first time you run any part of the application that accesses Google Drive, it will open a web browser and ask you to authorize access to your Google Account.
- Select the account you added as a "Test user" in the consent screen setup.
- Grant the requested permissions.
After successful authorization, a `config/token.json` file will be created. This token will be used for all subsequent runs, so you won't need to authorize again unless you change the API scopes or delete the token.

### 4.2. Running the Indexing Process

To synchronize files from Google Drive and build the search index, run the `run_indexing.py` script.

```bash
python scripts/run_indexing.py
```
You should run this script periodically to keep the search index up-to-date with the contents of the Google Drive folder.

### 4.3. Running the API Server

To start the REST API, use `uvicorn`.

```bash
uvicorn katana.api:app --host 0.0.0.0 --port 8000 --reload
```
- `--reload`: Enables auto-reload for development. Do not use in production.
- The API documentation will be available at `http://localhost:8000/docs`.

### 4.4. Running Tests

To verify that all components are working correctly, run the unit tests:

```bash
python3 -m unittest discover tests
```

## 5. Deployment and Maintenance

### 5.1. Deployment Strategy

For a production environment, it is recommended to run the FastAPI application using a production-grade ASGI server like Gunicorn with Uvicorn workers.

**Example Gunicorn command:**
```bash
gunicorn katana.api:app -w 4 -k uvicorn.workers.UvicornWorker -b 0.0.0.0:8000
```
- `-w 4`: Specifies 4 worker processes. Adjust based on your server's CPU cores.
- `-k uvicorn.workers.UvicornWorker`: Uses Uvicorn to manage the workers.

It is also highly recommended to containerize the application using **Docker** for portability and ease of deployment. A `Dockerfile` and `docker-compose.yml` would be the next logical steps for productionizing this service.

### 5.2. Zero-Downtime Updates

The current `Indexer` implementation rebuilds the index in place. For true zero-downtime updates, a blue-green indexing strategy can be implemented:
1. The indexing script builds a new index in a separate directory (e.g., `indexdir_new`).
2. Once the new index is complete, the application atomically swaps to reading from the new index.
3. The old index directory can then be safely deleted.

### 5.3. Monitoring and Logging
- **Logging:** All application events are logged to `katana.log` (and the console). Monitor this file for errors or unexpected behavior.
- **Monitoring:** For production, integrate a proper monitoring solution. Key metrics to watch would be:
    - API endpoint latency and error rates.
    - Search query performance.
    - CPU and memory usage during the indexing process.
