import os.path
import json

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from googleapiclient.http import MediaIoBaseDownload
from katana.logging_config import get_logger

logger = get_logger(__name__)

from config import settings

class GoogleDriveClient:
    """A client for interacting with the Google Drive API."""

    # If modifying these scopes, delete the file token.json.
    SCOPES = ["https://www.googleapis.com/auth/drive.readonly"]


    def __init__(self, credentials_path=settings.CREDENTIALS_PATH, token_path=settings.TOKEN_PATH):
        """
        Initializes the Google Drive client and handles authentication.

        :param credentials_path: Path to the Google API credentials file.
        :param token_path: Path to the token file for storing user's access and refresh tokens.
        """
        self.creds = self._authenticate(credentials_path, token_path)
        self.service = build("drive", "v3", credentials=self.creds)

    def _authenticate(self, credentials_path, token_path):
        """
        Handles the OAuth 2.0 authentication process.
        """
        creds = None
        if os.path.exists(token_path):
            creds = Credentials.from_authorized_user_file(token_path, self.SCOPES)

        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                # This part requires user interaction to authorize the application.
                # For a backend service, a service account is a better approach.
                # This implementation follows a common pattern for user-based OAuth.
                if not os.path.exists(credentials_path):
                    raise FileNotFoundError(
                        f"Credentials file not found at {credentials_path}. "
                        "Please obtain credentials from the Google Cloud Console and place the file here."
                    )
                flow = InstalledAppFlow.from_client_secrets_file(credentials_path, self.SCOPES)
                creds = flow.run_local_server(port=0)

            with open(token_path, "w") as token:
                token.write(creds.to_json())
        return creds

    def list_files(self, folder_id: str, page_size: int = 100):
        """
        Lists files in a specific Google Drive folder.

        :param folder_id: The ID of the Google Drive folder.
        :param page_size: The number of files to retrieve per page.
        :return: A list of file objects.
        """
        try:
            files = []
            page_token = None
            while True:
                response = (
                    self.service.files()
                    .list(
                        q=f"'{folder_id}' in parents and trashed=false",
                        spaces="drive",
                        fields="nextPageToken, files(id, name, mimeType, md5Checksum)",
                        pageToken=page_token,
                        pageSize=page_size,
                    )
                    .execute()
                )
                files.extend(response.get("files", []))
                page_token = response.get("nextPageToken", None)
                if page_token is None:
                    break
            return files
        except HttpError as error:
            logger.error(f"An error occurred: {error}")
            return None

    def download_file(self, file_id: str, destination_path: str):
        """
        Downloads a file from Google Drive.

        :param file_id: The ID of the file to download.
        :param destination_path: The path to save the downloaded file.
        """
        try:
            request = self.service.files().get_media(fileId=file_id)
            with open(destination_path, "wb") as fh:
                downloader = MediaIoBaseDownload(fh, request)
                done = False
                while done is False:
                    status, done = downloader.next_chunk()
                    logger.info(f"Download {int(status.progress() * 100)}%.")
            return destination_path
        except HttpError as error:
            logger.error(f"An error occurred: {error}")
            return None

    def get_file_metadata(self, file_id: str):
        """
        Retrieves metadata for a single file.

        :param file_id: The ID of the file.
        :return: A file metadata object.
        """
        try:
            file = self.service.files().get(fileId=file_id, fields="id, name, mimeType, md5Checksum").execute()
            return file
        except HttpError as error:
            print(f"An error occurred: {error}")
            return None
