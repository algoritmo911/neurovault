import strawberry
from strawberry.scalars import JSON
from .graph_db import GraphDB
from typing import List, Optional, Any

@strawberry.type
class Entity:
    """A node in the knowledge graph."""
    name: str
    labels: List[str]

@strawberry.type
class RelatedEntity:
    """An entity that is related to another entity in the graph."""
    name: str
    labels: List[str]
    relationship: str
    properties: Optional[JSON]

@strawberry.type
class Query:
    """GraphQL queries for the MemoryWeaver service."""

    @strawberry.field
    def find_entity(self, name: str, label: str) -> Optional[Entity]:
        """Finds an entity by name and label."""
        db = GraphDB()
        try:
            result = db.find_entity(name, label)
            if result:
                node = result["e"]
                return Entity(name=node["name"], labels=list(node.labels))
            return None
        finally:
            db.close()

    @strawberry.field
    def get_related_entities(self, name: str, label: str) -> List[RelatedEntity]:
        """Finds entities related to a given entity."""
        db = GraphDB()
        try:
            results = db.get_related_entities(name, label)
            return [RelatedEntity(name=r["name"], labels=r["labels"], relationship=r["relationship"]) for r in results]
        finally:
            db.close()
