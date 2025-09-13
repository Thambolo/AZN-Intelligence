"""
Asynchronous URL analysis handler for improved performance.
Handles multiple URLs concurrently and provides progressive updates.
"""

import asyncio
import sys
import os
from typing import List, Dict, Optional
from concurrent.futures import ThreadPoolExecutor
import time

# Add meta-agent to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'meta-agent'))

from agent import analyze_urls_with_agent
from cache_manager import cache

class AsyncUrlAnalyzer:
    """Handles asynchronous URL analysis with progressive updates."""

    def __init__(self, max_concurrent: int = 3, batch_size: int = 5):
        self.max_concurrent = max_concurrent
        self.batch_size = batch_size
        self.executor = ThreadPoolExecutor(max_workers=max_concurrent)

    async def analyze_urls_batch(self, urls: List[str], progress_callback=None) -> List[Dict]:
        """
        Analyze URLs in batches with concurrent processing.

        Args:
            urls: List of URLs to analyze
            progress_callback: Optional callback function for progress updates

        Returns:
            List of analysis results
        """
        results = []
        total_urls = len(urls)

        # Check cache first
        cached_results = []
        uncached_urls = []

        for url in urls:
            cached = cache.get(url)
            if cached:
                cached_results.append(cached)
                if progress_callback:
                    await progress_callback({
                        'type': 'cache_hit',
                        'url': url,
                        'result': cached
                    })
            else:
                uncached_urls.append(url)

        results.extend(cached_results)

        if not uncached_urls:
            return results

        print(f"🔍 Analyzing {len(uncached_urls)} uncached URLs in batches...")

        # Process uncached URLs in batches
        for i in range(0, len(uncached_urls), self.batch_size):
            batch = uncached_urls[i:i + self.batch_size]
            print(f"📦 Processing batch {i//self.batch_size + 1} with {len(batch)} URLs")

            # Process batch concurrently
            batch_results = await self._process_batch_concurrent(batch, progress_callback)
            results.extend(batch_results)

            # Small delay between batches to avoid overwhelming the system
            await asyncio.sleep(0.1)

        return results

    async def _process_batch_concurrent(self, urls: List[str], progress_callback=None) -> List[Dict]:
        """Process a batch of URLs concurrently."""
        loop = asyncio.get_event_loop()

        # Create tasks for concurrent processing
        tasks = []
        for url in urls:
            task = loop.run_in_executor(self.executor, self._analyze_single_url, url, progress_callback)
            tasks.append(task)

        # Wait for all tasks to complete
        batch_results = await asyncio.gather(*tasks, return_exceptions=True)

        # Handle results and exceptions
        processed_results = []
        for i, result in enumerate(batch_results):
            if isinstance(result, Exception):
                print(f"❌ Error analyzing {urls[i]}: {result}")
                # Return error result
                error_result = {
                    "url": urls[i],
                    "grade": "Error",
                    "score": 0,
                    "issues": [{"component": "Analysis", "message": f"Analysis failed: {result}", "passed": 0, "total": 1}],
                    "agent_response": f"Error: {result}"
                }
                processed_results.append(error_result)
                cache.set(urls[i], error_result)
            else:
                processed_results.append(result)
                cache.set(result['url'], result)

        return processed_results

    def _analyze_single_url(self, url: str, progress_callback=None) -> Dict:
        """Analyze a single URL synchronously (runs in thread pool)."""
        try:
            print(f"🔍 Analyzing: {url}")

            # Use the existing agent function
            results = analyze_urls_with_agent([url])

            if results and len(results) > 0:
                result = results[0]
                print(f"✅ Analyzed {url}: Grade {result.get('grade', 'Unknown')}, Score {result.get('score', 0)}")
                return result
            else:
                error_result = {
                    "url": url,
                    "grade": "No Result",
                    "score": 0,
                    "issues": [{"component": "Agent", "message": "No result returned from agent", "passed": 0, "total": 1}],
                    "agent_response": "No result from agent"
                }
                return error_result

        except Exception as e:
            print(f"❌ Error in _analyze_single_url for {url}: {e}")
            error_result = {
                "url": url,
                "grade": "Error",
                "score": 0,
                "issues": [{"component": "Analysis", "message": f"Analysis failed: {e}", "passed": 0, "total": 1}],
                "agent_response": f"Error: {e}"
            }
            return error_result

    async def analyze_with_timeout(self, urls: List[str], timeout_seconds: int = 60) -> List[Dict]:
        """Analyze URLs with a timeout to prevent hanging."""
        try:
            return await asyncio.wait_for(
                self.analyze_urls_batch(urls),
                timeout=timeout_seconds
            )
        except asyncio.TimeoutError:
            print(f"⏰ Analysis timed out after {timeout_seconds} seconds")
            # Return partial results if available
            return []

    def cleanup(self):
        """Clean up resources."""
        self.executor.shutdown(wait=True)

# Convenience functions for easy integration
async def analyze_urls_async(urls: List[str], max_concurrent: int = 3, batch_size: int = 5) -> List[Dict]:
    """Convenience function for async URL analysis."""
    analyzer = AsyncUrlAnalyzer(max_concurrent=max_concurrent, batch_size=batch_size)
    try:
        return await analyzer.analyze_urls_batch(urls)
    finally:
        analyzer.cleanup()

def analyze_urls_optimized(urls: List[str], max_concurrent: int = 3, batch_size: int = 5) -> List[Dict]:
    """Synchronous wrapper for async analysis."""
    async def run_analysis():
        return await analyze_urls_async(urls, max_concurrent, batch_size)

    return asyncio.run(run_analysis())
