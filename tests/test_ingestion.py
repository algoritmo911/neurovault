# tests/test_ingestion.py
import pytest
from httpx import ASGITransport, AsyncClient
from unittest.mock import AsyncMock, patch

from neurovault.main import app
from neurovault.core.db import get_db_session

@pytest.mark.asyncio
async def test_ingestion_endpoint_success():
    # 1. Create a mock for the transaction
    mock_tx = AsyncMock()
    mock_tx.run = AsyncMock()
    mock_tx.__aenter__.return_value = mock_tx

    # 2. Create a mock for the session
    mock_session = AsyncMock()
    mock_session.begin_transaction.return_value = mock_tx

    # 3. Create an override for the dependency
    async def override_get_db_session():
        yield mock_session

    # 4. Apply the override
    app.dependency_overrides[get_db_session] = override_get_db_session

    # 5. Send the request
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        test_payload = {
            "entities": [{"id": "node1", "label": "Person", "properties": {"name": "Alice"}}],
            "relationships": []
        }
        response = await client.post("/api/v1/ingest/", json=test_payload)

    # 6. Assert the results
    assert response.status_code == 201
    mock_tx.run.assert_awaited_once()
    mock_session.begin_transaction.assert_awaited_once()

    # 7. Clear the override
    app.dependency_overrides.clear()
