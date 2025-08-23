import pytest
import os
from fastapi.testclient import TestClient
from janus_protocol.components.memory_weaver.main import app
from janus_protocol.components.memory_weaver.economic_core import wallet
from janus_protocol.components.memory_weaver.eidolon_gateway import ResourceCatalog

WALLET_FILE = 'wallet.dat'

@pytest.fixture(autouse=True)
def manage_wallet_file():
    """Fixture to ensure the wallet file is clean before and after each test."""
    if os.path.exists(WALLET_FILE):
        os.remove(WALLET_FILE)

    # Initialize with a known balance for predictable tests
    wallet.__init__(filepath=WALLET_FILE, initial_balance=200.0)

    yield

    if os.path.exists(WALLET_FILE):
        os.remove(WALLET_FILE)

@pytest.fixture(scope="module")
def client():
    return TestClient(app)

def test_purchase_success(client):
    """Tests a successful resource purchase."""
    initial_balance = wallet.get_balance()
    resource_id = "compute_instance_small"
    resource = ResourceCatalog.get_resource(resource_id)
    resource_cost = resource['cost']

    assert initial_balance >= resource_cost

    response = client.post("/eidolon/purchase", json={"resource_id": resource_id})

    assert response.status_code == 200
    assert response.json() == {"message": f"Resource '{resource_id}' purchased successfully."}

    # Verify balance was debited
    expected_balance = initial_balance - resource_cost
    assert wallet.get_balance() == expected_balance

def test_purchase_insufficient_funds(client):
    """Tests a failed purchase due to insufficient funds."""
    # Use a resource that costs more than the initial balance
    resource_id = "compute_instance_large" # Costs 500.0
    initial_balance = wallet.get_balance() # Is 200.0

    response = client.post("/eidolon/purchase", json={"resource_id": resource_id})

    assert response.status_code == 402
    assert "Insufficient funds" in response.json()["detail"]

    # Verify balance has not changed
    assert wallet.get_balance() == initial_balance

def test_purchase_resource_not_found(client):
    """Tests a failed purchase for a non-existent resource."""
    initial_balance = wallet.get_balance()
    resource_id = "non_existent_resource"

    response = client.post("/eidolon/purchase", json={"resource_id": resource_id})

    assert response.status_code == 404
    assert f"Resource '{resource_id}' not found" in response.json()["detail"]

    # Verify balance has not changed
    assert wallet.get_balance() == initial_balance
