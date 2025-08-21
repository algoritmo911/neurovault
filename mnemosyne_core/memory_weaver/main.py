from fastapi import FastAPI
from pydantic import BaseModel
import strawberry
from strawberry.fastapi import GraphQLRouter
from fastapi import HTTPException
from .graphql_api import Query
from .connectors import process_text_input
from .syllogist import Syllogist
from .oracle import Oracle
from .graph_db import GraphDB
from .nlp import NLPProcessor
from .economic_core import wallet
from .config import economic_config

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
    This action has a cost.
    """
    cost = economic_config.COST_INGEST
    if wallet.get_balance() < cost:
        raise HTTPException(status_code=402, detail=f"Payment Required. Current balance: {wallet.get_balance()}, Cost: {cost}")

    process_text_input(data.text, data.source, data.properties)

    wallet.debit(cost)
    return {"message": "Data ingested successfully"}

@app.post("/syllogist/run/", tags=["Inference Engine"])
async def run_syllogist():
    """
    Triggers a full inference run by the Syllogist module.
    This action has a significant cost.
    """
    cost = economic_config.COST_SYLLOGIST_RUN
    if wallet.get_balance() < cost:
        raise HTTPException(status_code=402, detail=f"Payment Required. Current balance: {wallet.get_balance()}, Cost: {cost}")

    syllogist = Syllogist()
    syllogist.run_inference()

    wallet.debit(cost)
    return {"message": "Syllogist inference run completed."}

class HypothesizeRequest(BaseModel):
    question: str

@app.post("/hypothesize/", tags=["Hypothesis Generation"])
async def hypothesize(request: HypothesizeRequest):
    """
    Generates hypotheses based on an open-ended question.
    This action has a cost.
    """
    cost = economic_config.COST_HYPOTHESIZE
    if wallet.get_balance() < cost:
        raise HTTPException(status_code=402, detail=f"Payment Required. Current balance: {wallet.get_balance()}, Cost: {cost}")

    db = GraphDB()
    nlp = NLPProcessor()
    oracle = Oracle(db, nlp)

    hypotheses = oracle.generate_hypotheses(request.question)

    db.close()
    wallet.debit(cost)
    return {"hypotheses": hypotheses}

class CreditRequest(BaseModel):
    amount: float

@app.post("/wallet/credit", tags=["Wallet"])
async def credit_wallet(request: CreditRequest):
    """
    Adds funds to the agent's wallet.
    """
    if request.amount <= 0:
        raise HTTPException(status_code=400, detail="Credit amount must be positive.")

    wallet.credit(request.amount)
    new_balance = wallet.get_balance()
    return {"message": "Wallet credited successfully", "new_balance": new_balance}

@app.get("/wallet/balance", tags=["Wallet"])
async def get_wallet_balance():
    """
    Retrieves the current balance of the agent's wallet.
    """
    balance = wallet.get_balance()
    return {"balance": balance}

@app.get("/", tags=["Health Check"])
def read_root():
    """
    Root endpoint for health checks.
    """
    return {"message": "Welcome to the MemoryWeaver API"}
