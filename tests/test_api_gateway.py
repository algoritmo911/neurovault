import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from datetime import datetime, UTC

# Import the FastAPI app instance
from mnemosyne_core.api_gateway.main import app

# Mark all tests in this module as async
pytestmark = pytest.mark.asyncio

@pytest_asyncio.fixture
async def client():
    """
    Create an async test client for the app.
    """
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        yield client

async def test_health_check(client: AsyncClient):
    """
    Test the /health endpoint.
    """
    response = await client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}

async def test_ingest_event_success(client: AsyncClient):
    """
    Test successful event ingestion via the /ingest endpoint.
    """
    event_data = {
        "source": "telegram",
        "ts": datetime.now(UTC).isoformat(),
        "author": "user",
        "payload": {
            "text": "This is a test event."
        }
    }
    response = await client.post("/ingest", json=event_data)
    assert response.status_code == 201
    response_json = response.json()
    assert response_json["source"] == "telegram"
    assert response_json["author"] == "user"
    assert response_json["payload"]["text"] == "This is a test event."
    assert "id" in response_json
    assert "ontology" in response_json

async def test_ingest_event_invalid_data(client: AsyncClient):
    """
    Test event ingestion with missing required fields.
    """
    # 'source' is missing
    event_data = {
        "ts": datetime.now(UTC).isoformat(),
        "author": "user",
        "payload": {
            "text": "This is an invalid event."
        }
    }
    response = await client.post("/ingest", json=event_data)
    assert response.status_code == 400
    assert "Invalid event data" in response.json()["detail"]

async def test_ingest_event_bad_enum(client: AsyncClient):
    """
    Test event ingestion with an invalid enum value.
    """
    event_data = {
        "source": "invalid_source", # This is not in the SourceEnum
        "ts": datetime.now(UTC).isoformat(),
        "author": "user",
        "payload": {
            "text": "This is a test event."
        }
    }
    response = await client.post("/ingest", json=event_data)
    assert response.status_code == 400
    assert "Invalid event data" in response.json()["detail"]
