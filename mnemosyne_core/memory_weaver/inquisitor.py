from .graph_db import GraphDB
from collections import namedtuple

# A simple data structure to represent a dissonance event.
CognitiveDissonanceEvent = namedtuple("CognitiveDissonanceEvent", ["new_fact", "conflicting_fact"])

class Inquisitor:
    """
    The Inquisitor module protects the integrity of the knowledge graph by
    checking for contradictions before new information is added.
    """

    # Define which relationships are "functional", meaning a source node
    # can only have one of these relationships active at a time.
    # For example, a company can only have one CEO.
    FUNCTIONAL_RELATIONSHIPS = ["HAS_CEO", "HAS_BUDGET"]

    def __init__(self, db: GraphDB):
        """
        Initializes the Inquisitor with a database connection.
        """
        self.db = db

    def check_for_contradictions(self, subject_name: str, subject_label: str, relationship_type: str, target_name: str) -> CognitiveDissonanceEvent | None:
        """
        Checks if a new proposed fact contradicts existing knowledge,
        focusing on functional relationships.

        Returns:
            A CognitiveDissonanceEvent if a contradiction is found, otherwise None.
        """
        if relationship_type not in self.FUNCTIONAL_RELATIONSHIPS:
            return None

        # Query for existing relationships of the same functional type
        with self.db.driver.session() as session:
            query = (
                f"MATCH (a:{subject_label} {{name: $subject_name}})-[r:{relationship_type}]->(b) "
                "RETURN b.name AS name"
            )
            results = session.run(query, subject_name=subject_name).data()

            if results:
                existing_target_name = results[0]['name']
                if existing_target_name != target_name:
                    # Contradiction found!
                    new_fact = f"({subject_name})-[:{relationship_type}]->({target_name})"
                    conflicting_fact = f"({subject_name})-[:{relationship_type}]->({existing_target_name})"
                    print(f"Inquisitor: CONTRADICTION DETECTED! New fact '{new_fact}' conflicts with existing fact '{conflicting_fact}'")
                    return CognitiveDissonanceEvent(new_fact=new_fact, conflicting_fact=conflicting_fact)

        return None
