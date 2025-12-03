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
    async def get_input():
        return {
            "url": "https://example.com",
            "maxActions": 10,
            "removeBanners": True
        }
    
    @staticmethod
    async def push_data(data):
        MockActor.data_store.append(data)
        print(f"✅ DATA PUSHED: {json.dumps(data, indent=2)}")
    
    @staticmethod
    async def open_key_value_store():
        class MockKVStore:
            store_id = "test-store-id"
            
            @staticmethod
            async def set_value(key, value, content_type=None):
                MockActor.kv_store[key] = value
                print(f"✅ KV STORE: Saved {key}")
        
        return MockKVStore()
    
    # Mock context manager
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        return False
    
    async def __aenter__(self):
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        return False

# Monkey patch
import src.main
src.main.Actor = MockActor()

if __name__ == "__main__":
    import asyncio
    
    async def run_test():
        print("🚀 Starting mock actor...")
        async with MockActor():
            await main()
        print(f"\n📊 RESULTS:")
        print(f"  - Data entries pushed: {len(MockActor.data_store)}")
        print(f"  - KV store entries: {len(MockActor.kv_store)}")
        print(f"\n{'='*50}")
        if MockActor.data_store:
            print("✅ SUCCESS: Actor pushed data to dataset!")
        else:
            print("❌ FAIL: No data pushed to dataset")
        print('='*50)
    
    asyncio.run(run_test())

