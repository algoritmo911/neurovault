# MemoryWeaver Service & Logos Protocol

## Overview

The MemoryWeaver is a central service in the Mnemosyne Core project, responsible for creating and maintaining a unified knowledge graph. It ingests data from various sources, uses Natural Language Processing (NLP) to extract entities and concepts, and stores them in a Neo4j graph database.

This service implements the **Logos Protocol**, which extends it beyond simple data storage into a dynamic **reasoning engine**.

## Core Concepts of the Logos Protocol

*   **Temporal & Probabilistic Graph**: Facts are not just true or false; they exist in time and with varying degrees of confidence.
*   **Syllogist (Inference Engine)**: The service can reason about its knowledge, inferring new facts from existing ones based on a set of rules.
*   **Inquisitor (Contradiction Detector)**: An "intellectual immune system" that checks new information for contradictions before it is committed to the graph.
*   **Oracle (Hypothesis Generator)**: Allows asking complex, open-ended questions to generate plausible hypotheses based on graph traversals.

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

The MemoryWeaver API provides several endpoints for interacting with the knowledge graph.

### 1. Data Ingestion (`/ingest/`)

This endpoint is used to add new information to the graph. It accepts raw text and optional structured properties.

**Basic Ingestion:**
```bash
curl -X POST "http://127.0.0.1:8000/ingest/" \
-H "Content-Type: application/json" \
-d '{
  "text": "The project uses Python.",
  "source": "manual_entry"
}'
```

**Ingestion with Temporal and Probabilistic Data:**
You can add metadata to facts using the `properties` field.

```bash
curl -X POST "http://127.0.0.1:8000/ingest/" \
-H "Content-Type: application/json" \
-d '{
  "text": "Anna started working on Project Apollo.",
  "source": "project_log_123",
  "properties": {
    "confidence_score": 0.95,
    "valid_from": "2023-01-15T09:00:00Z"
  }
}'
```

### 2. Inference Engine (`/syllogist/run/`)

Trigger a run of the Syllogist inference engine to derive new knowledge based on the rules in `rules.yaml`.

```bash
curl -X POST "http://127.0.0.1:8000/syllogist/run/"
```
*Response: `{"message": "Syllogist inference run completed."}`*

#### Syllogist Rule Format

Rules are defined in `rules.yaml`. They consist of `if` conditions (patterns to match) and a `then` clause (the new relationship to create).

**Example Rule:**
```yaml
- name: "Skill Inference from Project"
  description: "If a person works on a project, and that project uses a certain technology, infer that the person has a skill in that technology."
  if:
    - "(person:Person)-[:WORKS_ON]->(project:Project)"
    - "(project)-[:USES_TECH]->(tech:Concept)"
  then:
    - create: "(person)-[r:HAS_SKILL]->(tech)"
      properties:
        inferred: true
        confidence_score: 0.85
        source: "Syllogist - Skill Inference from Project"
```

### 3. Hypothesis Generation (`/hypothesize/`)

Ask the Oracle an open-ended question to generate hypotheses.

```bash
curl -X POST "http://127.0.0.1:8000/hypothesize/" \
-H "Content-Type: application/json" \
-d '{
  "question": "Why are there potential issues with Project X?"
}'
```
**Example Response:**
```json
{
  "hypotheses": [
    "Hypothesis: A path exists from 'Project X' -> -[DEPENDS_ON]-> 'API Y', where API Y has notable properties: {'name': 'API Y', 'status': 'deprecated'}.",
    "Hypothesis: A path exists from 'Project X' -> -[HAS_LEAD]-> 'Person A', where Person A has notable properties: {'name': 'Person A', 'stress_level': 'high'}."
  ]
}
```

### 4. GraphQL API (`/graphql`)

The GraphQL endpoint provides powerful querying capabilities, including retrieving the new metadata.

**Example Query:**
This query finds entities related to "Project Apollo" and retrieves the properties of the relationships.
```graphql
query {
  getRelatedEntities(name: "Project Apollo", label: "Project") {
    name
    labels
    relationship
    properties
  }
}
```

**Example Response:**
```json
{
  "data": {
    "getRelatedEntities": [
      {
        "name": "Anna",
        "labels": ["Person"],
        "relationship": "WORKS_ON",
        "properties": {
          "source": "project_log_123",
          "confidence_score": 0.95,
          "valid_from": "2023-01-15T09:00:00Z"
        }
      }
    ]
  }
}
```
