import unittest
from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient

import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from katana.api import app

class TestApi(unittest.TestCase):

    def setUp(self):
        self.client = TestClient(app)

    @patch('katana.api.Searcher')
    def test_search_success(self, MockSearcher):
        """Test the /search endpoint with a successful query."""
        # Mock the searcher to return some results
        mock_searcher_instance = MockSearcher.return_value
        mock_results = [
            {
                "doc_id": "doc1", "doc_name": "test.txt", "doc_path": "/path/test.txt",
                "score": 1.23, "highlights": "This is a <B>test</B>"
            }
        ]
        mock_searcher_instance.search.return_value = mock_results

        response = self.client.get("/search?q=test")

        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("results", data)
        self.assertEqual(len(data["results"]), 1)
        self.assertEqual(data["results"][0]["doc_id"], "doc1")
        mock_searcher_instance.search.assert_called_once_with("test", limit=10)

    def test_search_query_too_short(self):
        """Test the /search endpoint with a query that is too short."""
        response = self.client.get("/search?q=ab")
        self.assertEqual(response.status_code, 422) # Unprocessable Entity for validation errors

    @patch('katana.api.Searcher')
    def test_search_limit_parameter(self, MockSearcher):
        """Test the /search endpoint with the limit parameter."""
        mock_searcher_instance = MockSearcher.return_value
        mock_searcher_instance.search.return_value = []

        self.client.get("/search?q=test&limit=50")
        mock_searcher_instance.search.assert_called_once_with("test", limit=50)

    @patch('katana.api.run_indexing_task')
    def test_index_endpoint(self, mock_run_indexing_task):
        """Test the /index endpoint."""
        # The TestClient runs background tasks immediately.
        response = self.client.post("/index")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"message": "Indexing process started in the background."})
        mock_run_indexing_task.assert_called_once()

    @patch('katana.api.Searcher')
    def test_search_handles_exception(self, MockSearcher):
        """Test that the /search endpoint handles exceptions from the Searcher."""
        mock_searcher_instance = MockSearcher.return_value
        mock_searcher_instance.search.side_effect = Exception("Whoosh is broken")

        response = self.client.get("/search?q=anything")

        self.assertEqual(response.status_code, 500)
        self.assertEqual(response.json(), {"detail": "Whoosh is broken"})


if __name__ == '__main__':
    unittest.main()
