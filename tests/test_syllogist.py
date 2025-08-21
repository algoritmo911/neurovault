import pytest
import yaml
from mnemosyne_core.memory_weaver.graph_db import GraphDB
from mnemosyne_core.memory_weaver.syllogist import Syllogist

@pytest.fixture(scope="module")
def db():
    test_db = GraphDB()
    # Clean up before and after
    with test_db.driver.session() as session:
        session.run("MATCH (n) DETACH DELETE n")
    yield test_db
    with test_db.driver.session() as session:
        session.run("MATCH (n) DETACH DELETE n")
    test_db.close()

def test_skill_inference_rule(db, tmp_path):
    # 1. Create a temporary, specific rule file for this test
    rules_content = """
- name: "Test Skill Inference"
  if:
    - "(person:Person)-[:WORKS_ON]->(project:Project)"
    - "(project)-[:USES_TECH]->(tech:Concept)"
  then:
    - create: "(person)-[r:HAS_SKILL]->(tech)"
      properties:
        inferred: true
        confidence_score: 0.9
        source: "Syllogist - Test Skill Inference"
"""
    rules_file = tmp_path / "test_rules.yaml"
    rules_file.write_text(rules_content)

    # 2. Set up the initial graph state
    db.add_entity("Anna", "Person")
    db.add_entity("Project Apollo", "Project")
    db.add_entity("Python", "Concept", properties={"name": "Python"}) # Ensure tech has a name property
    db.add_relationship("Anna", "Person", "Project Apollo", "Project", "WORKS_ON")
    db.add_relationship("Project Apollo", "Project", "Python", "Concept", "USES_TECH")

    # 3. Run the Syllogist
    syllogist = Syllogist(rules_path=str(rules_file))
    syllogist.run_inference()

    # 4. Verify the inferred relationship
    related_entities = db.get_related_entities("Anna", "Person")

    inferred_skill_found = False
    for entity in related_entities:
        if entity["name"] == "Python" and entity["relationship"] == "HAS_SKILL":
            inferred_skill_found = True
            assert entity["properties"]["inferred"] is True
            assert entity["properties"]["confidence_score"] == 0.9
            assert entity["properties"]["source"] == "Syllogist - Test Skill Inference"
            break

    assert inferred_skill_found, "Syllogist failed to infer the HAS_SKILL relationship."
