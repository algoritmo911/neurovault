import pytest
from fastapi.testclient import TestClient
import datetime

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
    test_db = GraphDB()
    yield test_db
    with test_db.driver.session() as session:
        session.run("MATCH (n) DETACH DELETE n")
    test_db.close()

def test_add_entity_with_properties(db):
    properties = {"source": "test", "confidence_score": 0.9}
    db.add_entity("Test Entity", "TestLabel", properties=properties)
    result = db.find_entity("Test Entity", "TestLabel")
    assert result is not None
    node = result["e"]
    assert node["name"] == "Test Entity"
    assert node["source"] == "test"
    assert node["confidence_score"] == 0.9

def test_add_relationship_with_properties(db):
    db.add_entity("Source Node", "Source")
    db.add_entity("Target Node", "Target")

    timestamp = datetime.datetime.now().isoformat()
    properties = {
        "source": "test_relationship",
        "confidence_score": 0.95,
        "valid_from": timestamp
    }
    db.add_relationship("Source Node", "Source", "Target Node", "Target", "CONNECTED_TO", properties=properties)

    related_entities = db.get_related_entities("Source Node", "Source")
    assert len(related_entities) > 0
    related = related_entities[0]
    assert related["name"] == "Target Node"
    assert related["relationship"] == "CONNECTED_TO"
    assert related["properties"]["source"] == "test_relationship"
    assert related["properties"]["confidence_score"] == 0.95
    assert related["properties"]["valid_from"] == timestamp

# -- API Tests --

@pytest.fixture(scope="module")
def client():
    return TestClient(app)

def test_health_check(client):
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Welcome to the MemoryWeaver API"}

def test_ingest_data_with_properties(client, db):
    timestamp = datetime.datetime.now().isoformat()
    payload = {
        "text": "The project uses Python.",
        "source": "api_ingest_test",
        "properties": {
            "confidence_score": 0.88,
            "valid_from": timestamp
        }
    }
    response = client.post("/ingest/", json=payload)
    assert response.status_code == 200
    assert response.json() == {"message": "Data ingested successfully"}

    # Verify the data was added to the graph with properties
    related_entities = db.get_related_entities("Python", "Concept")
    assert len(related_entities) > 0
    related = related_entities[0]
    assert related["name"] == "api_ingest_test"
    assert related["properties"]["confidence_score"] == 0.88
    assert related["properties"]["valid_from"] == timestamp

def test_graphql_query_with_properties(client):
    # First, ingest data
    payload = {
        "text": "GraphQL is used for this API.",
        "source": "graphql_properties_test",
        "properties": {"confidence_score": 0.99}
    }
    client.post("/ingest/", json=payload)

    # Now, query it via GraphQL
    graphql_query = """
    query {
        getRelatedEntities(name: "GraphQL", label: "Concept") {
            name
            relationship
            properties
        }
    }
    """
    response = client.post("/graphql", json={"query": graphql_query})
    assert response.status_code == 200
    data = response.json()
    assert "errors" not in data

    related_entities = data["data"]["getRelatedEntities"]
    assert len(related_entities) > 0

    # Find the specific relationship we're looking for
    target_entity = next((e for e in related_entities if e["name"] == "graphql_properties_test"), None)
    assert target_entity is not None
    assert target_entity["relationship"] == "CONTAINS"
    assert target_entity["properties"]["source"] == "graphql_properties_test"
    assert target_entity["properties"]["confidence_score"] == 0.99
