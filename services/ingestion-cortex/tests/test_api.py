import sys
import os
import pytest
from httpx import AsyncClient
from unittest.mock import patch
import json
import io

# Add the project root to the path to resolve import issues in this environment
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..'))
sys.path.insert(0, project_root)

from services.ingestion_cortex.main import app

# Mark all tests in this file as asyncio
pytestmark = pytest.mark.asyncio

@pytest.fixture
def mock_nats_publisher():
    """Fixture to mock the NATS publisher."""
    with patch("services.ingestion_cortex.main.publish_to_nats") as mock_publish:
        yield mock_publish

async def test_ingest_neuro_event_success(mock_nats_publisher):
    """Tests successful ingestion of a Neuro-Event."""
    # Arrange
    source_id = "test-user-123"
    metadata = {"location": "Test Room", "device": "Test-Sensor-A"}
    metadata_json = json.dumps(metadata)
    file_content = b"This is a test text stream."
    file_to_upload = ("test.txt", io.BytesIO(file_content), "text/plain")
    form_data = {"source_id": source_id, "metadata_json": metadata_json}
    files_data = {"files": file_to_upload}

    # Act
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.post("/ingest/", data=form_data, files=files_data)

    # Assert
    assert response.status_code == 202
    mock_nats_publisher.assert_called_once()

async def test_ingest_invalid_metadata_json(mock_nats_publisher):
    """Tests the case where metadata_json is not valid JSON."""
    # Arrange
    form_data = {"source_id": "test-user", "metadata_json": "this is not json"}
    files_data = {"files": ("test.txt", io.BytesIO(b"data"), "text/plain")}

    # Act
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.post("/ingest/", data=form_data, files=files_data)

    # Assert
    assert response.status_code == 400
    mock_nats_publisher.assert_not_called()

async def test_ingest_missing_field():
    """Tests the case where a required form field is missing."""
    # Arrange
    form_data = {"metadata_json": "{}"} # Missing source_id
    files_data = {"files": ("test.txt", io.BytesIO(b"data"), "text/plain")}

    # Act
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.post("/ingest/", data=form_data, files=files_data)

    # Assert
    assert response.status_code == 422

async def test_ingest_nats_publication_failure(mock_nats_publisher):
    """Tests the case where the NATS publisher raises an exception."""
    # Arrange
    mock_nats_publisher.side_effect = Exception("NATS is down")
    form_data = {
        "source_id": "test-user-fail",
        "metadata_json": json.dumps({"test": "fail"})
    }
    files_data = {"files": ("test.txt", io.BytesIO(b"data"), "text/plain")}

    # Act
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.post("/ingest/", data=form_data, files=files_data)

    # Assert
    assert response.status_code == 503
    mock_nats_publisher.assert_called_once()
