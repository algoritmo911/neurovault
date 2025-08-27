import pytest
from httpx import AsyncClient
from unittest.mock import patch, MagicMock
import json
import io

from services.ingestion_cortex.main import app

pytestmark = pytest.mark.asyncio

# --- Test Cases for Awareness Trigger ---

@pytest.mark.parametrize(
    "resonance_score, text_content, expected_subject",
    [
        (0.50, "A completely new experience.", "event.type.novel"),
        (0.95, "Thinking about that same topic again.", "event.type.reinforcement"),
        (0.80, "Just a routine daily update.", "event.type.routine"),
        (0.50, "This is a critical alert!", "event.type.anomaly.priority"), # Anomaly check overrides score
    ]
)
@patch("services.ingestion_cortex.main.publish_event_to_broker")
@patch("services.ingestion_cortex.main.check_resonance")
@patch("services.ingestion_cortex.main.context", {"model": MagicMock()})
async def test_awareness_trigger_logic(
    mock_check_resonance, mock_publish_task,
    resonance_score, text_content, expected_subject
):
    """
    Tests that the correct event type is published based on resonance and content.
    """
    # Arrange
    mock_check_resonance.return_value = resonance_score

    source_id = "test-user-123"
    metadata = {"text": text_content}
    metadata_json = json.dumps(metadata)
    form_data = {"source_id": source_id, "metadata_json": metadata_json}
    files_data = {"files": ("test.txt", io.BytesIO(b"data"), "text/plain")}

    # Act
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.post("/ingest/", data=form_data, files=files_data)

    # Assert
    assert response.status_code == 202

    mock_check_resonance.assert_called_once()
    mock_publish_task.assert_called_once()

    # Check the subject passed to the publisher
    call_args = mock_publish_task.call_args[0]
    published_subject = call_args[0]
    assert published_subject == expected_subject

# --- Other API Tests ---

async def test_ingest_missing_text_field():
    """Tests that a 400 is returned if the 'text' field is missing in metadata."""
    form_data = {"source_id": "test-user-no-text", "metadata_json": "{}"}
    files_data = {"files": ("test.txt", io.BytesIO(b"data"), "text/plain")}

    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.post("/ingest/", data=form_data, files=files_data)

    assert response.status_code == 400

async def test_ingest_invalid_metadata_json():
    """Tests the case where metadata_json is not valid JSON."""
    form_data = {"source_id": "test-user", "metadata_json": "not json"}
    files_data = {"files": ("test.txt", io.BytesIO(b"data"), "text/plain")}

    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.post("/ingest/", data=form_data, files=files_data)

    assert response.status_code == 400

async def test_ingest_missing_form_field():
    """Tests the case where a required form field is missing."""
    form_data = {"metadata_json": '{"text": "some text"}'}
    files_data = {"files": ("test.txt", io.BytesIO(b"data"), "text/plain")}

    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.post("/ingest/", data=form_data, files=files_data)

    assert response.status_code == 422 # Unprocessable Entity
