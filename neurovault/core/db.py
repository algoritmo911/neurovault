# neurovault/core/db.py
from neo4j import AsyncGraphDatabase
from .config import settings

# Создаем один экземпляр драйвера на все приложение
driver = AsyncGraphDatabase.driver(settings.NEO4J_URI, auth=(settings.NEO4J_USER, settings.NEO4J_PASSWORD))

async def get_db_session():
    """
    Dependency to get an async database session.
    """
    session = None
    try:
        # Важно: driver.session() возвращает AsyncSession
        session = driver.session()
        yield session
    finally:
        if session:
            await session.close()
