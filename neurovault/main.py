from fastapi import FastAPI
from .ingestion.router import router as ingestion_router

app = FastAPI(title="NeuroVault")

app.include_router(ingestion_router, prefix="/api/v1", tags=["ingestion"])

@app.get("/")
async def root():
    return {"message": "NeuroVault is running."}
