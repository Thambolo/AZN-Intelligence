#!/usr/bin/env python3
"""
Quick test to demonstrate the current program functionality.
"""

import sys
import os
import asyncio
import json

# Add server to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'server'))

from async_analyzer import AsyncUrlAnalyzer
from cache_manager import cache

async def quick_test():
    """Run a quick test of the accessibility analyzer."""
    print("🚀 Quick Test of Accessibility Analyzer")
    print("=" * 40)

    # Clear cache for clean test
    cache.clear()

    # Test URLs
    test_urls = [
        "https://www.example.com/",
        "https://www.google.com/"
    ]

    print(f"📊 Testing with {len(test_urls)} URLs")
    print(f"📂 Cache file: {cache.cache_file}")

    # Show initial cache stats
    stats = cache.get_stats()
    print(f"📈 Initial cache: {stats['total_entries']} entries")

    # Create analyzer
    analyzer = AsyncUrlAnalyzer(max_concurrent=2, batch_size=2)

    try:
        print("\n🔍 Running analysis...")
        start_time = asyncio.get_event_loop().time()

        # Analyze URLs
        results = await analyzer.analyze_urls_batch(test_urls)

        end_time = asyncio.get_event_loop().time()
        duration = end_time - start_time

        print(f"⏱️  Analysis completed in {duration:.2f}s")
        print(f"📊 Results: {len(results)} URLs analyzed")

        # Show results summary
        for result in results:
            url = result.get('url', 'Unknown')
            grade = result.get('grade', 'Unknown')
            score = result.get('score', 0)
            print(f"  • {url}: Grade {grade}, Score {score}")

        # Show final cache stats
        final_stats = cache.get_stats()
        print(f"\n📈 Final cache: {final_stats['total_entries']} entries")
        print(f"📂 Cache file size: {final_stats['total_size_bytes']} bytes")

        # Show cache file contents
        print("\n📋 Cache file contents:")
        try:
            with open(cache.cache_file, 'r') as f:
                cache_data = json.load(f)
                print(f"  Keys: {list(cache_data.keys())}")
        except Exception as e:
            print(f"  Error reading cache: {e}")

        print("\n✅ Test completed successfully!")

    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()

    finally:
        analyzer.cleanup()

if __name__ == "__main__":
    asyncio.run(quick_test())
