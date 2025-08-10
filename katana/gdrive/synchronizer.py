import os
import json
from .client import GoogleDriveClient
from katana.logging_config import get_logger

logger = get_logger(__name__)

from config import settings

class Synchronizer:
    """
    Synchronizes files from a Google Drive folder to a local directory.
    """

    def __init__(self, folder_id: str, download_path: str = settings.DOWNLOAD_DIR, state_path: str = settings.SYNC_STATE_PATH, client: GoogleDriveClient = None):
        """
        Initializes the Synchronizer.

        :param folder_id: The ID of the Google Drive folder to synchronize.
        :param download_path: The local directory to download files to.
        :param state_path: The path to the file storing the synchronization state.
        :param client: An instance of GoogleDriveClient. If None, a new one is created.
        """
        self.folder_id = folder_id
        self.download_path = download_path
        self.state_path = state_path
        self.client = client or GoogleDriveClient()
        self.state = self._load_state()

        if not os.path.exists(self.download_path):
            os.makedirs(self.download_path)

    def _load_state(self):
        """Loads the synchronization state from the state file."""
        if os.path.exists(self.state_path):
            with open(self.state_path, "r") as f:
                return json.load(f)
        return {}

    def _save_state(self):
        """Saves the synchronization state to the state file."""
        with open(self.state_path, "w") as f:
            json.dump(self.state, f, indent=4)

    def sync(self):
        """
        Performs the synchronization.
        - Fetches the list of remote files.
        - Compares with the local state.
        - Downloads new or modified files.
        - Updates the state.
        :return: A list of dicts representing the files that were downloaded/updated.
        """
        logger.info("Starting synchronization...")
        downloaded_files = []
        remote_files = self.client.list_files(self.folder_id)
        if remote_files is None:
            logger.error("Could not retrieve file list from Google Drive. Aborting sync.")
            return []

        for file in remote_files:
            file_id = file["id"]
            file_name = file["name"]
            remote_checksum = file.get("md5Checksum")
            local_checksum = self.state.get(file_id)

            # Skip folders and files without checksum
            if file['mimeType'] == 'application/vnd.google-apps.folder' or not remote_checksum:
                logger.info(f"Skipping folder or unsupported file: {file_name}")
                continue

            # A file should be downloaded if it's new (local_checksum is None) or if the checksums don't match.
            if local_checksum is None or remote_checksum != local_checksum:
                logger.info(f"Downloading new or updated file: {file_name}")
                destination_path = os.path.join(self.download_path, file_name)
                self.client.download_file(file_id, destination_path)
                self.state[file_id] = remote_checksum
                downloaded_files.append({
                    "id": file_id,
                    "name": file_name,
                    "path": destination_path
                })
            else:
                logger.info(f"File is up to date: {file_name}")

        self._save_state()
        logger.info(f"Synchronization complete. {len(downloaded_files)} files downloaded/updated.")
        return downloaded_files
