from fastapi import FastAPI, BackgroundTasks
from pydantic import BaseModel
from typing import List, Dict
import sys
import os
import random
import json
import time

# Add meta-agent to path for future import
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'meta-agent'))

from agent import analyze_urls_with_agent
from cache_manager import cache

app = FastAPI()

class AuditRequest(BaseModel):
    urls: List[str]

@app.post("/audit")
async def audit_urls(request: AuditRequest):
    """Audit URLs for accessibility with sequential processing."""
    urls = request.urls

    if not urls:
        return {"results": []}

    print(f"📥 Received audit request for {len(urls)} URLs")

    results = []

    # Process URLs sequentially to avoid rate limiting
    for url in urls:
        cached_result = cache.get(url)
        if cached_result:
            print(f"✅ Cache hit for {url}")
            results.append(cached_result)
        else:
            print(f"🔍 Analyzing {url}")
            try:
                agent_results = analyze_urls_with_agent([url])
                if agent_results and len(agent_results) > 0:
                    result = agent_results[0]
                    cache.set(url, result)
                    results.append(result)
                    print(f"✅ Analyzed {url}: Grade {result.get('grade', 'Unknown')}, Score {result.get('score', 0)}")
                else:
                    error_result = {
                        "url": url,
                        "grade": "No Result",
                        "score": 0,
                        "issues": [{"component": "Agent", "message": "No result returned from agent", "passed": 0, "total": 1}],
                        "agent_response": "No result from agent"
                    }
                    results.append(error_result)
                    cache.set(url, error_result)
                    # Add minimum pause between URL analyses to prevent rate limiting
                    if url != urls[-1]:  # Don't pause after the last URL
                        print(f"⏳ Pausing 30 seconds before next URL...")
                        time.sleep(30)
            except Exception as e:
                print(f"❌ Error analyzing {url}: {e}")
                error_result = {
                    "url": url,
                    "grade": "Error",
                    "score": 0,
                    "issues": [{"component": "Analysis", "message": f"Analysis failed: {e}", "passed": 0, "total": 1}],
                    "agent_response": f"Error: {e}"
                }
                results.append(error_result)
                cache.set(url, error_result)


    print(f"📤 Returning {len(results)} results")
    return {"results": results}

@app.post("/audit/sync")
def audit_urls_sync(request: AuditRequest):
    """Legacy synchronous endpoint for backward compatibility."""
    results = []
    for url in request.urls:
        cached_result = cache.get(url)
        if cached_result:
            results.append(cached_result)
        else:
            print(f"🔍 Analyzing {url} synchronously")
            agent_results = analyze_urls_with_agent([url])
            if agent_results:
                result = agent_results[0]
                cache.set(url, result)
                results.append(result)
            else:
                error_result = {
                    "url": url,
                    "grade": "Error",
                    "score": 0,
                    "issues": [{"component": "Agent", "message": "No result from agent", "passed": 0, "total": 1}]
                }
                results.append(error_result)

    return {"results": results}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
