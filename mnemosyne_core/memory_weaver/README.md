# MemoryWeaver Service

## Overview

The MemoryWeaver is a central service in the Mnemosyne Core project, responsible for creating and maintaining a unified knowledge graph. It ingests data from various sources, uses Natural Language Processing (NLP) to extract entities and concepts, and stores them in a Neo4j graph database.

The service provides a powerful GraphQL API to query the knowledge graph, allowing other components like Katana to perform semantic searches and uncover relationships between different pieces of information.

## Setup

### 1. Install Dependencies

Ensure you have installed all the required Python packages from the root of the project:

```bash
pip install -r requirements.txt
```

### 2. Download NLP Model

The service uses a spaCy model for NLP. Download it with the following command:

```bash
python -m spacy download en_core_web_sm
```

### 3. Configure Neo4j Database

The MemoryWeaver service requires a running Neo4j instance. Configure the connection details using the following environment variables:

```bash
export NEO4J_URI="bolt://127.0.0.1:7687"
export NEO4J_USER="neo4j"
export NEO4J_PASSWORD="your_neo4j_password"
```

## Running the Service

You can run the service using `uvicorn`. From the root directory of the project, run:

```bash
uvicorn mnemosyne_core.memory_weaver.main:app --reload
```

The API will be available at `http://127.0.0.1:8000`.

## API Usage

### Data Ingestion

You can add new information to the knowledge graph by sending a POST request to the `/ingest/` endpoint.

**Example using `curl`:**

```bash
curl -X POST "http://127.0.0.1:8000/ingest/" \
-H "Content-Type: application/json" \
-d '{
  "text": "I had a meeting with Elon Musk to discuss the future of AI and space exploration.",
  "source": "sapiens_note_123"
}'
```

### GraphQL API

The GraphQL endpoint is available at `http://127.0.0.1:8000/graphql`. You can use any GraphQL client (like Postman or Insomnia) or access the interactive Strawberry documentation at the same URL in your browser.

**Example Query: Find related entities**

This query finds all entities related to the "AI" concept, which was ingested in the previous example.

```graphql
query {
  getRelatedEntities(name: "AI", label: "Concept") {
    name
    labels
    relationship
  }
}
```

**Example Response:**

```json
{
  "data": {
    "getRelatedEntities": [
      {
        "name": "sapiens_note_123",
        "labels": [
          "Source"
        ],
        "relationship": "CONTAINS"
      }
    ]
  }
}
```
