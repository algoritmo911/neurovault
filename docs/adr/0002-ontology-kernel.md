# ADR-0002: Memory Event Ontology Kernel

**Status:** Proposed

## Context

For the "Factory of Memories" to function, all incoming data, regardless of its source, must be normalized into a single, unified structure. This canonical data model—the "Memory Event"—needs to be rich enough to capture not just the raw data, but also its meaning, context, and significance. This is the foundation of the entire system's ability to reason about the past.

## Decision

We have designed a comprehensive Pydantic model, `MemoryEvent`, located in `mnemosyne_core/models/memory.py`, to serve as this canonical representation. This model is not just a data container; it is an ontological kernel that structures information into distinct layers:

1.  **Core Metadata:**
    -   `event_id` (UUID): A unique, immutable identifier for the event.
    -   `source` (Enum): The system or channel of origin (`telegram`, `github`, etc.).
    -   `ts` (datetime): The precise timestamp of the event's occurrence.
    -   `author` (Enum): The entity responsible for the event (`user`, `agent`, `system`).

2.  **Payload:** A flexible object containing the core content:
    -   `text` (str): The primary textual content.
    -   `meta` (dict): A key-value store for any additional, source-specific metadata.
    -   `attachments` (list): A list to hold references to any associated files or objects.

3.  **Provenance:** A dedicated object to ensure full traceability of every memory back to its exact origin (e.g., a specific Git commit hash, a repository branch, or a file path). This is critical for auditing and debugging.

4.  **Ontological Classification (`MemoryOntology` object):** This is the "sense-making" layer of the model.
    -   `type` (Enum): Every event is classified according to a core ontology:
        -   **Episodic:** Concrete events and experiences ("what happened").
        -   **Semantic:** Facts, concepts, and definitions ("what is true").
        -   **Procedural:** Skills, instructions, and workflows ("how to do something").
        -   **Attentional:** Triggers or points of focus.
        -   **Valence:** The affective dimension of the memory.
    -   `valence` (Model): A nested object to score the event's perceived `utility`, `stress`, and `fatigue`. This is a crucial input for the future Predictive Engine.

## Consequences

### Positive
- **Rich, Structured Data:** By enforcing this structure at the point of ingestion, we ensure that all data in the memory fabric is immediately ready for complex analysis.
- **Foundation for AI:** The explicit ontological classification (`type`, `valence`) provides the necessary features for downstream AI/ML models to understand and reason about the data without expensive preprocessing.
- **Extensibility:** The model is easily extensible. New ontological fields or metadata can be added to the `MemoryOntology` or `Payload` without breaking existing functionality.

### Negative
- **Initial Complexity:** The model is more complex than a simple key-value store, which introduces a minor overhead during ingestion.
- **Under-utilized at First:** The full power of the ontological fields will only be unlocked once the Memory Fabric (Stage 2) and Predictive Engine (Stage 3) are implemented to act upon them. Until then, they are being collected but not fully utilized.
