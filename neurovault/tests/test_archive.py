import unittest
import sqlite3
import json
from neurovault.deep_analysis.archive import initialize_database, add_item_to_queue

class TestArchive(unittest.TestCase):

    def setUp(self):
        """Set up a single, shared in-memory database connection for the test."""
        self.conn = sqlite3.connect(":memory:")
        self.conn.row_factory = sqlite3.Row
        initialize_database(self.conn)

    def tearDown(self):
        """Close the database connection."""
        self.conn.close()

    def test_add_item_to_queue(self):
        """Test that an item can be successfully added to the queue."""
        test_item = {"original_data": {"id": "999"}, "analysis": {"classification": "unverifiable"}}

        # Pass the connection to the function
        item_id = add_item_to_queue(self.conn, test_item)
        self.assertIsNotNone(item_id)

        # Verify directly against the shared connection
        cursor = self.conn.cursor()
        cursor.execute("SELECT item_data, status FROM deep_analysis_queue WHERE id = ?", (item_id,))
        row = cursor.fetchone()

        self.assertIsNotNone(row)
        self.assertEqual(json.loads(row["item_data"]), test_item)
        self.assertEqual(row["status"], "pending_analysis")

if __name__ == "__main__":
    unittest.main()