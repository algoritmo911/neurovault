from neo4j import GraphDatabase
from .config import neo4j_config

class GraphDB:
    """
    A class to handle the connection and operations with the Neo4j database.
    """

    def __init__(self):
        """
        Initializes the database connection.
        """
        self.driver = GraphDatabase.driver(
            neo4j_config.NEO4J_URI,
            auth=(neo4j_config.NEO4J_USER, neo4j_config.NEO4J_PASSWORD)
        )

    def close(self):
        """
        Closes the database connection.
        """
        if self.driver:
            self.driver.close()

    def add_entity(self, name: str, label: str, properties: dict = None):
        """
        Adds a new entity node to the graph, with optional properties.

        Args:
            name (str): The name of the entity.
            label (str): The label of the entity (e.g., "Person", "Organization").
            properties (dict, optional): A dictionary of properties for the entity.
        """
        with self.driver.session() as session:
            session.execute_write(self._create_entity, name, label, properties)

    @staticmethod
    def _create_entity(tx, name, label, properties):
        query = f"MERGE (e:{label} {{name: $name}})"
        if properties:
            query += " SET e += $properties"
        tx.run(query, name=name, properties=properties or {})

    def add_relationship(self, source_name: str, source_label: str, target_name: str, target_label: str, relationship_type: str, properties: dict = None):
        """
        Creates a relationship between two entities in the graph, with optional properties.

        Args:
            source_name (str): The name of the source entity.
            source_label (str): The label of the source entity.
            target_name (str): The name of the target entity.
            target_label (str): The label of the target entity.
            relationship_type (str): The type of the relationship (e.g., "MENTIONED_IN").
            properties (dict, optional): A dictionary of properties for the relationship.
        """
        with self.driver.session() as session:
            session.execute_write(
                self._create_relationship,
                source_name,
                source_label,
                target_name,
                target_label,
                relationship_type,
                properties
            )

    @staticmethod
    def _create_relationship(tx, source_name, source_label, target_name, target_label, relationship_type, properties):
        query = (
            f"MATCH (a:{source_label} {{name: $source_name}}) "
            f"MATCH (b:{target_label} {{name: $target_name}}) "
            f"MERGE (a)-[r:{relationship_type}]->(b)"
        )
        if properties:
            query += " SET r += $properties"
        tx.run(query, source_name=source_name, target_name=target_name, properties=properties or {})

    def find_entity(self, name: str, label: str):
        """
        Finds an entity by name and label.
        """
        with self.driver.session() as session:
            result = session.execute_read(self._find_entity, name, label)
            return result

    @staticmethod
    def _find_entity(tx, name, label):
        query = f"MATCH (e:{label} {{name: $name}}) RETURN e"
        result = tx.run(query, name=name)
        return result.single()

    def get_related_entities(self, name: str, label: str):
        """
        Finds entities related to a given entity.
        """
        with self.driver.session() as session:
            result = session.execute_read(self._get_related_entities, name, label)
            return result

    @staticmethod
    def _get_related_entities(tx, name, label):
        query = (
            f"MATCH (a:{label} {{name: $name}})-[r]-(b) "
            "RETURN b.name AS name, labels(b) AS labels, type(r) AS relationship, properties(r) as properties"
        )
        result = tx.run(query, name=name)
        return [{
            "name": record["name"],
            "labels": record["labels"],
            "relationship": record["relationship"],
            "properties": record["properties"]
        } for record in result]

# Example usage (for testing purposes)
if __name__ == "__main__":
    db = GraphDB()
    try:
        # Add some entities and relationships for testing
        db.add_entity("Test User", "Person")
        db.add_entity("GraphQL", "Concept")
        db.add_relationship("Test User", "Person", "GraphQL", "Concept", "LEARNING_ABOUT")

        # Test the new methods
        entity = db.find_entity("GraphQL", "Concept")
        if entity:
            print("Found entity:", dict(entity["e"]))

        related_entities = db.get_related_entities("GraphQL", "Concept")
        print("Related entities:", related_entities)

    finally:
        db.close()
        print("Database connection closed.")
