import sys
import os
print("Current working directory:", os.getcwd())
print("PYTHONPATH:", os.environ.get("PYTHONPATH"))
print("sys.path:", sys.path)

print("\nAttempting to import...")
try:
    from services.ingestion_cortex.main import app
    print("\nSuccessfully imported 'app' from 'services.ingestion_cortex.main'")
except ImportError as e:
    print(f"\nFailed to import app with ImportError: {e}")
except Exception as e:
    print(f"\nFailed to import app with a general Exception: {e}")
