import os

class Neo4jConfig:
    """
    Configuration for the Neo4j database connection.
    """
    NEO4J_URI = os.getenv("NEO4J_URI", "bolt://127.0.0.1:7687")
    NEO4J_USER = os.getenv("NEO4J_USER", "neo4j")
    NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD", "password")

# Instantiate the config
neo4j_config = Neo4jConfig()
