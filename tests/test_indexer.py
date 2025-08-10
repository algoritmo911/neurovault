import unittest
import os
import shutil
import tempfile

# Add project root to path to allow absolute imports
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from katana.indexer.whoosh_indexer import Indexer, Searcher, get_schema
from whoosh.index import open_dir

class TestIndexerAndSearcher(unittest.TestCase):

    def setUp(self):
        """Set up a temporary directory for the index."""
        self.index_dir = tempfile.mkdtemp()
        self.indexer = Indexer(index_dir=self.index_dir)
        self.searcher = Searcher(index_dir=self.index_dir)

    def tearDown(self):
        """Remove the temporary directory after tests."""
        shutil.rmtree(self.index_dir)

    def test_01_index_creation(self):
        """Test that the indexer creates the index directory."""
        self.assertTrue(os.path.exists(self.index_dir))

    def test_02_index_document(self):
        """Test adding a single document to the index."""
        self.indexer.index_document(
            doc_id="doc1",
            doc_name="test_document.txt",
            doc_path="/path/to/test_document.txt",
            content="The quick brown fox jumps over the lazy dog."
        )

        # Verify directly with a whoosh searcher
        ix = open_dir(self.index_dir)
        with ix.searcher() as s:
            results = list(s.documents())
            self.assertEqual(len(results), 1)
            self.assertEqual(results[0]['doc_id'], 'doc1')
            self.assertEqual(results[0]['content'], 'The quick brown fox jumps over the lazy dog.')

    def test_03_search_document(self):
        """Test searching for an indexed document."""
        self.indexer.index_document(
            doc_id="doc1",
            doc_name="test_document.txt",
            doc_path="/path/to/test_document.txt",
            content="The quick brown fox jumps over the lazy dog."
        )

        results = self.searcher.search("fox")
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]['doc_id'], 'doc1')
        self.assertIn("FOX", results[0]['highlights'])

    def test_04_search_no_results(self):
        """Test a search query that should yield no results."""
        self.indexer.index_document(
            doc_id="doc1",
            doc_name="test_document.txt",
            doc_path="/path/to/test_document.txt",
            content="The quick brown fox jumps over the lazy dog."
        )

        results = self.searcher.search("wolf")
        self.assertEqual(len(results), 0)

    def test_05_update_document(self):
        """Test updating an existing document in the index."""
        # First, index the document
        self.indexer.index_document(
            doc_id="doc1",
            doc_name="test_document.txt",
            doc_path="/path/to/test_document.txt",
            content="Old content."
        )

        # Now, update it
        self.indexer.index_document(
            doc_id="doc1",
            doc_name="test_document_renamed.txt",
            doc_path="/path/to/test_document_renamed.txt",
            content="New updated content."
        )

        ix = open_dir(self.index_dir)
        with ix.searcher() as s:
            results = list(s.documents())
            self.assertEqual(len(results), 1) # Should still be one document
            self.assertEqual(results[0]['doc_id'], 'doc1')
            self.assertEqual(results[0]['content'], 'New updated content.')
            self.assertEqual(results[0]['doc_name'], 'test_document_renamed.txt')

    def test_06_clear_index(self):
        """Test clearing the index."""
        self.indexer.index_document(doc_id="doc1", doc_name="doc1.txt", doc_path="/doc1", content="some content")
        self.indexer.index_document(doc_id="doc2", doc_name="doc2.txt", doc_path="/doc2", content="more content")

        # Clear the index
        self.indexer.clear_index()

        ix = open_dir(self.index_dir)
        with ix.searcher() as s:
            results = list(s.documents())
            self.assertEqual(len(results), 0)


if __name__ == '__main__':
    unittest.main()
