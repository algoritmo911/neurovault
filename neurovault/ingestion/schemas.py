from pydantic import BaseModel
from typing import List, Dict, Any

class Entity(BaseModel):
    id: str
    label: str
    properties: Dict[str, Any]

class Relationship(BaseModel):
    source_id: str
    target_id: str
    type: str
    properties: Dict[str, Any]

class IngestionData(BaseModel):
    entities: List[Entity]
    relationships: List[Relationship]
