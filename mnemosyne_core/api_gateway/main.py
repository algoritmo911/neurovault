from fastapi import FastAPI, Request, HTTPException, status
from typing import Dict, Any

from mnemosyne_core.data_ingestion.ingest_service import IngestionService
from mnemosyne_core.models.memory import MemoryEvent

# Initialize the FastAPI app
app = FastAPI(
    title="Mnemosyne Core API",
    description="API for the Factory of Memories.",
    version="0.1.0",
)

# Create a singleton instance of the IngestionService
# In a real application, this might be managed with a dependency injection system.
ingestion_service = IngestionService()

@app.post(
    "/ingest",
    response_model=MemoryEvent,
    status_code=status.HTTP_201_CREATED,
    summary="Ingest a new memory event",
    tags=["Ingestion"],
)
async def ingest_event(request: Request):
    """
    Accepts a raw JSON payload representing a memory event, validates it,
    processes it, and stores it.

    - **source**: The origin of the memory event (e.g., `telegram`, `github`).
    - **ts**: The ISO 8601 timestamp of the event.
    - **author**: The author of the event (e.g., `user`, `agent`).
    - **payload**: The content of the event, including `text`.
    - **provenance**: Optional details about the event's origin.
    """
    try:
        event_data = await request.json()
        processed_event = ingestion_service.process_event(event_data)
        return processed_event
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid event data: {e}",
        )
    except Exception as e:
        # Catch-all for other unexpected errors
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An unexpected error occurred: {e}",
        )

@app.get("/health", status_code=status.HTTP_200_OK, tags=["System"])
async def health_check():
    """
    Simple health check endpoint.
    """
    return {"status": "ok"}
