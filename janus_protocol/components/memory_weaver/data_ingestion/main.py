from fastapi import FastAPI, UploadFile, File
from typing import Optional

app = FastAPI(
    title="Data Ingestion API",
    description="API для загрузки и обработки воспоминаний в проекте 'Фабрика Воспоминаний'.",
    version="0.1.0",
)

@app.post("/upload/", tags=["Memories"])
async def upload_memory(file: UploadFile = File(...)):
    """
    Принимает файл воспоминания (аудио, видео, фото, текст).

    В этой базовой версии API просто возвращает метаданные файла.
    В будущем здесь будет реализована логика для:
    - **Валидации данных**: Проверка формата и размера файла.
    - **Конвертации медиа**: Приведение к единому формату.
    - **Извлечения метаданных**: Анализ файла для получения базовой информации.
    """
    return {"filename": file.filename, "content_type": file.content_type, "message": "File uploaded successfully"}

@app.get("/", tags=["Health Check"])
def read_root():
    """
    Корневой эндпоинт для проверки доступности сервиса.
    """
    return {"message": "Welcome to the Data Ingestion API for Mnemosyne Core"}
