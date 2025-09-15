import asyncio
import aiohttp
import time

async def audit_url(session, url, request_id):
    """Send audit request for a single URL."""
    payload = {"url": url, "timeout": 30}
    
    start = time.time()
    print(f"🚀 Request {request_id}: Starting {url}")
    
    try:
        async with session.post("http://localhost:8000/audit", json=payload) as response:
            result = await response.json()
            duration = time.time() - start
            
            grade = result.get("result", {}).get("grade", "Error")
            score = result.get("result", {}).get("score", 0)
            
            print(f"✅ Request {request_id} ({url}): {grade} ({score}/100) in {duration:.1f}s")
            return {"id": request_id, "grade": grade, "time": duration}
            
    except Exception as e:
        duration = time.time() - start
        print(f"❌ Request {request_id}: Failed in {duration:.1f}s - {e}")
        return {"id": request_id, "error": str(e), "time": duration}

async def main():
    """Run concurrent audit test."""
    # Test URLs
    urls = [
        "https://example.com",
        "https://google.com", 
        "https://github.com",
        "https://wikipedia.org",
        "https://fastapi.tiangolo.com",
        "https://pydantic.dev",
        "https://python.org",
        "https://stackoverflow.com",
        "https://reddit.com",
        "https://news.ycombinator.com",
        "https://openai.com",
        "https://twitter.com",
    ]
    
    print("🧪 Testing Concurrent WCAG Audits")
    print("=" * 40)
    
    # Test concurrent requests
    start_time = time.time()
    
    async with aiohttp.ClientSession() as session:
        # Create concurrent tasks
        tasks = [audit_url(session, url, i+1) for i, url in enumerate(urls)]
        
        # Wait for all to complete
        results = await asyncio.gather(*tasks)
        
    total_time = time.time() - start_time
    
    print("=" * 40)
    print(f"🎯 All {len(urls)} requests completed in {total_time:.1f}s")
    
    # Show results
    successful = [r for r in results if "grade" in r]
    if successful:
        avg_time = sum(r["time"] for r in successful) / len(successful)
        print(f"📊 Average response time: {avg_time:.1f}s")
        print(f"⚡ Concurrency benefit: ~{(avg_time * len(urls) - total_time):.1f}s saved")

if __name__ == "__main__":
    print("🔧 Make sure server is running: python server/app.py")
    print("⏳ Starting in 2 seconds...")
    time.sleep(2)
    asyncio.run(main())