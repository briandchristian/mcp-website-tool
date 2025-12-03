"""
Quick local test to verify the actor works before deploying to Apify.
"""

import json
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

from src.main import main

# Mock Actor class for local testing
class MockActor:
    data_store = []
    kv_store = {}
    
    @staticmethod
    def get_input():
        return {
            "url": "https://example.com",
            "maxActions": 10,
            "removeBanners": True
        }
    
    @staticmethod
    def push_data(data):
        MockActor.data_store.append(data)
        print(f"✅ DATA PUSHED: {json.dumps(data, indent=2)}")
    
    @staticmethod
    def open_key_value_store():
        class MockKVStore:
            store_id = "test-store-id"
            
            @staticmethod
            def set_value(key, value, content_type=None):
                MockActor.kv_store[key] = value
                print(f"✅ KV STORE: Saved {key}")
        
        return MockKVStore()
    
    @staticmethod
    def start(func):
        print("🚀 Starting mock actor...")
        func()
        print(f"\n📊 RESULTS:")
        print(f"  - Data entries pushed: {len(MockActor.data_store)}")
        print(f"  - KV store entries: {len(MockActor.kv_store)}")
        print(f"\n{'='*50}")
        if MockActor.data_store:
            print("✅ SUCCESS: Actor pushed data to dataset!")
        else:
            print("❌ FAIL: No data pushed to dataset")
        print('='*50)

# Monkey patch
import src.main
src.main.Actor = MockActor

if __name__ == "__main__":
    import src.main
    src.main.Actor.start(main)

