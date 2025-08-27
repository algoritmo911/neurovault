import uuid
from datetime import datetime
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field

class DataStream(BaseModel):
    """
    Represents a single stream of data within a Neuro-Event payload.
    e.g., a text transcript, an audio file, sensor data, etc.
    """
    stream_type: str = Field(..., description="MIME type of the data stream, e.g., 'text/plain' or 'image/jpeg'.")
    content: bytes = Field(..., description="The raw byte content of the data stream.")
    # In a real implementation, content might be a URL to object storage.
    # For now, we handle it directly.

class NeuroEventPayload(BaseModel):
    """
    The payload of a Neuro-Event, containing multiple data streams.
    """
    streams: List[DataStream]

class NeuroEvent(BaseModel):
    """
    The core data structure for a "memory" in the Mnemosyne Protocol.
    It's a structured object encapsulating a single moment of experience.
    """
    id: uuid.UUID = Field(default_factory=uuid.uuid4, description="Unique identifier for the event (UUIDv4 for simplicity, can be upgraded to v7).")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="The precise time the event occurred.")
    source_id: str = Field(..., description="The ID of the user, agent, or sensor that generated the event.")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Structured metadata (e.g., geolocation, device info).")
    payload: NeuroEventPayload = Field(..., description="The main content of the event, composed of various data streams.")
    signature: Optional[str] = Field(None, description="The Mnemonic Signature, a crypto-semantic hash of the event.")
