from fastapi import FastAPI
from typing import List, Dict, Any

app = FastAPI(
    title="Фабрика Воспоминаний",
    description="API для доступа к базе знаний.",
    version="0.1.0",
)

def search_vector_db(topic: str) -> List[Dict[str, Any]]:
    """
    Заглушка для поиска в векторной базе данных.
    Имитирует поиск по заданной теме.
    """
    print(f"Поиск в базе данных по теме: {topic}")
    if topic == "Sapiens Coin":
        return [
            {
                "id": "doc123",
                "content": "Sapiens Coin - это инновационная криптовалюта, основанная на принципах децентрализованной экономики и коллективного интеллекта.",
                "source": "whitepaper_v1.pdf",
                "relevance_score": 0.95,
            },
            {
                "id": "doc456",
                "content": "Для майнинга Sapiens Coin используется алгоритм Proof-of-Wisdom, который вознаграждает пользователей за вклад в базу знаний.",
                "source": "technical_docs_v2.1.md",
                "relevance_score": 0.92,
            },
            {
                "id": "doc789",
                "content": "Команда проекта Sapiens Coin объявила о партнерстве с ведущими исследовательскими институтами.",
                "source": "press_release_q2_2024.txt",
                "relevance_score": 0.88,
            },
        ]
    return []

@app.get("/query")
def query_knowledge_base(topic: str):
    """
    Принимает запрос на поиск информации в базе знаний по определенной теме.
    """
    search_results = search_vector_db(topic)
    return {"status": "success", "data": search_results}

# Пример эндпоинта для проверки, что сервер работает
@app.get("/")
def read_root():
    return {"message": "Добро пожаловать на Фабрику Воспоминаний!"}
