import os
from whoosh.index import create_in, open_dir, exists_in
from whoosh.fields import Schema, TEXT, ID, STORED
from whoosh.qparser import QueryParser
from whoosh.highlight import UppercaseFormatter
from whoosh.index import EmptyIndexError


def get_schema():
    """Defines and returns the index schema."""
    return Schema(
        doc_id=ID(unique=True, stored=True),
        doc_name=STORED,
        doc_path=STORED,
        content=TEXT(stored=True),
    )


from config import settings

class Indexer:
    """
    Handles indexing of documents.

    Scalability Note: For very large document sets, this indexer could be extended
    to work with multiple sharded indexes. The `index_document` method would need
    a sharding strategy (e.g., hashing the doc_id) to decide which index shard
    to write to.
    """

    def __init__(self, index_dir=settings.INDEX_DIR):
        """
        Initializes the Indexer.

        :param index_dir: The directory where the index is stored.
        """
        self.index_dir = index_dir
        if not os.path.exists(self.index_dir):
            os.makedirs(self.index_dir)

        if exists_in(self.index_dir):
            self.ix = open_dir(self.index_dir)
        else:
            self.ix = create_in(self.index_dir, get_schema())

    def index_document(self, doc_id: str, doc_name: str, doc_path: str, content: str):
        """
        Adds or updates a document in the index.

        :param doc_id: A unique ID for the document.
        :param doc_name: The name of the document.
        :param doc_path: The path to the document.
        :param content: The text content of the document.
        """
        writer = self.ix.writer()
        writer.update_document(
            doc_id=doc_id,
            doc_name=doc_name,
            doc_path=doc_path,
            content=content,
        )
        writer.commit()

    def clear_index(self):
        """Removes all documents from the index."""
        self.ix = create_in(self.index_dir, get_schema()) # Re-create the index


class Searcher:
    """
    Handles searching the index.

    Scalability Note: To work with a sharded index, this class would need to be
    modified to open all index shards. The `search` method would then query each
    shard in parallel and aggregate the results before returning them.
    """

    def __init__(self, index_dir=settings.INDEX_DIR):
        """
        Initializes the Searcher.

        :param index_dir: The directory where the index is stored.
        """
        self.index_dir = index_dir
        try:
            self.ix = open_dir(self.index_dir)
        except EmptyIndexError:
            self.ix = None  # Index doesn't exist

    def search(self, query_str: str, limit: int = 10):
        """
        Searches the index for a given query string.

        :param query_str: The query string.
        :param limit: The maximum number of results to return.
        :return: A list of result dictionaries.
        """
        if not self.ix:
            return [] # Return empty list if index doesn't exist

        results_list = []
        with self.ix.searcher() as searcher:
            parser = QueryParser("content", self.ix.schema)
            query = parser.parse(query_str)
            results = searcher.search(query, limit=limit)

            # Use a custom formatter for highlighting
            results.formatter = UppercaseFormatter()

            for hit in results:
                results_list.append(
                    {
                        "doc_id": hit["doc_id"],
                        "doc_name": hit["doc_name"],
                        "doc_path": hit["doc_path"],
                        "score": hit.score,
                        "highlights": hit.highlights("content"),
                    }
                )
        return results_list
