#!/usr/bin/env python3
"""
Simple test to verify server integration with persistent cache.
Tests the complete workflow: cache check -> analysis -> storage -> retrieval.
"""

import sys
import os
import json
from pathlib import Path

# Add server to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'server'))

from cache_manager import cache

def test_server_workflow():
    """Test the complete server workflow with persistent cache."""
    print("🧪 Testing server workflow with persistent cache...")

    # Clear cache for clean test
    cache.clear()

    # Simulate server audit request
    test_urls = [
        "https://www.example.com/",
        "https://www.wikipedia.org/",
        "https://www.github.com/"
    ]

    # Step 1: Check cache for existing results (should be empty)
    print("Step 1: Checking cache for existing results...")
    cached_results = []
    uncached_urls = []

    for url in test_urls:
        cached_result = cache.get(url)
        if cached_result:
            cached_results.append(cached_result)
        else:
            uncached_urls.append(url)

    assert len(cached_results) == 0, "Cache should be empty initially"
    assert len(uncached_urls) == 3, "All URLs should be uncached"
    print(f"✅ Found {len(cached_results)} cached, {len(uncached_urls)} uncached URLs")

    # Step 2: Simulate analysis results (normally from agent)
    print("Step 2: Simulating analysis results...")
    mock_results = [
        {
            "url": "https://www.example.com/",
            "grade": "AA",
            "score": 95,
            "issues": [],
            "agent_response": "Mock analysis for example.com"
        },
        {
            "url": "https://www.wikipedia.org/",
            "grade": "AAA",
            "score": 98,
            "issues": [],
            "agent_response": "Mock analysis for wikipedia.org"
        },
        {
            "url": "https://www.github.com/",
            "grade": "AA",
            "score": 92,
            "issues": [{"component": "Test", "message": "Mock issue", "passed": 1, "total": 1}],
            "agent_response": "Mock analysis for github.com"
        }
    ]

    # Step 3: Store results in cache
    print("Step 3: Storing results in cache...")
    for result in mock_results:
        cache.set(result['url'], result)

    # Step 4: Verify cache storage
    print("Step 4: Verifying cache storage...")
    stats = cache.get_stats()
    assert stats['total_entries'] == 3, f"Expected 3 entries, got {stats['total_entries']}"
    print(f"✅ Cache now contains {stats['total_entries']} entries")

    # Step 5: Test cache retrieval
    print("Step 5: Testing cache retrieval...")
    for url in test_urls:
        cached = cache.get(url)
        assert cached is not None, f"URL {url} should be cached"
        assert cached['url'] == url, f"URL mismatch for {url}"
        print(f"✅ Retrieved cached result for {url}: Grade {cached['grade']}, Score {cached['score']}")

    # Step 6: Test cache persistence across instances
    print("Step 6: Testing persistence across instances...")
    from cache_manager import PersistentCache
    new_cache = PersistentCache()

    for url in test_urls:
        cached = new_cache.get(url)
        assert cached is not None, f"URL {url} should persist across instances"
        assert cached['grade'] in ['AA', 'AAA'], f"Grade should be valid for {url}"

    print("✅ Persistence test passed!")

    # Step 7: Verify JSON file structure
    print("Step 7: Verifying JSON file structure...")
    cache_file = Path("cache/accessibility_cache.json")
    assert cache_file.exists(), "Cache file should exist"

    with open(cache_file, 'r') as f:
        file_data = json.load(f)

    assert isinstance(file_data, dict), "Cache file should contain a dictionary"
    assert len(file_data) == 3, "Should have 3 entries in file"

    for url, data in file_data.items():
        assert 'timestamp' in data, f"Entry {url} should have timestamp"
        assert 'last_accessed' in data, f"Entry {url} should have last_accessed"
        assert 'url' in data, f"Entry {url} should have url"
        assert 'grade' in data, f"Entry {url} should have grade"
        assert 'score' in data, f"Entry {url} should have score"

    print("✅ JSON file structure is valid!")

    print("\n🎉 Server workflow test completed successfully!")
    print(f"📊 Final cache stats: {cache.get_stats()}")

    return True

if __name__ == "__main__":
    try:
        success = test_server_workflow()
        if success:
            print("\n✅ All server integration tests passed!")
            print("The persistent cache is working correctly with the server workflow.")
        else:
            print("\n❌ Server integration tests failed!")
            sys.exit(1)
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
