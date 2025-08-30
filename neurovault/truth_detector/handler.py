import logging
from .detector import TruthDetector

# Configure basic logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def process_data_item(item_id: str, data_item: dict):
    """
    Processes a single data item by analyzing it with the TruthDetector
    and logging the result. This function simulates being called by a
    worker from a queue.
    """
    logging.info(f"Processing item {item_id}...")

    # 1. Create an instance of the TruthDetector
    detector = TruthDetector()

    # 2. Call the analyze method with the data item
    result = detector.analyze(data_item)

    # 3. Log the result in the specified format
    classification = result.get("classification", "unknown")
    score = result.get("confidence_score", 0.0)

    log_message = (
        f"Элемент {item_id} классифицирован как {classification} "
        f"с уверенностью {score:.2f}"
    )
    logging.info(log_message)

    # For debugging, we can also log the full reasoning
    reasoning = result.get("reasoning", "No reasoning provided.")
    logging.debug(f"Reasoning for item {item_id}: {reasoning}")

if __name__ == '__main__':
    """
    Main execution block to test the handler function with sample data.
    """
    # This is the test data item as described in the task
    sample_data_item = {
        "source": "encyclopedia_britannica",
        "type": "text",
        "content": "The Battle of Hastings was fought on 14 October 1066 between the Norman-French army of William, Duke of Normandy, and an English army under the Anglo-Saxon King Harold Godwinson, beginning the Norman conquest of England.",
        "item_id": "HB-1066"
    }

    # The handler function is called with the test data
    process_data_item(item_id=sample_data_item["item_id"], data_item=sample_data_item)

    # --- Another example for 'fiction' ---
    sample_fiction_item = {
        "source": "story_book_adventures",
        "type": "text",
        "content": "The brave knight rode his trusty unicorn to the candy mountain to defeat the gingerbread dragon.",
        "item_id": "SB-A001"
    }
    # Here we can imagine the mocked LLM would return a different result.
    # To test this properly, we would need to adjust the mock in `detector.py`.
    # For now, it will still return 'fact', demonstrating the flow.
    # If we had a real LLM, the prompt would handle this.
    # process_data_item(item_id=sample_fiction_item["item_id"], data_item=sample_fiction_item)
