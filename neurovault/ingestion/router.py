# neurovault/ingestion/router.py
from fastapi import APIRouter, Depends
from neo4j import AsyncSession
from ..core.db import get_db_session
from . import schemas, services

router = APIRouter()

@router.post("/ingest/", status_code=201)
async def ingest_data(
    data: schemas.IngestionData,
    session: AsyncSession = Depends(get_db_session) # <--- Вот магия!
):
    # Теперь сервис получает готовую сессию
    result = await services.create_knowledge_graph_data(session, data)
    return result
