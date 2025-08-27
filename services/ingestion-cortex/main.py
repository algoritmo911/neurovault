import json
import uuid
import nats
from fastapi import FastAPI, UploadFile, File, Form, HTTPException, status
from fastapi.responses import JSONResponse
from typing import List, Dict, Any
from datetime import datetime

# Assuming common models are in a directory that is in the PYTHONPATH
# In a real microservice setup, this might be a shared library
from common.models import NeuroEvent, DataStream, NeuroEventPayload

app = FastAPI(
    title="Ingestion Cortex",
    description="The single entry point for all Neuro-Events into the Mnemosyne Protocol.",
    version="1.0.0",
)

# Placeholder for NATS connection
# In a real app, this would be managed more robustly (e.g., on startup/shutdown)
NATS_URL = "nats://localhost:4222"

async def publish_to_nats(event: NeuroEvent):
    """
    Publishes a Neuro-Event to the NATS server.
    """
    try:
        nc = await nats.connect(NATS_URL)
        js = nc.jetstream()
        # Publish to the 'neuro.events.raw' subject (topic)
        await js.publish("neuro.events.raw", event.model_dump_json().encode('utf-8'))
        await nc.close()
        print(f"Successfully published event {event.id} to NATS.")
    except Exception as e:
        print(f"Error publishing to NATS: {e}")
        # In a real system, you'd have more robust error handling, maybe a retry mechanism or dead-letter queue.
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Could not publish event to message broker."
        )

@app.post("/ingest/", status_code=status.HTTP_202_ACCEPTED)
async def ingest_neuro_event(
    source_id: str = Form(...),
    metadata_json: str = Form(...),
    files: List[UploadFile] = File(...)
):
    """
    Accepts a complex Neuro-Event as a multipart/form-data payload.

    - **source_id**: The ID of the user, agent, or sensor.
    - **metadata_json**: A JSON string containing structured metadata.
    - **files**: One or more files representing the Data Streams of the event.
    """
    trace_id = str(uuid.uuid4())

    try:
        metadata = json.loads(metadata_json)
    except json.JSONDecodeError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid JSON format for metadata_json.",
        )

    # Construct the DataStream objects from the uploaded files
    data_streams = []
    for file in files:
        content = await file.read()
        stream = DataStream(
            stream_type=file.content_type,
            content=content # In a real system, this might be a URI after uploading to GCS
        )
        data_streams.append(stream)

    # Assemble the full Neuro-Event
    neuro_event = NeuroEvent(
        id=uuid.uuid4(),
        timestamp=datetime.utcnow(),
        source_id=source_id,
        metadata=metadata,
        payload=NeuroEventPayload(streams=data_streams)
    )

    # Publish the event to the message broker
    # In a real scenario, this should not block the response.
    # We might use background tasks for this.
    await publish_to_nats(neuro_event)

    return JSONResponse(
        content={"message": "Neuro-Event accepted for processing.", "trace_id": trace_id},
        status_code=status.HTTP_202_ACCEPTED
    )

@app.get("/", tags=["Health Check"])
def read_root():
    """
    Корневой эндпоинт для проверки доступности сервиса.
    """
    return {"message": "Welcome to the Ingestion Cortex"}
