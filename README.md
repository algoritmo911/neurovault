# Neurovault - Memory Module

This project contains the memory module for Neurovault. It provides a simple API for saving and retrieving memories.

## Setup

1. Install the dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Run the application:
   ```bash
   python neurovault/memory_module/api.py
   ```

## API Endpoints

- `POST /save_memory`: Saves a new memory.
  - **Request body**: `{"memory_text": "This is a memory."}`
  - **Response**: `{"message": "Memory saved successfully", "memory_id": 0}`

- `GET /retrieve_memory/<memory_id>`: Retrieves a memory by its ID.
  - **Response**: `{"memory_id": 0, "memory_text": "This is a memory."}`
