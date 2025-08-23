from .graph_db import GraphDB
from .nlp import NLPProcessor
from .inquisitor import Inquisitor

def process_text_input(text: str, source: str = "text_input", properties: dict = None):
    """
    Processes raw text, extracts entities and concepts, and stores them in the graph.

    Args:
        text (str): The raw text to process.
        source (str): The source of the information (e.g., "sapiens_note", "katana_log").
        properties (dict, optional): A dictionary of properties for the relationships.
    """
    db = GraphDB()
    inquisitor = Inquisitor(db)
    nlp = NLPProcessor()
    properties = properties or {}
    properties['source'] = source  # Ensure the source is always in the properties

    # --- Inquisitor Check ---
    # In a real system, a more sophisticated pre-processing step would
    # extract structured facts. For now, we simulate this by checking
    # for a special 'fact' key in the properties.
    if 'fact' in properties and len(properties['fact']) == 3:
        subj, pred, obj = properties['fact']
        # For simplicity, we assume the labels are the same as the variable names capitalized.
        # e.g., 'person' -> 'Person'
        subj_label = subj.capitalize()
        obj_label = obj.capitalize()

        contradiction = inquisitor.check_for_contradictions(subj, subj_label, pred, obj)
        if contradiction:
            print(f"Ingestion halted due to contradiction: {contradiction}")
            return # Halt processing

    try:
        # Extract entities and concepts
        entities = nlp.extract_entities(text)
        concepts = nlp.extract_concepts(text)

        # Add a source node to the graph
        db.add_entity(source, "Source")

        # Add entities to the graph and link them to the source
        for entity_text, entity_label in entities:
            db.add_entity(entity_text, entity_label)
            db.add_relationship(entity_text, entity_label, source, "Source", "MENTIONED_IN", properties=properties)

        # Add concepts to the graph and link them to the source
        for concept_text in concepts:
            db.add_entity(concept_text, "Concept")
            db.add_relationship(concept_text, "Concept", source, "Source", "CONTAINS", properties=properties)

        print(f"Processed text from source '{source}' and updated the graph with properties: {properties}")

    finally:
        db.close()

def sapiens_notes_connector():
    """
    Mock connector for sapiens_notes_private database.
    In a real implementation, this would fetch new notes from the database.
    """
    print("Checking for new notes in sapiens_notes_private...")
    # Simulate fetching a new note
    new_note = {
        "id": "note_123",
        "content": "I had a meeting with Elon Musk to discuss the future of AI and space exploration.",
        "source": "sapiens_note"
    }
    process_text_input(new_note["content"], source=new_note["source"])

def katana_memory_connector():
    """
    Mock connector for Katana's operational memory.
    In a real implementation, this would monitor successful commands and dialogs.
    """
    print("Monitoring Katana's operational memory...")
    # Simulate a successful command log
    katana_log = {
        "command": "trade",
        "params": {"pair": "BTC-USD", "amount": 1.5},
        "result": "success",
        "source": "katana_log"
    }
    log_text = f"Successful trade of {katana_log['params']['amount']} {katana_log['params']['pair']}"
    process_text_input(log_text, source=katana_log["source"])

# Example usage (for testing purposes)
if __name__ == "__main__":
    # Process a sample text input
    sample_text = "The quick brown fox jumps over the lazy dog."
    process_text_input(sample_text)

    # Run the mock connectors
    sapiens_notes_connector()
    katana_memory_connector()
