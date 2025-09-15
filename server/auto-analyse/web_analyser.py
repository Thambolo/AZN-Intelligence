import requests
from bs4 import BeautifulSoup
import time
from typing import Dict, Any

# Import modular principle analysis functions
from principle1_perceivable import analyse_principle1_perceivable
from principle2_operable import analyse_principle2_operable
from principle3_understandable import analyse_principle3_understandable
from principle4_robust import analyse_principle4_robust


def comprehensive_analyse_url(url: str, timeout: int = 10) -> Dict[str, Any]:
    """
    Perform comprehensive WCAG 2.2 analysis across all four principles with weighted scoring.
    
    This function fetches the webpage content once and passes the BeautifulSoup object
    to each modular principle analysis function for better efficiency and consistency.
    
    Principles 1 & 2 have higher weight (70%) as they are more accurately testable with HTML analysis.
    Principles 3 & 4 have lower weight (30%) due to limitations of static HTML analysis.
    """
    try:
        start_time = time.time()
        
        # Fetch webpage content once with proper headers
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none'
        }
        
        # Use session to handle cookies and redirects properly
        session = requests.Session()
        session.headers.update(headers)
        
        response = session.get(url, timeout=timeout, allow_redirects=True)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Analyse each principle using modular functions
        principle1_result = analyse_principle1_perceivable(soup, url)
        principle2_result = analyse_principle2_operable(soup, url)
        principle3_result = analyse_principle3_understandable(soup, url)
        principle4_result = analyse_principle4_robust(soup, url)
        
        # Extract scores for weighted calculation
        p1_score = principle1_result.get("score", 0)
        p2_score = principle2_result.get("score", 0)
        p3_score = principle3_result.get("score", 0)
        p4_score = principle4_result.get("score", 0)
        
        # Weighted scoring (P1&P2: 35% each, P3&P4: 15% each)
        weighted_score = (p1_score * 0.35) + (p2_score * 0.35) + (p3_score * 0.15) + (p4_score * 0.15)
        
        # Determine overall grade based on weighted score
        if weighted_score >= 85:
            overall_grade = "AAA"
        elif weighted_score >= 75:
            overall_grade = "AA"
        elif weighted_score >= 60:
            overall_grade = "A"
        else:
            overall_grade = "Not WCAG compliant"
        
        # Compile all issues
        all_issues = []
        for result in [principle1_result, principle2_result, principle3_result, principle4_result]:
            if "issues" in result:
                all_issues.extend(result["issues"])
        
        analysis_time = round(time.time() - start_time, 2)
        
        return {
            "url": url,
            "grade": overall_grade,
            "score": int(weighted_score),
            "overall_grade": overall_grade,
            "overall_score": int(weighted_score),
            "principle_scores": {
                "principle1_perceivable": p1_score,
                "principle2_operable": p2_score,
                "principle3_understandable": p3_score,
                "principle4_robust": p4_score
            },
            "principle_grades": {
                "principle1_perceivable": principle1_result.get("grade", "Error"),
                "principle2_operable": principle2_result.get("grade", "Error"),
                "principle3_understandable": principle3_result.get("grade", "Error"),
                "principle4_robust": principle4_result.get("grade", "Error")
            },
            "detailed_results": {
                "principle1": principle1_result,
                "principle2": principle2_result,
                "principle3": principle3_result,
                "principle4": principle4_result
            },
            "all_issues": all_issues,
            "analysis_time_seconds": analysis_time,
            "scoring_note": "Weighted scoring: Principles 1&2 (70% total), Principles 3&4 (30% total) due to HTML analysis limitations"
        }
        
    except Exception as e:
        return {
            "url": url,
            "grade": "Error",
            "score": 0,
            "overall_grade": "Error",
            "overall_score": 0,
            "error": f"Comprehensive analysis failed: {str(e)}",
            "analysis_time_seconds": 0
        }
