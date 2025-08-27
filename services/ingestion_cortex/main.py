import json
import uuid
import nats
import redis
import numpy as np
from fastapi import FastAPI, UploadFile, File, Form, HTTPException, status, BackgroundTasks
from fastapi.responses import JSONResponse
from typing import List, Dict, Any
from datetime import datetime, timezone
from contextlib import asynccontextmanager
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity

from common.models import NeuroEvent, DataStream, NeuroEventPayload

# --- Constants ---
SHORT_TERM_MEMORY_MAX_SIZE = 100
REDIS_IDS_LIST_KEY = "short_term_memory:ids"
REDIS_VECTOR_HASH_KEY_PREFIX = "event_vector:"

# This dictionary will hold our model and clients, loaded during the app's lifespan.
context = {}

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manages the application's lifespan."""
    print("Startup: Loading Sentence Transformer model...")
    context["model"] = SentenceTransformer('all-MiniLM-L6-v2')
    print("Startup: Model loaded.")

    print("Startup: Connecting to Redis...")
    context["redis_client"] = redis.Redis(host='localhost', port=6379, db=0, decode_responses=False)
    context["redis_client"].ping()
    print("Startup: Redis connection successful.")

    yield

    print("Shutdown: Cleaning up resources...")
    context["redis_client"].close()
    print("Shutdown: Redis connection closed.")
    context.clear()

app = FastAPI(
    title="Ingestion Cortex (Sentient Synapse)",
    description="The cognitive entry point for all Neuro-Events into the Mnemosyne Protocol.",
    version="1.1.0",
    lifespan=lifespan
)

# --- NATS Publisher ---
async def publish_event_to_broker(subject: str, event_data: str):
    """Connects to NATS and publishes the event."""
    try:
        nc = await nats.connect("nats://localhost:4222")
        await nc.publish(subject, event_data.encode('utf-8'))
        await nc.close()
        print(f"Successfully published event to NATS subject '{subject}'.")
    except Exception as e:
        print(f"BACKGROUND TASK ERROR: Could not publish to NATS: {e}")

# --- Awareness Trigger Logic ---
ANOMALY_KEYWORDS = {"urgent", "help", "error", "failed", "critical", "alert"}

def is_anomaly(text: str) -> bool:
    """
    Performs a simple keyword check to identify potential anomalies.
    """
    return any(keyword in text.lower() for keyword in ANOMALY_KEYWORDS)

def get_event_type_and_payload(
    score: float, text: str, event: NeuroEvent
) -> (str, str):
    """
    Determines the event type and payload based on resonance score and content.
    """
    # Anomaly check takes precedence
    if is_anomaly(text):
        subject = "event.type.anomaly.priority"
        payload = event.model_dump()
        payload["metadata"]["anomaly_reason"] = "Keyword detected"
        # Use a custom JSON encoder to handle UUID and datetime objects
        return subject, json.dumps(payload, default=str)

    if score > 0.90:
        subject = "event.type.reinforcement"
        # Here we would need the ID of the event it resonated with.
        # This is a simplification; a real implementation would fetch it.
        payload = event.model_dump()
        payload["metadata"]["resonant_with"] = "unknown_for_now"
        # Use a custom JSON encoder to handle UUID and datetime objects
        return subject, json.dumps(payload, default=str)

    if score < 0.75:
        subject = "event.type.novel"
        return subject, event.model_dump_json()

    # Default case for scores between 0.75 and 0.90
    subject = "event.type.routine"
    return subject, event.model_dump_json()


# --- Resonance Check Logic ---
def check_resonance(event_id: str, new_vector: np.ndarray) -> float:
    """
    Checks the new vector against recent vectors in short-term memory (Redis).
    Returns the highest similarity score.
    """
    r = context["redis_client"]

    # 1. Get IDs of recent events
    recent_event_ids_bytes = r.lrange(REDIS_IDS_LIST_KEY, 0, SHORT_TERM_MEMORY_MAX_SIZE)
    recent_event_ids = [id_bytes.decode('utf-8') for id_bytes in recent_event_ids_bytes]

    if not recent_event_ids:
        print("Short-term memory is empty. Skipping resonance check.")
        max_similarity = 0.0
    else:
        # 2. Fetch the vectors for these IDs
        pipe = r.pipeline()
        for id_str in recent_event_ids:
            pipe.get(f"{REDIS_VECTOR_HASH_KEY_PREFIX}{id_str}")

        recent_vectors_bytes = pipe.execute()

        # Filter out None values for vectors that might have expired
        recent_vectors = [np.frombuffer(v, dtype=np.float32) for v in recent_vectors_bytes if v]

        if not recent_vectors:
            print("No valid recent vectors found. Skipping resonance check.")
            max_similarity = 0.0
        else:
            # 3. Calculate cosine similarity
            # Reshape new_vector to (1, n_features) for sklearn
            similarities = cosine_similarity(new_vector.reshape(1, -1), recent_vectors)
            max_similarity = np.max(similarities)
            print(f"Resonance check complete. Max similarity: {max_similarity:.4f}")

    # 4. Add the new event to short-term memory
    # Use a pipeline for atomicity
    pipe = r.pipeline()
    # Store the new vector as bytes
    pipe.set(f"{REDIS_VECTOR_HASH_KEY_PREFIX}{event_id}", new_vector.astype(np.float32).tobytes())
    # Add the new ID to the list and trim the list
    pipe.lpush(REDIS_IDS_LIST_KEY, event_id)
    pipe.ltrim(REDIS_IDS_LIST_KEY, 0, SHORT_TERM_MEMORY_MAX_SIZE - 1)
    pipe.execute()
    print(f"Event {event_id} added to short-term memory.")

    return float(max_similarity)

# --- API Endpoint ---
@app.post("/ingest/", status_code=status.HTTP_202_ACCEPTED)
async def ingest_neuro_event(
    background_tasks: BackgroundTasks,
    source_id: str = Form(...),
    metadata_json: str = Form(...),
    files: List[UploadFile] = File(...)
):
    trace_id = str(uuid.uuid4())
    event_id = str(uuid.uuid4())

    try:
        metadata = json.loads(metadata_json)
    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="Invalid JSON format for metadata_json.")

    data_streams = [DataStream(stream_type=f.content_type, content=await f.read()) for f in files]

    neuro_event = NeuroEvent(
        id=event_id,
        timestamp=datetime.now(timezone.utc),
        source_id=source_id,
        metadata=metadata,
        payload=NeuroEventPayload(streams=data_streams)
    )

    # --- The Sentient Synapse Workflow ---
    # 1. Sensation: Extract text and generate vector
    text_to_analyze = metadata.get("text")
    if not text_to_analyze or not isinstance(text_to_analyze, str):
        raise HTTPException(status_code=400, detail="Metadata must contain a 'text' field.")

    model = context["model"]
    new_vector = model.encode(text_to_analyze)

    # 2. Pattern Recognition: Check for resonance
    max_similarity_score = check_resonance(event_id, new_vector)

    # 3. Awareness Trigger: Decide event type based on resonance and content
    event_type, event_payload = get_event_type_and_payload(
        max_similarity_score, text_to_analyze, neuro_event
    )

    # 4. Publish the categorized event
    background_tasks.add_task(publish_event_to_broker, event_type, event_payload)

    return {
        "message": "Neuro-Event processed and categorized.",
        "trace_id": trace_id,
        "event_id": event_id,
        "resonance_score": max_similarity_score
    }

@app.get("/", tags=["Health Check"])
def read_root():
    return {"message": "Welcome to the Ingestion Cortex (Sentient Synapse)"}
