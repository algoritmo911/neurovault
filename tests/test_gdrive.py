import unittest
import os
import json
import tempfile
import shutil
from unittest.mock import patch, MagicMock, mock_open

# Add project root to path to allow absolute imports
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from katana.gdrive.client import GoogleDriveClient
from katana.gdrive.synchronizer import Synchronizer

# Since we are testing gdrive, we need to mock the settings it uses
from config import settings

class TestGoogleDriveIntegration(unittest.TestCase):

    def setUp(self):
        # Create a temporary directory for downloads and config files
        self.test_dir = tempfile.mkdtemp()
        self.download_path = os.path.join(self.test_dir, 'downloads')
        self.config_path = os.path.join(self.test_dir, 'config')
        os.makedirs(self.download_path)
        os.makedirs(self.config_path)

        # Override settings to use the temporary directory
        settings.DOWNLOAD_DIR = self.download_path
        settings.CREDENTIALS_PATH = os.path.join(self.config_path, 'credentials.json')
        settings.TOKEN_PATH = os.path.join(self.config_path, 'token.json')
        settings.SYNC_STATE_PATH = os.path.join(self.config_path, 'sync_state.json')

    def tearDown(self):
        # Clean up the temporary directory
        shutil.rmtree(self.test_dir)

    @patch('katana.gdrive.client.build')
    @patch('katana.gdrive.client.InstalledAppFlow')
    @patch('katana.gdrive.client.Credentials')
    @patch('os.path.exists')
    def test_gdrive_client_auth_new_token(self, mock_exists, mock_credentials, mock_flow, mock_build):
        """Test GDriveClient authentication when no token exists."""
        # Mock os.path.exists to simulate token not existing, but credentials existing.
        def exists_side_effect(path):
            if path == settings.CREDENTIALS_PATH:
                return True
            if path == settings.TOKEN_PATH:
                return False
            return False
        mock_exists.side_effect = exists_side_effect

        # Mock the flow to return a mock credential object
        mock_creds_instance = MagicMock()
        mock_creds_instance.to_json.return_value = '{"token": "fake_token"}'
        mock_flow.from_client_secrets_file.return_value.run_local_server.return_value = mock_creds_instance

        # Mock the open call for writing the token
        m = mock_open()
        with patch('builtins.open', m):
            client = GoogleDriveClient(
                credentials_path=settings.CREDENTIALS_PATH,
                token_path=settings.TOKEN_PATH
            )
            m.assert_called_once_with(settings.TOKEN_PATH, 'w')
            m().write.assert_called_once_with('{"token": "fake_token"}')

        self.assertIsNotNone(client.service)
        mock_build.assert_called_once()

    @patch('katana.gdrive.client.build')
    @patch('katana.gdrive.client.Credentials')
    @patch('os.path.exists', return_value=True)
    def test_gdrive_client_auth_existing_token(self, mock_exists, mock_credentials, mock_build):
        """Test GDriveClient authentication when a valid token exists."""
        mock_creds_instance = MagicMock()
        mock_creds_instance.valid = True
        mock_credentials.from_authorized_user_file.return_value = mock_creds_instance

        client = GoogleDriveClient(
            credentials_path=settings.CREDENTIALS_PATH,
            token_path=settings.TOKEN_PATH
        )

        self.assertIsNotNone(client.service)
        mock_credentials.from_authorized_user_file.assert_called_once_with(settings.TOKEN_PATH, GoogleDriveClient.SCOPES)
        mock_build.assert_called_once()

    def test_synchronizer_initial_sync(self):
        """Test the synchronizer with a fresh start."""
        # --- Mock GDriveClient ---
        mock_client = MagicMock(spec=GoogleDriveClient)

        # Mock list_files to return a list of file metadata
        mock_remote_files = [
            {'id': 'file1', 'name': 'doc1.txt', 'md5Checksum': 'sum1', 'mimeType': 'text/plain'},
            {'id': 'file2', 'name': 'doc2.pdf', 'md5Checksum': 'sum2', 'mimeType': 'application/pdf'},
        ]
        mock_client.list_files.return_value = mock_remote_files

        # Mock download_file to "create" a file
        def mock_download(file_id, dest_path):
            with open(dest_path, 'w') as f:
                f.write(f"content of {file_id}")
            return dest_path
        mock_client.download_file.side_effect = mock_download

        # --- Run Synchronizer ---
        synchronizer = Synchronizer(
            folder_id='fake_folder_id',
            client=mock_client,
            download_path=self.download_path,
            state_path=settings.SYNC_STATE_PATH
        )
        downloaded_files = synchronizer.sync()

        # --- Assertions ---
        # Check the return value
        self.assertEqual(len(downloaded_files), 2)
        self.assertIn("doc1.txt", [f["name"] for f in downloaded_files])
        self.assertIn("doc2.pdf", [f["name"] for f in downloaded_files])

        # Check that list_files and download_file were called
        mock_client.list_files.assert_called_once_with('fake_folder_id')
        self.assertEqual(mock_client.download_file.call_count, 2)

        # Check that files were "downloaded"
        self.assertTrue(os.path.exists(os.path.join(self.download_path, 'doc1.txt')))
        self.assertTrue(os.path.exists(os.path.join(self.download_path, 'doc2.pdf')))

        # Check that the state file is correct
        with open(settings.SYNC_STATE_PATH, 'r') as f:
            state = json.load(f)
        self.assertEqual(state, {'file1': 'sum1', 'file2': 'sum2'})

    def test_synchronizer_update_sync(self):
        """Test the synchronizer when some files are new, some updated, some unchanged."""
        # --- Initial State ---
        initial_state = {
            'file1': 'old_sum1', # Will be updated
            'file3': 'sum3'      # Will be unchanged
        }
        with open(settings.SYNC_STATE_PATH, 'w') as f:
            json.dump(initial_state, f)

        # --- Mock GDriveClient ---
        mock_client = MagicMock(spec=GoogleDriveClient)
        mock_remote_files = [
            {'id': 'file1', 'name': 'doc1.txt', 'md5Checksum': 'new_sum1', 'mimeType': 'text/plain'}, # Updated
            {'id': 'file2', 'name': 'doc2.pdf', 'md5Checksum': 'sum2', 'mimeType': 'application/pdf'},     # New
            {'id': 'file3', 'name': 'doc3.csv', 'md5Checksum': 'sum3', 'mimeType': 'text/csv'},     # Unchanged
        ]
        mock_client.list_files.return_value = mock_remote_files

        # Use the same file-writing mock as the other test
        def mock_download(file_id, dest_path):
            with open(dest_path, 'w') as f:
                f.write(f"content of {file_id}")
            return dest_path
        mock_client.download_file.side_effect = mock_download

        # --- Run Synchronizer ---
        synchronizer = Synchronizer(
            folder_id='fake_folder_id',
            client=mock_client,
            download_path=self.download_path,
            state_path=settings.SYNC_STATE_PATH
        )
        downloaded_files = synchronizer.sync()

        # --- Assertions ---
        # Check the return value (should contain the updated and new files)
        self.assertEqual(len(downloaded_files), 2)
        self.assertEqual(downloaded_files[0]['id'], 'file1')
        self.assertEqual(downloaded_files[1]['id'], 'file2')

        # Should be called for the new and updated file
        self.assertEqual(mock_client.download_file.call_count, 2)

        # Check final state
        with open(settings.SYNC_STATE_PATH, 'r') as f:
            state = json.load(f)
        self.assertEqual(state, {'file1': 'new_sum1', 'file2': 'sum2', 'file3': 'sum3'})


if __name__ == '__main__':
    unittest.main()
