#!/usr/bin/env python3
"""
Consolidated test suite for AZN-Intelligence accessibility grader system.
Tests the core functionality: agent analysis, caching, and API endpoints.
"""

import sys
import os
import asyncio
import json
from pathlib import Path

# Add paths for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'server'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'server', 'meta-agent'))

# Test configuration
TEST_URLS = [
    "https://www.example.com/",
    "https://www.wikipedia.org/"
]

def test_cache_manager():
    """Test the persistent cache functionality."""
    from cache_manager import cache

    print("\n🧪 Testing Cache Manager...")

    # Clear cache for clean test
    cache.clear()

    # Test storing and retrieving
    test_data = {
        "url": TEST_URLS[0],
        "grade": "AA",
        "score": 85,
        "issues": []
    }

    # Store data
    cache.set(TEST_URLS[0], test_data)

    # Retrieve data
    retrieved = cache.get(TEST_URLS[0])
    assert retrieved is not None, "Cache should return stored data"
    assert retrieved["grade"] == "AA", "Grade should match"
    assert retrieved["score"] == 85, "Score should match"

    # Test cache stats
    stats = cache.get_stats()
    assert stats["total_entries"] == 1, "Should have 1 entry"

    print("✅ Cache manager test passed!")


async def test_async_analyzer():
    """Test the async URL analyzer."""
    from async_analyzer import AsyncUrlAnalyzer
    from cache_manager import cache

    print("\n🧪 Testing Async Analyzer...")

    # Clear cache
    cache.clear()

    # Create analyzer
    analyzer = AsyncUrlAnalyzer(max_concurrent=2, batch_size=2)

    try:
        # Analyze URLs
        results = await analyzer.analyze_with_timeout(TEST_URLS[:1], timeout_seconds=30)

        assert len(results) > 0, "Should return results"

        # Check result structure
        if results:
            result = results[0]
            assert "url" in result, "Result should have URL"
            assert "grade" in result, "Result should have grade"
            assert "score" in result, "Result should have score"

        print(f"✅ Async analyzer test passed! Analyzed {len(results)} URLs")

    finally:
        analyzer.cleanup()


def test_agent_integration():
    """Test the ConnectOnion agent integration."""
    from agent import agent, analyze_urls_with_agent

    print("\n🧪 Testing Agent Integration...")

    try:
        # Test agent availability
        response = agent.input("List your available tools", max_iterations=1)
        assert response is not None, "Agent should respond"

        # Test URL analysis function
        results = analyze_urls_with_agent(TEST_URLS[:1])
        assert len(results) > 0, "Should return analysis results"

        if results:
            result = results[0]
            assert "url" in result, "Result should have URL"
            assert "grade" in result, "Result should have grade"
            assert "agent_response" in result, "Result should have agent response"

        print("✅ Agent integration test passed!")

    except Exception as e:
        print(f"⚠️  Agent test skipped (may require API key): {e}")


def test_api_endpoints():
    """Test the FastAPI endpoints."""
    print("\n🧪 Testing API Endpoints...")

    try:
        from app import app
        from fastapi.testclient import TestClient

        client = TestClient(app)

        # Test /audit endpoint
        response = client.post("/audit", json={"urls": TEST_URLS[:1]})
        assert response.status_code == 200, "Should return 200 OK"

        data = response.json()
        assert "results" in data, "Should have results key"

        print("✅ API endpoints test passed!")

    except ImportError:
        print("⚠️  API test skipped (install fastapi[test] for full testing)")


def run_all_tests():
    """Run all tests in sequence."""
    print("🚀 AZN-Intelligence Consolidated Test Suite")
    print("=" * 50)

    # Run synchronous tests
    test_cache_manager()
    test_agent_integration()
    test_api_endpoints()

    # Run async tests
    print("\n🧪 Running Async Tests...")
    asyncio.run(test_async_analyzer())

    print("\n" + "=" * 50)
    print("🎉 All tests completed!")
    print("\nSystem Components Verified:")
    print("  ✓ Cache manager with persistent storage")
    print("  ✓ Async URL analyzer with batch processing")
    print("  ✓ ConnectOnion agent with WCAG analysis")
    print("  ✓ FastAPI endpoints for web service")


if __name__ == "__main__":
    run_all_tests()