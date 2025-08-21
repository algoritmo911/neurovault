# NeuroVault

NeuroVault is a service for ingesting and storing knowledge graphs. It provides an API endpoint to receive structured data (entities and relationships) and persists them in a Neo4j database.

## Getting Started

### Prerequisites

- Python 3.9+
- A running Neo4j database

### Installation

1.  Clone the repository:
    ```bash
    git clone <repository-url>
    cd neurovault
    ```
2.  Install the dependencies:
    ```bash
    pip install -r requirements.txt
    ```

### Configuration

The application can be configured using environment variables. You can create a `.env` file in the root of the project to store your configuration.

-   `NEO4J_URI`: The URI of your Neo4j database (e.g., `bolt://localhost:7687`)
-   `NEO4J_USER`: The username for your Neo4j database (e.g., `neo4j`)
-   `NEO4J_PASSWORD`: The password for your Neo4j database

### Running the Application

To run the application, use `uvicorn`:

```bash
uvicorn neurovault.main:app --reload
```

The application will be available at `http://127.0.0.1:8000`.

## API

The API documentation is available at `http://127.0.0.1:8000/docs` when the application is running.

### Ingestion Endpoint

-   **URL:** `/api/v1/ingest`
-   **Method:** `POST`
-   **Body:** See the `IngestionPayload` schema in the API documentation.
