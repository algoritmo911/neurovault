import os
import sys

# Add the project root to the Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from katana.gdrive.synchronizer import Synchronizer
from katana.parser.factory import parse_document
from katana.indexer.whoosh_indexer import Indexer
from katana.logging_config import get_logger

from config import settings

logger = get_logger(__name__)


def main():
    """
    Main function to run the indexing pipeline.

    Scalability Note: For a production environment, this script should be evolved
    into a more robust background task. Instead of being triggered by an API call
    that runs it in-process, it could be managed by a dedicated task queue system
    like Celery with RabbitMQ or Redis as a broker. This would provide better
    reliability, retry mechanisms, and decoupling from the API server.
    """
    if settings.GOOGLE_DRIVE_FOLDER_ID == "YOUR_GOOGLE_DRIVE_FOLDER_ID":
        logger.error("Please configure the GOOGLE_DRIVE_FOLDER_ID in config/settings.py or set the environment variable.")
        return

    # 1. Synchronize files from Google Drive
    synchronizer = Synchronizer(
        folder_id=settings.GOOGLE_DRIVE_FOLDER_ID,
    )
    # The sync method now returns the list of downloaded files
    files_to_index = synchronizer.sync()

    # 2. Initialize the indexer
    indexer = Indexer()

    # 3. Parse and index the downloaded files
    if not files_to_index:
        logger.info("No new or updated files to index.")
        return

    logger.info(f"Starting parsing and indexing for {len(files_to_index)} files...")
    for file_info in files_to_index:
        file_path = file_info["path"]
        doc_id = file_info["id"]
        filename = file_info["name"]

        if os.path.isfile(file_path):
            logger.info(f"Processing {file_path}...")
            content = parse_document(file_path)
            if content:
                indexer.index_document(
                    doc_id=doc_id,
                    doc_name=filename,
                    doc_path=file_path,
                    content=content,
                )
                logger.info(f"Indexed {filename}")
            else:
                logger.warning(f"Could not parse {filename}. Skipping.")
        else:
            logger.warning(f"Downloaded file not found at {file_path}. Skipping.")


    logger.info("Indexing complete.")


if __name__ == "__main__":
    main()
