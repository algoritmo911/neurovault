import pytest
import os
import json
from fastapi.testclient import TestClient
from mnemosyne_core.alpha_cabinets.user_001.main import app

# Define the path for the test memories file
TEST_MEMORIES_FILE = "tests/memories_test.json"

@pytest.fixture(autouse=True)
def setup_and_teardown_test_db(monkeypatch):
    """
    This fixture ensures that each test function has a clean, isolated
    environment. It patches the application's file path to use a test-specific
    file and handles its creation and cleanup.
    """
    # 1. Setup: Patch the MEMORIES_FILE constant in the main app to isolate tests
    monkeypatch.setattr(
        "mnemosyne_core.alpha_cabinets.user_001.main.MEMORIES_FILE",
        TEST_MEMORIES_FILE
    )

    # 2. Setup: Ensure the test file is clean before the test
    if os.path.exists(TEST_MEMORIES_FILE):
        os.remove(TEST_MEMORIES_FILE)
    with open(TEST_MEMORIES_FILE, "w") as f:
        json.dump([], f)

    # This is where the test function will execute
    yield

    # 3. Teardown: Clean up the test file after the test is done
    if os.path.exists(TEST_MEMORIES_FILE):
        os.remove(TEST_MEMORIES_FILE)


@pytest.fixture
def client():
    """Provides a TestClient instance for making API requests."""
    return TestClient(app)


def test_read_root(client):
    """Tests the root endpoint."""
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {
        "message": "Welcome to your personal Alpha Cabinet, User 001."
    }

def test_empty_memories(client):
    """Tests that initially there are no memories."""
    response = client.get("/memories/")
    assert response.status_code == 200
    assert response.json() == []

def test_full_crud_workflow(client):
    """
    Tests the complete lifecycle of a memory object:
    Create -> Read -> Update -> Delete
    """
    # 1. Create a memory
    response_create = client.post(
        "/memories/",
        json={"title": "Test CRUD", "content": "Content CRUD"},
    )
    assert response_create.status_code == 200
    created_memory = response_create.json()
    memory_id = created_memory["id"]
    assert created_memory["title"] == "Test CRUD"
    assert memory_id == 1

    # Verify it was written to the file
    with open(TEST_MEMORIES_FILE, "r") as f:
        data = json.load(f)
        assert len(data) == 1
        assert data[0]["title"] == "Test CRUD"

    # 2. Get the memory by ID
    response_get = client.get(f"/memories/{memory_id}")
    assert response_get.status_code == 200
    assert response_get.json()["title"] == "Test CRUD"

    # 3. Get all memories
    response_get_all = client.get("/memories/")
    assert response_get_all.status_code == 200
    assert len(response_get_all.json()) == 1

    # 4. Update the memory
    response_update = client.put(
        f"/memories/{memory_id}",
        json={"title": "Updated Title", "content": "Updated Content"},
    )
    assert response_update.status_code == 200
    assert response_update.json()["title"] == "Updated Title"

    # Verify the update was written to the file
    with open(TEST_MEMORIES_FILE, "r") as f:
        data = json.load(f)
        assert data[0]["title"] == "Updated Title"

    # 5. Delete the memory
    response_delete = client.delete(f"/memories/{memory_id}")
    assert response_delete.status_code == 200
    assert response_delete.json() == {"message": "Memory deleted successfully"}

    # Verify it was deleted from the file
    with open(TEST_MEMORIES_FILE, "r") as f:
        data = json.load(f)
        assert len(data) == 0

def test_not_found_errors(client):
    """Tests that API returns 404 for non-existent memories."""
    response_get_fail = client.get("/memories/999")
    assert response_get_fail.status_code == 404

    response_update_fail = client.put(
        "/memories/999",
        json={"title": "Updated Title", "content": "Updated Content"},
    )
    assert response_update_fail.status_code == 404

    response_delete_fail = client.delete("/memories/999")
    assert response_delete_fail.status_code == 404
