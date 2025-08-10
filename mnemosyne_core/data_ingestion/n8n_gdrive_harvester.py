"""
n8n Google Drive Harvester

This script is responsible for scanning a specified Google Drive folder for n8n
workflow files (JSON), detecting changes, and downloading new or updated files.
"""
import os
import json
import logging
from typing import List, Dict, Optional

from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Constants
SCOPES = ['https://www.googleapis.com/auth/drive.readonly']
GDRIVE_FOLDER_ID = 'YOUR_GOOGLE_DRIVE_FOLDER_ID_HERE'  # IMPORTANT: This must be configured
SERVICE_ACCOUNT_FILE = 'service_account.json'  # Path to the service account key file
CACHE_FILE = '.gdrive_cache.json'
DOWNLOAD_DIR = 'n8n_workflows'


def get_gdrive_service(credentials_path: str):
    """
    Authenticates with the Google Drive API using a service account.

    Args:
        credentials_path (str): The path to the service account JSON file.

    Returns:
        A Google Drive API service object, or None if authentication fails.
    """
    try:
        creds = Credentials.from_service_account_file(
            credentials_path, scopes=SCOPES)
        service = build('drive', 'v3', credentials=creds)
        logger.info("Successfully authenticated with Google Drive API.")
        return service
    except FileNotFoundError:
        logger.error(f"Service account key file not found at: {credentials_path}")
    except Exception as e:
        logger.error(f"An error occurred during Google Drive authentication: {e}")
    return None


def scan_gdrive_folder(service, folder_id: str) -> List[Dict]:
    """
    Scans a Google Drive folder for JSON files and returns their metadata.

    Args:
        service: The authenticated Google Drive API service object.
        folder_id (str): The ID of the Google Drive folder to scan.

    Returns:
        A list of dictionaries, where each dictionary contains the metadata
        of a file (id, name, modifiedTime, md5Checksum).
    """
    files = []
    page_token = None
    try:
        while True:
            response = service.files().list(
                q=f"mimeType='application/json' and '{folder_id}' in parents and trashed=false",
                fields='nextPageToken, files(id, name, modifiedTime, md5Checksum)',
                pageSize=100,
                pageToken=page_token
            ).execute()
            files.extend(response.get('files', []))
            page_token = response.get('nextPageToken', None)
            if page_token is None:
                break
        logger.info(f"Found {len(files)} JSON files in Google Drive folder '{folder_id}'.")
        return files
    except HttpError as error:
        logger.error(f"An error occurred while scanning Google Drive folder: {error}")
        return []


def load_cache(cache_file_path: str) -> Dict[str, str]:
    """
    Loads the file cache from a local JSON file.

    The cache maps file IDs to their md5Checksums.

    Args:
        cache_file_path (str): The path to the cache file.

    Returns:
        A dictionary with the cached data, or an empty dictionary if the
        file doesn't exist or is invalid.
    """
    if not os.path.exists(cache_file_path):
        logger.info("Cache file not found. A new one will be created.")
        return {}
    try:
        with open(cache_file_path, 'r') as f:
            cache_data = json.load(f)
            logger.info(f"Successfully loaded cache for {len(cache_data)} files from {cache_file_path}.")
            return cache_data
    except (json.JSONDecodeError, IOError) as e:
        logger.warning(f"Could not read cache file at {cache_file_path}. "
                       f"A new cache will be created. Error: {e}")
        return {}


def save_cache(cache_file_path: str, cache_data: Dict[str, str]):
    """
    Saves the file cache to a local JSON file.

    Args:
        cache_file_path (str): The path to the cache file.
        cache_data (Dict[str, str]): The dictionary to save.
    """
    try:
        with open(cache_file_path, 'w') as f:
            json.dump(cache_data, f, indent=4)
        logger.info(f"Successfully saved cache for {len(cache_data)} files to {cache_file_path}.")
    except IOError as e:
        logger.error(f"Could not write to cache file at {cache_file_path}: {e}")


