import logging
import queue
import threading
import time
from typing import Dict, Any

from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

# 1. Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# 2. In-memory queue for asynchronous processing
data_queue = queue.Queue()

# 3. Pydantic model for incoming data
class IngestionData(BaseModel):
    source: str
    type: str
    content: str
    metadata: Dict[str, Any] = Field(default_factory=dict)

# 4. Lifespan manager for the application
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Start the background worker
    worker_thread = threading.Thread(target=worker, daemon=True)
    worker_thread.start()
    logging.info("Background worker started.")
    yield
    # Clean up and shutdown logic can be added here if needed
    logging.info("Application is shutting down.")

# 5. FastAPI application instance
app = FastAPI(
    title="NeuroVault - Memory Factory",
    description="Data ingestion pipeline for the Memory Factory.",
    version="0.1.0",
    lifespan=lifespan
)

# 5. API Endpoint for data ingestion
@app.post("/ingest")
async def ingest_data(data: IngestionData):
    """
    Receives data, validates it, and puts it into a queue for processing.
    """
    # Basic validation: ensure content is not empty
    if not data.content.strip():
        logging.warning(f"Invalid data from source '{data.source}': content is empty.")
        raise HTTPException(
            status_code=422,
            detail="Content cannot be empty."
        )

    # Put valid data into the queue
    data_queue.put(data)
    logging.info(f"Data from source '{data.source}' received and queued for processing.")

    return {"message": "Data received and queued successfully."}

# 6. Background worker function (placeholder)
def worker():
    """
    Processes data from the queue.
    """
    while True:
        try:
            # The `get` call is blocking, so it will wait until an item is available
            item = data_queue.get()

            logging.info(f"Starting to process item from source '{item.source}'")
            # In a real scenario, this is where you'd process the data.
            # For this MVP, we just log. The original request was to "log 'Starting to process item X from source Y' and remove the element from the queue"

            # `task_done()` is called to signal that the processing of the item is complete.
            data_queue.task_done()
            # No need to log "finished" as per the prompt, just that it started.

        except Exception as e:
            # Log any exception that occurs during processing
            logging.error(f"Error processing item: {e}")


# The old startup event is now replaced by the lifespan manager.
