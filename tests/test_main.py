import pytest
from fastapi.testclient import TestClient
from neurovault.main import app, data_queue

client = TestClient(app)

@pytest.fixture(autouse=True)
def clear_queue():
    """A fixture to clear the queue before each test."""
    while not data_queue.empty():
        data_queue.get_nowait()
    yield

def test_ingest_data_success():
    """
    Test successful data ingestion.
    """
    payload = {
        "source": "test_source",
        "type": "test_type",
        "content": "This is a test content.",
        "metadata": {"key": "value"}
    }
    response = client.post("/ingest", json=payload)
    assert response.status_code == 200
    assert response.json() == {"message": "Data received and queued successfully."}

    # Check if the item was added to the queue
    assert not data_queue.empty()
    item = data_queue.get_nowait()
    assert item.source == "test_source"
    assert item.content == "This is a test content."
    data_queue.task_done()

def test_ingest_data_invalid_content():
    """
    Test data ingestion with empty content.
    """
    payload = {
        "source": "test_source",
        "type": "test_type",
        "content": " ", # Empty content
        "metadata": {}
    }
    response = client.post("/ingest", json=payload)
    assert response.status_code == 422
    assert response.json() == {"detail": "Content cannot be empty."}

    # Check that nothing was added to the queue
    assert data_queue.empty()

def test_ingest_data_missing_fields():
    """
    Test data ingestion with missing required fields (e.g., 'content').
    """
    payload = {
        "source": "test_source",
        "type": "test_type",
        # 'content' field is missing
    }
    response = client.post("/ingest", json=payload)
    # FastAPI's TestClient with Pydantic should return a 422 Unprocessable Entity
    assert response.status_code == 422
    # The detail message will contain information about the missing field
    assert "Field required" in response.text

    # Check that nothing was added to the queue
    assert data_queue.empty()
