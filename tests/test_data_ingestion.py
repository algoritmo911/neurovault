import pytest
from httpx import AsyncClient
from mnemosyne_core.data_ingestion.main import app
import io

# Mark all tests in this file as asyncio
pytestmark = pytest.mark.asyncio

async def test_read_root():
    """Тестирует корневой эндпоинт."""
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Welcome to the Data Ingestion API for Mnemosyne Core"}

async def test_upload_memory_success():
    """Тестирует успешную загрузку файла."""
    # Создаем "файл" в памяти
    file_content = b"my test memory data"
    file_to_upload = ("test_memory.txt", io.BytesIO(file_content), "text/plain")

    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.post("/upload/", files={"file": file_to_upload})

    assert response.status_code == 200
    response_json = response.json()
    assert response_json["filename"] == "test_memory.txt"
    assert response_json["content_type"] == "text/plain"
    assert response_json["message"] == "File uploaded successfully"

async def test_upload_memory_no_file():
    """Тестирует случай, когда файл не был отправлен."""
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.post("/upload/") # Файл не прикреплен

    # FastAPI должен вернуть ошибку 422 Unprocessable Entity
    assert response.status_code == 422
    # Проверяем структуру ответа об ошибке валидации
    response_json = response.json()
    assert "detail" in response_json
    assert response_json["detail"][0]["type"] == "missing"
    assert response_json["detail"][0]["loc"] == ["body", "file"]
