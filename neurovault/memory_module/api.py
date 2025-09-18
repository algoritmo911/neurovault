from flask import Flask, request, jsonify

app = Flask(__name__)

# In-memory database for storing memories
memories_db = {}
memory_id_counter = 0

@app.route('/save_memory', methods=['POST'])
def save_memory():
    """
    Saves a memory to the database.
    Expects a JSON payload with a 'memory_text' field.
    """
    global memory_id_counter
    data = request.get_json()
    if not data or 'memory_text' not in data:
        return jsonify({'error': 'Missing memory_text in request'}), 400

    memory_text = data['memory_text']
    memory_id = memory_id_counter
    memories_db[memory_id] = memory_text
    memory_id_counter += 1

    return jsonify({'message': 'Memory saved successfully', 'memory_id': memory_id}), 201

@app.route('/retrieve_memory/<int:memory_id>', methods=['GET'])
def retrieve_memory(memory_id):
    """
    Retrieves a memory from the database by its ID.
    """
    if memory_id not in memories_db:
        return jsonify({'error': 'Memory not found'}), 404

    memory_text = memories_db[memory_id]
    return jsonify({'memory_id': memory_id, 'memory_text': memory_text}), 200

if __name__ == '__main__':
    app.run(debug=True, port=5000)
