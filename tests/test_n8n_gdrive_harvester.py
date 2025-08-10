import pytest
import json
from unittest.mock import MagicMock, patch

from mnemosyne_core.data_ingestion import n8n_gdrive_harvester as harvester

@pytest.fixture
def sample_remote_files():
    """Provides a sample list of remote file metadata."""
    return [
        {'id': 'file1', 'name': 'Workflow1.json', 'md5Checksum': 'md5_1_new'},
        {'id': 'file2', 'name': 'Workflow2.json', 'md5Checksum': 'md5_2_same'},
        {'id': 'file3', 'name': 'Workflow3.json', 'md5Checksum': 'md5_3_new'},
    ]

@pytest.fixture
def sample_local_cache():
    """Provides a sample local cache."""
    return {
        'file2': 'md5_2_same',      # Unchanged file
        'file3': 'md5_3_old',      # Modified file
        'file4': 'md5_4_deleted',  # A file that was deleted on remote
    }

def test_identify_changes_new_modified_and_unchanged(sample_remote_files, sample_local_cache):
    """
    Tests the identify_changes function with a mix of new, modified, and unchanged files.
    """
    changes = harvester.identify_changes(sample_remote_files, sample_local_cache)

    assert len(changes) == 2

    changed_ids = {change['id'] for change in changes}
    assert 'file1' in changed_ids  # New file
    assert 'file3' in changed_ids  # Modified file
    assert 'file2' not in changed_ids # Unchanged file

def test_identify_changes_no_changes(sample_remote_files):
    """
    Tests that no changes are detected when the cache is in sync.
    """
    # Create a cache that is perfectly in sync with remote files
    local_cache = {
        'file1': 'md5_1_new',
        'file2': 'md5_2_same',
        'file3': 'md5_3_new',
    }
    changes = harvester.identify_changes(sample_remote_files, local_cache)
    assert len(changes) == 0

def test_identify_changes_all_new():
    """
    Tests that all files are detected as new when the cache is empty.
    """
    remote_files = [
        {'id': 'file1', 'name': 'W1.json', 'md5Checksum': 'md5_1'},
        {'id': 'file2', 'name': 'W2.json', 'md5Checksum': 'md5_2'},
    ]
    local_cache = {}
    changes = harvester.identify_changes(remote_files, local_cache)
    assert len(changes) == 2
    assert changes[0]['id'] == 'file1'
    assert changes[1]['id'] == 'file2'

def test_identify_changes_empty_remote():
    """
    Tests that no changes are detected when there are no remote files.
    """
    remote_files = []
    local_cache = {'file1': 'md5_1'}
    changes = harvester.identify_changes(remote_files, local_cache)
    assert len(changes) == 0

def test_cache_functions(tmp_path):
    """
    Tests the save_cache and load_cache functions together.
    """
    cache_dir = tmp_path / "cache"
    cache_dir.mkdir()
    cache_file = cache_dir / ".gdrive_cache.json"

    # 1. Test loading from a non-existent file
    assert harvester.load_cache(cache_file) == {}

    # 2. Test saving and then loading the cache
    cache_data_to_save = {'file1': 'md5_1', 'file2': 'md5_2'}
    harvester.save_cache(cache_file, cache_data_to_save)

    loaded_cache = harvester.load_cache(cache_file)
    assert loaded_cache == cache_data_to_save

def test_load_cache_invalid_json(tmp_path):
    """
    Tests that load_cache handles invalid JSON gracefully.
    """
    cache_file = tmp_path / "invalid.json"
    cache_file.write_text("this is not json")

    loaded_cache = harvester.load_cache(cache_file)
    assert loaded_cache == {}
