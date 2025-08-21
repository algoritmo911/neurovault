# ADR-0001: Ingest Bus Architecture

**Status:** Proposed

## Context

The "Factory of Memories" requires a centralized and standardized way to receive memory events from a variety of sources, including Telegram, GitHub commits, notes, and n8n workflows. The ingestion mechanism must be reliable, easy to integrate with, and capable of validating incoming data to ensure the integrity of the memory fabric.

## Decision

We have decided to implement a synchronous RESTful API endpoint, `POST /ingest`, as the primary ingestion bus. This endpoint will be built using the **FastAPI** web framework.

The key characteristics of this approach are:
1.  **Standard Interface:** A simple HTTP POST request is a universally understood and easy-to-implement integration pattern for any client.
2.  **Schema-based Validation:** Incoming data will be validated against a formal **JSON Schema**. This ensures that all data entering the system conforms to the required structure.
3.  **Pydantic Models:** The validated data will be parsed into **Pydantic models** within the application. This provides strong typing, autocompletion, and a robust domain model for the service layer.
4.  **Separation of Concerns:** The API gateway (`api_gateway`) is responsible only for handling HTTP requests and responses, while the core business logic (validation, normalization, deduplication) is encapsulated in a separate `IngestionService`.

## Consequences

### Positive
- **Simplicity & Speed of Development:** FastAPI's tight integration with Pydantic allows for rapid development of a validated and self-documenting API.
- **Interoperability:** Any service or script that can make an HTTP request can push data into the Factory.
- **Robustness:** Strict validation at the entry point prevents malformed data from corrupting the system.

### Negative
- **Synchronous Nature:** The current implementation is synchronous. A client must wait for the request to be processed. For sources that generate a very high volume of events, this could become a bottleneck.
- **No Built-in Retry Mechanism:** If the API is down, clients are responsible for implementing their own retry logic.

### Future Considerations
If ingestion latency or volume becomes a concern, this simple API bus can be evolved. The `IngestionService` could be adapted to consume events from a message queue (e.g., RabbitMQ, Kafka) without changing its core logic. The API endpoint could then become a simple producer that publishes events to this queue. For the initial implementation, the direct API approach is sufficient and meets the requirements.
