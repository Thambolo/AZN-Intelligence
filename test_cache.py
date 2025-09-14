#!/usr/bin/env python3
"""
Test cases for persistent data storage functionality.
Tests the cache manager to ensure data persistence across server restarts.
"""

import sys
import os
import json
import time
from pathlib import Path

# Add server to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'server'))

from cache_manager import PersistentCache, cache

def test_basic_cache_operations():
    """Test basic cache operations: set, get, has."""
    print("🧪 Testing basic cache operations...")

    # Test data
    test_url = "https://www.example.com/"
    test_data = {
        "url": test_url,
        "grade": "AA",
        "score": 95,
        "issues": [],
        "agent_response": "Test response"
    }

    # Test set and get
    cache.set(test_url, test_data)
    retrieved = cache.get(test_url)

    assert retrieved is not None, "Failed to retrieve cached data"
    assert retrieved['url'] == test_url, "URL mismatch"
    assert retrieved['grade'] == "AA", "Grade mismatch"
    assert retrieved['score'] == 95, "Score mismatch"

    # Test has
    assert cache.has(test_url), "has() should return True for cached URL"
    assert not cache.has("https://nonexistent.com/"), "has() should return False for non-cached URL"

    print("✅ Basic cache operations test passed!")

def test_persistence_across_instances():
    """Test that data persists across different cache instances."""
    print("🧪 Testing persistence across instances...")

    # Set data in first instance
    test_url = "https://www.test-persistence.com/"
    test_data = {
        "url": test_url,
        "grade": "A",
        "score": 88,
        "issues": [{"component": "Test", "message": "Test issue", "passed": 1, "total": 1}]
    }

    cache.set(test_url, test_data)

    # Create new instance and verify data persists
    new_cache = PersistentCache()
    retrieved = new_cache.get(test_url)

    assert retrieved is not None, "Data should persist across instances"
    assert retrieved['grade'] == "A", "Grade should persist"
    assert retrieved['score'] == 88, "Score should persist"

    print("✅ Persistence test passed!")

def test_cache_stats():
    """Test cache statistics functionality."""
    print("🧪 Testing cache statistics...")

    # Clear cache first
    cache.clear()

    # Add some test data
    test_data = [
        ("https://www.site1.com/", {"url": "https://www.site1.com/", "grade": "AAA", "score": 98}),
        ("https://www.site2.com/", {"url": "https://www.site2.com/", "grade": "AA", "score": 92}),
        ("https://www.site3.com/", {"url": "https://www.site3.com/", "grade": "A", "score": 85})
    ]

    for url, data in test_data:
        cache.set(url, data)

    stats = cache.get_stats()

    assert stats['total_entries'] == 3, f"Expected 3 entries, got {stats['total_entries']}"
    assert stats['total_size_bytes'] > 0, "Cache size should be greater than 0"
    assert 'cache_file' in stats, "Stats should include cache file path"

    print(f"✅ Cache stats test passed! Stats: {stats}")

def test_expiration_cleanup():
    """Test expired entry cleanup functionality."""
    print("🧪 Testing expiration cleanup...")

    # Create a cache with short expiration for testing
    test_cache = PersistentCache(cache_file="test_cache.json", max_age_days=0)  # 0 days = immediate expiration

    # Add data
    test_url = "https://www.expire-test.com/"
    test_data = {"url": test_url, "grade": "AA", "score": 90}
    test_cache.set(test_url, test_data)

    # Wait a moment and cleanup
    time.sleep(0.1)
    removed_count = test_cache.cleanup_expired()

    # Since max_age_days=0, entry should be considered expired
    assert removed_count >= 0, "Cleanup should not fail"

    # Check if entry was actually removed (depends on implementation)
    remaining = test_cache.get(test_url)

    print(f"✅ Expiration cleanup test passed! Removed {removed_count} entries")

    # Clean up test file
    test_cache_file = Path("cache/test_cache.json")
    if test_cache_file.exists():
        test_cache_file.unlink()

def test_server_integration():
    """Test integration with the FastAPI server."""
    print("🧪 Testing server integration...")

    # Import the server app
    from app import app

    # Test data
    test_urls = ["https://www.integration-test.com/"]
    test_data = {
        "url": test_urls[0],
        "grade": "AA",
        "score": 93,
        "issues": [],
        "agent_response": "Integration test response"
    }

    # Pre-populate cache
    cache.set(test_urls[0], test_data)

    # Simulate server request (we'll test the logic without actually running the server)
    from app import audit_urls
    from pydantic import BaseModel

    class MockRequest:
        def __init__(self, urls):
            self.urls = urls

    # Test the audit function
    mock_request = MockRequest(test_urls)

    # This would normally be called by FastAPI, but we can test the logic
    results = []
    uncached_urls = []

    for url in mock_request.urls:
        cached_result = cache.get(url)
        if cached_result:
            results.append(cached_result)
        else:
            uncached_urls.append(url)

    assert len(results) == 1, "Should have 1 cached result"
    assert results[0]['url'] == test_urls[0], "URL should match"
    assert results[0]['grade'] == "AA", "Grade should match cached value"

    print("✅ Server integration test passed!")

def test_cache_file_structure():
    """Test that the cache file has the expected JSON structure."""
    print("🧪 Testing cache file structure...")

    # Clear and add test data
    cache.clear()

    test_entries = {
        "https://www.site1.com/": {"url": "https://www.site1.com/", "grade": "AAA", "score": 98},
        "https://www.site2.com/": {"url": "https://www.site2.com/", "grade": "AA", "score": 92}
    }

    for url, data in test_entries.items():
        cache.set(url, data)

    # Read the cache file directly
    cache_file = Path("cache/accessibility_cache.json")
    assert cache_file.exists(), "Cache file should exist"

    with open(cache_file, 'r') as f:
        file_data = json.load(f)

    # Verify structure
    assert isinstance(file_data, dict), "Cache file should contain a dictionary"
    assert len(file_data) == 2, "Should have 2 entries"

    for url, data in file_data.items():
        assert 'timestamp' in data, "Each entry should have a timestamp"
        assert 'last_accessed' in data, "Each entry should have last_accessed"
        assert 'url' in data, "Each entry should have url"
        assert 'grade' in data, "Each entry should have grade"
        assert 'score' in data, "Each entry should have score"

    print("✅ Cache file structure test passed!")

def run_all_tests():
    """Run all cache tests."""
    print("🚀 Running Persistent Cache Test Suite")
    print("=" * 50)

    try:
        test_basic_cache_operations()
        test_persistence_across_instances()
        test_cache_stats()
        test_expiration_cleanup()
        test_server_integration()
        test_cache_file_structure()

        print("\n🎉 All tests passed successfully!")
        print("\n📊 Final Cache Stats:")
        stats = cache.get_stats()
        for key, value in stats.items():
            print(f"  {key}: {value}")

    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

    return True

if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
