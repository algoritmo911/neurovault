import uuid
from datetime import datetime
from enum import Enum
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field, ConfigDict

class SourceEnum(str, Enum):
    """Enumeration for the source of a memory event."""
    TELEGRAM = "telegram"
    GITHUB = "github"
    NOTES = "notes"
    N8N = "n8n"
    SYSTEM = "system"

class AuthorEnum(str, Enum):
    """Enumeration for the author of a memory event."""
    USER = "user"
    AGENT = "agent"
    SYSTEM = "system"

class Payload(BaseModel):
    """The data payload of a memory event."""
    text: str
    meta: Optional[Dict[str, Any]] = None
    attachments: Optional[List[Any]] = None

class Provenance(BaseModel):
    """The detailed origin of the event for traceability."""
    repo: Optional[str] = None
    branch: Optional[str] = None
    commit: Optional[str] = None

class MemoryTypeEnum(str, Enum):
    """Enumeration for the type of memory based on the ontology."""
    EPISODIC = "Episodic" # Events, experiences
    SEMANTIC = "Semantic" # Facts, concepts, terms
    PROCEDURAL = "Procedural" # Skills, steps, how-tos
    ATTENTIONAL = "Attentional" # Triggers, focus points
    VALENCE = "Valence" # Utility, stress, fatigue scores

class Valence(BaseModel):
    """Represents the utility, stress, and fatigue associated with a memory."""
    utility: float = 0.0
    stress: float = 0.0
    fatigue: float = 0.0

class MemoryOntology(BaseModel):
    """The ontological classification of the memory event."""
    type: MemoryTypeEnum = MemoryTypeEnum.EPISODIC
    valence: Valence = Field(default_factory=Valence)
    # Further semantic and procedural links can be added here
    # e.g., entities: List[str] = []

class MemoryEvent(BaseModel):
    """
    Represents a single, normalized memory event, the fundamental unit of the Memory Fabric.
    """
    event_id: uuid.UUID = Field(default_factory=uuid.uuid4, alias="id")
    source: SourceEnum
    ts: datetime
    author: AuthorEnum
    payload: Payload
    provenance: Optional[Provenance] = None
    ontology: MemoryOntology = Field(default_factory=MemoryOntology)

    model_config = ConfigDict(
        populate_by_name=True,
        use_enum_values=True, # Still useful for ensuring string values in output
    )


class Narrative(BaseModel):
    """
    Represents a higher-level story or case, consolidated from multiple memory events.
    For example, "Work on feature X" or "Debugged production issue Y".
    """
    narrative_id: uuid.UUID = Field(default_factory=uuid.uuid4, alias="id")
    title: str
    summary: Optional[str] = None
    event_ids: List[uuid.UUID]
    start_time: datetime
    end_time: datetime
    metadata: Optional[Dict[str, Any]] = None

    model_config = ConfigDict(
        populate_by_name=True,
    )
