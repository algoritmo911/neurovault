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

class EconomicConfig:
    """
    Configuration for the economic model of the agent.
    Defines the cost for various actions.
    """
    COST_INGEST = 1.0
    COST_SYLLOGIST_RUN = 25.0
    COST_HYPOTHESIZE = 5.0

economic_config = EconomicConfig()
