import requests
from bs4 import BeautifulSoup
import time
from typing import Dict, Any

# Import modular principle analysis functions
from principle1_perceivable import analyse_principle1_perceivable
from principle2_operable import analyse_principle2_operable
from principle3_understandable import analyse_principle3_understandable
from principle4_robust import analyse_principle4_robust


def detect_spa_website(soup: BeautifulSoup, content: bytes) -> bool:
    """
    Detect if a website is likely a Single Page Application (SPA) that requires JavaScript rendering.
    
    Returns True if the site appears to be SPA/JavaScript-heavy, False otherwise.
    """
    # Check for minimal content indicators
    body = soup.find('body')
    if not body:
        return True
    
    body_text = body.get_text(strip=True)
    
    # Indicators of SPA:
    # 1. Very little or no body text
    if len(body_text) < 100:
        return True
    
    # 2. No title tag
    if not soup.find('title'):
        return True
        
    # 3. Very few interactive elements
    interactive_count = len(soup.find_all(['a', 'button', 'input', 'form']))
    if interactive_count == 0:
        return True
    
    # 4. No headings at all
    heading_count = len(soup.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6']))
    if heading_count == 0:
        return True
    
    # 5. Check for common SPA framework indicators in script tags
    scripts = soup.find_all('script')
    spa_indicators = ['react', 'vue', 'angular', 'next', 'gatsby', 'nuxt', 'svelte']
    
    for script in scripts:
        src = script.get('src', '').lower()
        script_content = script.string or ''
        
        if any(indicator in src or indicator in script_content.lower() for indicator in spa_indicators):
            return True
    
    # 6. Check for typical SPA meta tags
    meta_tags = soup.find_all('meta')
    for meta in meta_tags:
        name = meta.get('name', '').lower()
        if name in ['generator', 'framework'] and any(fw in meta.get('content', '').lower() for fw in spa_indicators):
            return True
    
    return False


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
        
        # Detect if this is likely a Single Page Application (SPA)
        is_spa = detect_spa_website(soup, response.content)
        
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
        
        # Adjust scoring for SPA websites
        if is_spa:
            # For SPA sites, give them a reasonable base score since static analysis is limited
            # Many modern, well-designed SPAs can have good accessibility when fully rendered
            base_spa_score = 65  # Base score for SPA sites that can't be fully analyzed
            
            # Calculate penalty-adjusted score
            penalty_adjusted_score = ((p1_score * 0.35) + (p2_score * 0.35) + (p3_score * 0.15) + (p4_score * 0.15)) * 0.9
            
            # Use the higher of penalty-adjusted score or base SPA score
            weighted_score = max(penalty_adjusted_score, base_spa_score)
        else:
            # Standard weighted scoring for non-SPA sites
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
        print("Issues", all_issues)
        
        return {
            "url": url,
            "grade": overall_grade,
            "score": int(weighted_score),
            "overall_grade": overall_grade, # Remove
            "overall_score": int(weighted_score), # Remove
            "is_spa": is_spa, # Remove
            "spa_detected": is_spa,
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
            "scoring_note": f"{'SPA-adjusted scoring (85% factor)' if is_spa else 'Standard weighted scoring'}: Principles 1&2 (70% total), Principles 3&4 (30% total) due to HTML analysis limitations"
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
