# Alpha Cabinet for User 001

This directory contains the personal memory cabinet for User 001.

## Running the Cabinet

To run the cabinet, you need to have Python, FastAPI, and Uvicorn installed.

1.  **Install dependencies:**
    ```bash
    pip install fastapi "uvicorn[standard]"
    ```

2.  **Run the application:**
    Navigate to the `mnemosyne_core/alpha_cabinets/user_001` directory and run the following command:
    ```bash
    uvicorn main:app --reload
    ```
    The application will be available at `http://127.0.0.1:8000`.

## API Endpoints

- `GET /`: Welcome message.
- `POST /memories/`: Create a new memory.
- `GET /memories/`: Get a list of all memories.

You can access the interactive API documentation at `http://127.0.0.1:8000/docs`.
