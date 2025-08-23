import pytest
import os
from fastapi.testclient import TestClient
from janus_protocol.components.memory_weaver.main import app
from janus_protocol.components.memory_weaver.economic_core import Wallet, wallet
from janus_protocol.components.memory_weaver.config import economic_config

WALLET_FILE = 'wallet.dat'

@pytest.fixture(autouse=True)
def manage_wallet_file():
    """Fixture to ensure the wallet file is clean before and after each test."""
    if os.path.exists(WALLET_FILE):
        os.remove(WALLET_FILE)

    # Re-initialize the global wallet instance to start fresh for each test
    wallet.__init__(filepath=WALLET_FILE, initial_balance=100.0)

    yield

    if os.path.exists(WALLET_FILE):
        os.remove(WALLET_FILE)

# -- Unit Tests for Wallet Class --

def test_wallet_initialization():
    assert wallet.get_balance() == 100.0
    assert os.path.exists(WALLET_FILE)

def test_wallet_credit():
    wallet.credit(50.0)
    assert wallet.get_balance() == 150.0

def test_wallet_debit_success():
    success = wallet.debit(70.0)
    assert success is True
    assert wallet.get_balance() == 30.0

def test_wallet_debit_insufficient_funds():
    success = wallet.debit(120.0)
    assert success is False
    assert wallet.get_balance() == 100.0 # Balance should not change

def test_wallet_persistence():
    wallet.credit(25.5)
    wallet.debit(10.0)
    # The balance should be 115.5

    # Create a new instance, which should load from the file
    new_wallet = Wallet(filepath=WALLET_FILE)
    assert new_wallet.get_balance() == 115.5

# -- API Tests for Economic Core --

@pytest.fixture(scope="module")
def client():
    return TestClient(app)

def test_get_balance_endpoint(client):
    response = client.get("/wallet/balance")
    assert response.status_code == 200
    assert response.json() == {"balance": 100.0}

def test_credit_wallet_endpoint(client):
    response = client.post("/wallet/credit", json={"amount": 50})
    assert response.status_code == 200
    assert response.json() == {"message": "Wallet credited successfully", "new_balance": 150.0}

    # Verify with the balance endpoint
    balance_response = client.get("/wallet/balance")
    assert balance_response.json()["balance"] == 150.0

def test_costly_endpoint_success(client):
    # Ensure there are enough funds
    wallet.credit(100) # Balance is now 200

    # Call a costly endpoint
    response = client.post("/ingest/", json={"text": "This should succeed.", "source": "test"})
    assert response.status_code == 200

    # Check if balance was debited
    expected_balance = 200.0 - economic_config.COST_INGEST
    assert wallet.get_balance() == expected_balance

def test_costly_endpoint_insufficient_funds(client):
    # Set a low balance
    wallet.debit(99.5) # Balance is now 0.5, less than any cost

    # Call a costly endpoint
    response = client.post("/ingest/", json={"text": "This should fail.", "source": "test"})
    assert response.status_code == 402
    assert "Payment Required" in response.json()["detail"]

    # Verify balance was not changed
    assert wallet.get_balance() == 0.5
