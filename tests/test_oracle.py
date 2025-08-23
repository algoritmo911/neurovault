import pytest
from fastapi.testclient import TestClient
from janus_protocol.components.memory_weaver.graph_db import GraphDB
from janus_protocol.components.memory_weaver.main import app

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

def setup_test_scenario(db: GraphDB):
    """Helper function to create a graph for hypothesis testing."""
    # Project X depends on an outdated API
    db.add_entity("Project X", "Project")
    db.add_entity("API Y", "API", properties={"status": "deprecated"})
    db.add_relationship("Project X", "Project", "API Y", "API", "DEPENDS_ON")

    # The lead developer is overworked
    db.add_entity("Person A", "Person", properties={"stress_level": "high"})
    db.add_relationship("Project X", "Project", "Person A", "Person", "HAS_LEAD")

def test_oracle_generates_hypotheses(client, db):
    # 1. Set up the graph with a known scenario
    setup_test_scenario(db)

    # 2. Ask a question that the Oracle should be able to answer
    question = "Why are there potential issues with Project X?"

    response = client.post("/hypothesize/", json={"question": question})
    assert response.status_code == 200

    data = response.json()
    hypotheses = data.get("hypotheses", [])

    # 3. Verify that the correct hypotheses were generated
    assert len(hypotheses) >= 2, "Oracle should have found at least two hypotheses."

    hypothesis1_found = any("API Y" in h and "deprecated" in h for h in hypotheses)
    assert hypothesis1_found, "Oracle failed to find the hypothesis about the deprecated API."

    hypothesis2_found = any("Person A" in h and "high" in h for h in hypotheses)
    assert hypothesis2_found, "Oracle failed to find the hypothesis about the overworked project lead."
