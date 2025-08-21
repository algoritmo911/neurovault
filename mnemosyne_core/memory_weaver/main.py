from fastapi import FastAPI
from pydantic import BaseModel
import strawberry
from strawberry.fastapi import GraphQLRouter
from .graphql_api import Query
from .connectors import process_text_input

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

class IngestData(BaseModel):
    text: str
    source: str

@app.post("/ingest/", tags=["Data Ingestion"])
async def ingest_data(data: IngestData):
    """
    Receives text data, processes it, and adds it to the knowledge graph.
    """
    process_text_input(data.text, data.source)
    return {"message": "Data ingested successfully"}

@app.get("/", tags=["Health Check"])
def read_root():
    """
    Root endpoint for health checks.
    """
    return {"message": "Welcome to the MemoryWeaver API"}
