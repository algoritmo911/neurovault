import pytest
from fastapi.testclient import TestClient
from mnemosyne_core.memory_weaver.graph_db import GraphDB
from mnemosyne_core.memory_weaver.main import app

@pytest.fixture(scope="module")
def db():
    test_db = GraphDB()
    with test_db.driver.session() as session:
        session.run("MATCH (n) DETACH DELETE n")
    yield test_db
    with test_db.driver.session() as session:
        session.run("MATCH (n) DETACH DELETE n")
    test_db.close()

@pytest.fixture(scope="module")
def client():
    return TestClient(app)

def test_inquisitor_blocks_contradiction(client, db):
    # 1. Establish an initial fact: Apple's CEO is Steve Jobs.
    db.add_entity("Apple", "Company")
    db.add_entity("Steve Jobs", "Person")
    db.add_relationship("Apple", "Company", "Steve Jobs", "Person", "HAS_CEO")

    # 2. Attempt to ingest a contradictory fact: Apple's CEO is Tim Cook.
    # We pass the structured fact in the 'properties' for the Inquisitor to check.
    payload = {
        "text": "Tim Cook is the CEO of Apple.",
        "source": "inquisitor_test_1",
        "properties": {
            "fact": ["Apple", "HAS_CEO", "Tim Cook"]
        }
    }
    response = client.post("/ingest/", json=payload)
    # The connector should just print a message and return, so the API response is still 200.
    assert response.status_code == 200

    # 3. Verify the contradictory fact was NOT added. The CEO should still be Steve Jobs.
    related_entities = db.get_related_entities("Apple", "Company")
    ceo_found = False
    for entity in related_entities:
        if entity["relationship"] == "HAS_CEO":
            assert entity["name"] == "Steve Jobs", "Inquisitor failed to block contradictory fact."
            ceo_found = True
    assert ceo_found, "Initial CEO relationship was not found."

def test_inquisitor_allows_non_contradictory_data(client, db):
    # 1. Ingest a non-contradictory fact (USES_TECH is not a functional relationship)
    db.add_entity("Mnemosyne", "Project")
    db.add_entity("FastAPI", "Concept")
    db.add_relationship("Mnemosyne", "Project", "FastAPI", "Concept", "USES_TECH")

    payload = {
        "text": "The Mnemosyne project also uses Neo4j.",
        "source": "inquisitor_test_2"
    }
    response = client.post("/ingest/", json=payload)
    assert response.status_code == 200

    # 2. Verify the new, non-contradictory fact was added.
    related_entities = db.get_related_entities("Mnemosyne", "Project")
    techs_used = [entity["name"] for entity in related_entities if entity["relationship"] == "USES_TECH"]

    assert "FastAPI" in techs_used
    assert "Neo4j" in techs_used, "Inquisitor incorrectly blocked a non-contradictory fact."
