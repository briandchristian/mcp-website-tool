"""
Test script to run the actor locally with simulated Apify environment.
This simulates what Apify CLI does for local testing.
"""
import json
import os
import sys
from pathlib import Path

# Set up Apify environment variables for local testing
os.environ["APIFY_LOCAL_STORAGE_DIR"] = str(Path.cwd() / "storage")
os.environ["APIFY_DEFAULT_KEY_VALUE_STORE_ID"] = "default"
os.environ["APIFY_DEFAULT_DATASET_ID"] = "default"
os.environ["APIFY_DEFAULT_REQUEST_QUEUE_ID"] = "default"

# Load test input
input_file = Path("test-input.json")
if input_file.exists():
    with open(input_file, "r") as f:
        input_data = json.load(f)
    # Save to expected location for Actor.get_input()
    storage_dir = Path("storage") / "key_value_stores" / "default"
    storage_dir.mkdir(parents=True, exist_ok=True)
    input_path = storage_dir / "INPUT.json"
    with open(input_path, "w") as f:
        json.dump(input_data, f)
    print(f"[OK] Loaded input from {input_file}")
    print(f"  Input: {json.dumps(input_data, indent=2)}")
else:
    print(f"[ERROR] Input file {input_file} not found")
    sys.exit(1)

# Mock all Actor methods needed for local testing
from unittest.mock import MagicMock, patch
import apify

# Create a mock key-value store
mock_key_value_store = MagicMock()
mock_key_value_store.store_id = "test-store-id"
mock_key_value_store.set_value = MagicMock()

# Create a mock dataset (for push_data)
mock_dataset = MagicMock()
mock_dataset.push_items = MagicMock()

# Mock all Actor methods before importing main
apify.Actor.get_input = MagicMock(return_value=input_data)
apify.Actor.open_key_value_store = MagicMock(return_value=mock_key_value_store)
apify.Actor.push_data = MagicMock()  # push_data is a simple function call
apify.Actor.open_dataset = MagicMock(return_value=mock_dataset)

# Import and run the main function
print("\n[START] Starting Actor...\n")
try:
    from src.main import main
    main()
    print("\n[OK] Actor completed successfully!")
    print(f"\n[INFO] Key-value store operations: {mock_key_value_store.set_value.call_count} calls")
    print(f"[INFO] Dataset push operations: {apify.Actor.push_data.call_count} calls")
except Exception as e:
    print(f"\n[ERROR] Actor failed: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

