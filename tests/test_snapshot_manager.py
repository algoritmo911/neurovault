import pytest
from datetime import datetime
from mnemosyne_core.services.snapshot_manager import SnapshotManager
from mnemosyne_core.models.memory import MemoryEvent, SourceEnum, AuthorEnum, Payload

@pytest.fixture
def sample_events():
    """Provides a list of sample MemoryEvent objects for testing."""
    return [
        MemoryEvent(
            source=SourceEnum.SYSTEM,
            author=AuthorEnum.AGENT,
            ts=datetime.now(),
            payload=Payload(text="Test event 1")
        ),
        MemoryEvent(
            source=SourceEnum.GITHUB,
            author=AuthorEnum.USER,
            ts=datetime.now(),
            payload=Payload(text="Test event 2")
        ),
    ]

@pytest.fixture
def snapshot_manager():
    """Provides an instance of the SnapshotManager."""
    return SnapshotManager()

def test_create_snapshot(snapshot_manager: SnapshotManager, sample_events: list):
    """Test the creation of a snapshot."""
    snapshot = snapshot_manager.create_snapshot(sample_events)

    assert isinstance(snapshot, dict)
    assert snapshot["version"] == "1.0"
    assert "created_at" in snapshot
    assert snapshot["metadata"]["event_count"] == 2
    assert len(snapshot["events"]) == 2
    assert snapshot["events"][0]["payload"]["text"] == "Test event 1"

def test_restore_from_valid_snapshot(snapshot_manager: SnapshotManager, sample_events: list):
    """Test restoring from a valid snapshot."""
    snapshot = snapshot_manager.create_snapshot(sample_events)
    result = snapshot_manager.restore_from_snapshot(snapshot)
    assert result is True

def test_restore_from_invalid_snapshot(snapshot_manager: SnapshotManager):
    """Test restoring from an invalid or incomplete snapshot."""
    invalid_snapshot = {"version": "1.0", "some_other_key": []}
    result = snapshot_manager.restore_from_snapshot(invalid_snapshot)
    assert result is False
