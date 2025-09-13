#!/usr/bin/env python3
"""
Test the synchronous wrapper function separately.
"""

import sys
import os
import time

# Add server to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'server'))

from async_analyzer import analyze_urls_optimized
from cache_manager import cache

def test_sync_wrapper():
    """Test the synchronous wrapper function."""
    print("🧪 Testing synchronous wrapper...")

    # Clear cache
    cache.clear()

    test_urls = [
        "https://www.sync1.com/",
        "https://www.sync2.com/",
        "https://www.sync3.com/"
    ]

    start_time = time.time()
    results = analyze_urls_optimized(test_urls, max_concurrent=2, batch_size=2)
    end_time = time.time()

    assert len(results) == 3, f"Expected 3 results, got {len(results)}"
    print(f"✅ Synchronous wrapper: {end_time - start_time:.2f}s")
    print("✅ Synchronous wrapper test passed!")

    print("\n📊 Cache Stats:")
    stats = cache.get_stats()
    for key, value in stats.items():
        print(f"  {key}: {value}")

if __name__ == "__main__":
    test_sync_wrapper()
