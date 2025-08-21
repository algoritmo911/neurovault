from fastapi import FastAPI
from pydantic import BaseModel
import strawberry
from strawberry.fastapi import GraphQLRouter
from .graphql_api import Query
from .connectors import process_text_input
from .syllogist import Syllogist
from .oracle import Oracle
from .graph_db import GraphDB
from .nlp import NLPProcessor

# Create the Strawberry GraphQL schema
schema = strawberry.Schema(query=Query)

# Create the GraphQL router
graphql_app = GraphQLRouter(schema)

# Create the FastAPI app
app = FastAPI(
    title="MemoryWeaver API",
    description="API for the MemoryWeaver service, providing GraphQL access to the knowledge graph.",
    version="0.1.0",
)

# Mount the GraphQL app
app.include_router(graphql_app, prefix="/graphql")

from typing import Optional, Dict, Any

class IngestData(BaseModel):
    text: str
    source: str
    properties: Optional[Dict[str, Any]] = None

@app.post("/ingest/", tags=["Data Ingestion"])
async def ingest_data(data: IngestData):
    """
    Receives text data, processes it, and adds it to the knowledge graph.
    """
    process_text_input(data.text, data.source, data.properties)
    return {"message": "Data ingested successfully"}

@app.post("/syllogist/run/", tags=["Inference Engine"])
async def run_syllogist():
    """
    Triggers a full inference run by the Syllogist module.
    """
    syllogist = Syllogist()
    syllogist.run_inference()
    return {"message": "Syllogist inference run completed."}

class HypothesizeRequest(BaseModel):
    question: str

@app.post("/hypothesize/", tags=["Hypothesis Generation"])
async def hypothesize(request: HypothesizeRequest):
    """
    Generates hypotheses based on an open-ended question.
    """
    db = GraphDB()
    nlp = NLPProcessor()
    oracle = Oracle(db, nlp)

    hypotheses = oracle.generate_hypotheses(request.question)

    db.close()
    return {"hypotheses": hypotheses}

@app.get("/", tags=["Health Check"])
def read_root():
    """
    Root endpoint for health checks.
    """
    return {"message": "Welcome to the MemoryWeaver API"}
