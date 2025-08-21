import pytest
import httpx
from fastapi.testclient import TestClient

from mnemosyne_core.memory_weaver.main import app
from mnemosyne_core.memory_weaver.nlp import NLPProcessor
from mnemosyne_core.memory_weaver.graph_db import GraphDB

# -- NLP Tests --

def test_extract_entities():
    processor = NLPProcessor()
    text = "Apple is a company founded by Steve Jobs."
    entities = processor.extract_entities(text)
    assert ("Apple", "ORG") in entities
    assert ("Steve Jobs", "PERSON") in entities

def test_extract_concepts():
    processor = NLPProcessor()
    text = "The future of AI is a complex topic."
    concepts = processor.extract_concepts(text)
    assert "The future" in concepts
    assert "AI" in concepts
    assert "a complex topic" in concepts

# -- GraphDB Tests --

@pytest.fixture(scope="module")
def db():
    # Set up a test database connection
    test_db = GraphDB()
    yield test_db
    # Clean up test data after tests are done
    with test_db.driver.session() as session:
        session.run("MATCH (n) DETACH DELETE n")
    test_db.close()

def test_add_and_find_entity(db):
    db.add_entity("Test Entity", "TestLabel")
    result = db.find_entity("Test Entity", "TestLabel")
    assert result is not None
    assert result["e"]["name"] == "Test Entity"

def test_add_and_get_relationship(db):
    db.add_entity("Source Node", "Source")
    db.add_entity("Target Node", "Target")
    db.add_relationship("Source Node", "Source", "Target Node", "Target", "CONNECTED_TO")

    related_entities = db.get_related_entities("Source Node", "Source")
    assert len(related_entities) > 0
    assert related_entities[0]["name"] == "Target Node"
    assert related_entities[0]["relationship"] == "CONNECTED_TO"

# -- API Tests --

@pytest.fixture(scope="module")
def client():
    return TestClient(app)

def test_health_check(client):
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Welcome to the MemoryWeaver API"}

def test_ingest_data(client, db):
    # Ingest data
    response = client.post("/ingest/", json={"text": "Test ingestion for the API.", "source": "api_test"})
    assert response.status_code == 200
    assert response.json() == {"message": "Data ingested successfully"}

    # Verify the data was added to the graph
    result = db.find_entity("api_test", "Source")
    assert result is not None

def test_graphql_query(client):
    # First, ingest some data to query
    client.post("/ingest/", json={"text": "GraphQL is a query language.", "source": "graphql_test"})

    # Now, query it via GraphQL
    graphql_query = """
    query {
        getRelatedEntities(name: "GraphQL", label: "Concept") {
            name
            relationship
        }
    }
    """
    response = client.post("/graphql", json={"query": graphql_query})
    assert response.status_code == 200
    data = response.json()
    assert "errors" not in data
    related_entities = data["data"]["getRelatedEntities"]
    assert len(related_entities) > 0
    assert related_entities[0]["name"] == "graphql_test"
    assert related_entities[0]["relationship"] == "CONTAINS"
