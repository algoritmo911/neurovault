import sqlite3
import json
import os

DB_FILE = "deep_analysis_archive.db"

def get_db_connection():
    """Establishes a connection to the SQLite database."""
    # This function is now only for creating a connection to the main DB file.
    os.makedirs(os.path.dirname(DB_FILE), exist_ok=True)
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    return conn

def initialize_database(conn):
    """Initializes the database table on the given connection."""
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS deep_analysis_queue (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            item_data TEXT NOT NULL,
            status TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()

def add_item_to_queue(conn, item: dict):
    """Adds a new item to the queue using the provided database connection."""
    cursor = conn.cursor()
    item_data_str = json.dumps(item)
    cursor.execute(
        "INSERT INTO deep_analysis_queue (item_data, status) VALUES (?, ?)",
        (item_data_str, "pending_analysis")
    )
    conn.commit()
    return cursor.lastrowid