def identify_changes(remote_files: List[Dict], local_cache: Dict[str, str]) -> List[Dict]:
    """
    Compares remote files with the local cache to find new or modified files.

    Args:
        remote_files (List[Dict]): A list of file metadata from Google Drive.
        local_cache (Dict[str, str]): A dict mapping file IDs to md5Checksums.

    Returns:
        A list of file metadata for files that need to be downloaded.
    """
    files_to_download = []
    for remote_file in remote_files:
        file_id = remote_file.get('id')
        md5_checksum = remote_file.get('md5Checksum')

        if not file_id or not md5_checksum:
            logger.warning(f"Skipping remote file with missing id or md5Checksum: {remote_file}")
            continue

        if file_id not in local_cache:
            logger.info(f"New file found: {remote_file.get('name')} (ID: {file_id})")
            files_to_download.append(remote_file)
        elif local_cache[file_id] != md5_checksum:
            logger.info(f"Modified file found: {remote_file.get('name')} (ID: {file_id})")
            files_to_download.append(remote_file)

    logger.info(f"Change detection complete. Found {len(files_to_download)} new/modified files.")
    return files_to_download


def download_file(service, file_id: str, file_name: str, download_dir: str) -> Optional[str]:
    """
    Downloads a file from Google Drive.

    Args:
        service: The authenticated Google Drive API service object.
        file_id (str): The ID of the file to download.
        file_name (str): The name to save the file as.
        download_dir (str): The directory to save the file in.

    Returns:
        The path to the downloaded file, or None on failure.
    """
    try:
        os.makedirs(download_dir, exist_ok=True)
        request = service.files().get_media(fileId=file_id)
        file_path = os.path.join(download_dir, file_name)

        content = request.execute()

        with open(file_path, 'wb') as f:
            f.write(content)

        logger.info(f"Successfully downloaded file: {file_name} to {file_path}")
        return file_path
    except HttpError as error:
        logger.error(f"An error occurred while downloading file ID {file_id}: {error}")
        return None
    except IOError as e:
        logger.error(f"Could not write file {file_name} to disk: {e}")
        return None


def main():
    """
    Main function to run the harvester.
    """
    logger.info("Starting n8n Google Drive Harvester...")

    if GDRIVE_FOLDER_ID == 'YOUR_GOOGLE_DRIVE_FOLDER_ID_HERE':
        logger.error("GDRIVE_FOLDER_ID is not configured. Please set it in the script.")
        return

    gdrive_service = get_gdrive_service(SERVICE_ACCOUNT_FILE)
    if not gdrive_service:
        logger.error("Could not create Google Drive service. Exiting.")
        return

    # 1. Load local cache
    local_cache = load_cache(CACHE_FILE)

    # 2. Scan Google Drive for remote files
    remote_files = scan_gdrive_folder(gdrive_service, GDRIVE_FOLDER_ID)
    if not remote_files:
        logger.info("No remote files found or an error occurred. Exiting.")
        return

    # 3. Identify changes
    files_to_download = identify_changes(remote_files, local_cache)
    if not files_to_download:
        logger.info("No new or modified files to download. Task complete.")
        return

    # 4. Download new/modified files
    successful_downloads = []
    for file_to_download in files_to_download:
        file_id = file_to_download['id']
        file_name = file_to_download['name']

        downloaded_path = download_file(gdrive_service, file_id, file_name, DOWNLOAD_DIR)

        if downloaded_path:
            successful_downloads.append(file_to_download)

    # 5. Update cache for successfully downloaded files
    if successful_downloads:
        # We can safely update the in-memory cache and then save it
        for downloaded_file in successful_downloads:
            local_cache[downloaded_file['id']] = downloaded_file['md5Checksum']
        save_cache(CACHE_FILE, local_cache)

    logger.info("Harvester run finished.")

if __name__ == '__main__':
    main()
