from fastapi import FastAPI
from pydantic import BaseModel
from typing import List, Dict
import sys
import os
import random
import json

# Add meta-agent to path for future import
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'meta-agent'))

from agent import scrape_page, analyze_accessibility, ai_accessibility_analysis

app = FastAPI()

class AuditRequest(BaseModel):
    urls: List[str]

# Global cache for URL analysis results
cache: Dict[str, Dict] = {}

app = FastAPI()

class AuditRequest(BaseModel):
    urls: List[str]

@app.post("/audit")
async def audit_urls(request: AuditRequest):
    results = []
    for url in request.urls:
        if url in cache:
            print(f"Cache hit for {url}")
            results.append(cache[url])
        else:
            print(f"Analyzing {url}")
            html = scrape_page(url)
            if html.startswith("Error:"):
                data = {
                    "url": url,
                    "grade": "Fail",
                    "score": 0,
                    "issues": [{"component": "Scraping", "message": html, "passed": 0, "total": 1}]
                }
            else:
                analysis = analyze_accessibility(html)
                ai_result = ai_accessibility_analysis(html, url, analysis)
                
                data = {
                    "url": url,
                    "grade": analysis["grade"],
                    "score": analysis["score"],
                    "issues": analysis["issues"]
                }
                
                # Add AI analysis if available
                ai_analysis = ai_result.get("ai_analysis")
                if ai_analysis:
                    data["ai_grade"] = ai_analysis.get("wcag_grade")
                    data["ai_score"] = ai_analysis.get("overall_score")
                    data["critical_issues"] = ai_analysis.get("critical_issues", [])
                    data["improvement_suggestions"] = ai_analysis.get("improvement_suggestions", [])
                    data["developer_checklist"] = ai_analysis.get("developer_checklist", [])
                    data["next_steps"] = ai_analysis.get("next_steps", "")
                
                cache[url] = data
            results.append(data)
    return {"results": results}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
