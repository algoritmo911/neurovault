import sys
import os
from fastapi import FastAPI, BackgroundTasks, HTTPException, Query
from pydantic import BaseModel
from typing import List, Optional

# Add the project root to the Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from katana.indexer.whoosh_indexer import Searcher
from scripts.run_indexing import main as run_indexing_main
from katana.logging_config import get_logger

logger = get_logger(__name__)

app = FastAPI(
    title="Katana AI - Document Search API",
    description="API for searching and indexing documents from Google Drive.",
    version="1.0.0",
)

# --- Models ---

class SearchResult(BaseModel):
    doc_id: str
    doc_name: str
    doc_path: str
    score: float
    highlights: str

class SearchResponse(BaseModel):
    results: List[SearchResult]

class IndexResponse(BaseModel):
    message: str

# --- Helper Functions ---

def run_indexing_task():
    """Wrapper function to run the indexing script."""
    logger.info("Starting background indexing task...")
    try:
        run_indexing_main()
        logger.info("Background indexing task finished.")
    except Exception as e:
        logger.error(f"Error during background indexing: {e}")

# --- API Endpoints ---

@app.post("/index", response_model=IndexResponse, summary="Trigger Document Indexing")
async def trigger_indexing(background_tasks: BackgroundTasks):
    """
    Triggers the process of synchronizing documents from Google Drive,
    parsing them, and updating the search index.
    This is an asynchronous operation that runs in the background.
    """
    background_tasks.add_task(run_indexing_task)
    return {"message": "Indexing process started in the background."}


@app.get("/search", response_model=SearchResponse, summary="Search for Documents")
async def search_documents(
    q: str = Query(..., min_length=3, description="The search query string."),
    limit: int = Query(10, gt=0, le=100, description="The maximum number of results to return.")
):
    """
    Searches the indexed documents for a given query string.
    Returns a list of matching documents with highlighted snippets.
    """
    # Scalability/Optimization Note:
    # For high-traffic applications, a caching layer (e.g., Redis) could be
    # implemented here. Before hitting the searcher, check if the results for
    # the query `q` are already in the cache. If so, return the cached results.
    # Otherwise, perform the search and store the results in the cache before returning.
    try:
        searcher = Searcher()
        results = searcher.search(q, limit=limit)
        return {"results": results}
    except Exception as e:
        # This can happen if the index does not exist yet.
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/", include_in_schema=False)
async def root():
    return {"message": "Welcome to the Katana AI Document Search API. See /docs for documentation."}
