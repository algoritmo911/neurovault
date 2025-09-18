import unittest
import json
from neurovault.memory_module.api import app

class MemoryModuleApiTest(unittest.TestCase):

    def setUp(self):
        self.app = app.test_client()
        self.app.testing = True

    def test_save_memory(self):
        """Test saving a memory."""
        payload = {'memory_text': 'Test memory'}
        response = self.app.post('/save_memory',
                                 data=json.dumps(payload),
                                 content_type='application/json')
        self.assertEqual(response.status_code, 201)
        data = json.loads(response.get_data(as_text=True))
        self.assertEqual(data['message'], 'Memory saved successfully')
        self.assertIn('memory_id', data)

    def test_retrieve_memory(self):
        """Test retrieving a memory."""
        # First, save a memory to retrieve
        payload = {'memory_text': 'Another test memory'}
        response = self.app.post('/save_memory',
                                 data=json.dumps(payload),
                                 content_type='application/json')
        memory_id = json.loads(response.get_data(as_text=True))['memory_id']

        # Now, retrieve it
        response = self.app.get(f'/retrieve_memory/{memory_id}')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.get_data(as_text=True))
        self.assertEqual(data['memory_text'], 'Another test memory')
        self.assertEqual(data['memory_id'], memory_id)

    def test_retrieve_nonexistent_memory(self):
        """Test retrieving a memory that does not exist."""
        response = self.app.get('/retrieve_memory/999')
        self.assertEqual(response.status_code, 404)
        data = json.loads(response.get_data(as_text=True))
        self.assertEqual(data['error'], 'Memory not found')

    def test_save_memory_no_text(self):
        """Test saving a memory with no text."""
        payload = {}
        response = self.app.post('/save_memory',
                                 data=json.dumps(payload),
                                 content_type='application/json')
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.get_data(as_text=True))
        self.assertEqual(data['error'], 'Missing memory_text in request')

if __name__ == '__main__':
    unittest.main()
