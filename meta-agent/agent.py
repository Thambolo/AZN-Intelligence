from connectonion import Agent
import requests
from bs4 import BeautifulSoup
from typing import List, Dict, Tuple
import json
import os
from dotenv import load_dotenv
load_dotenv()
# --- 4. TOOL: Re-rank a batch of results by grade ---
def store_result_json(url: str, grade: str, issues: List[str], score: int, filename: str = "results.json") -> str:
    """Store the accessibility result for a URL in a JSON file."""
    record = {"url": url, "grade": grade, "issues": issues, "score": score}
    if os.path.exists(filename):
        with open(filename, "r", encoding="utf-8") as f:
            try:
                data = json.load(f)
            except Exception:
                data = []
    else:
        data = []
    data.append(record)
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)
    return f"Stored result for {url} in {filename}"

# --- 1. TOOL: Scrape a webpage ---
def scrape_page(url: str) -> str:
    """Download the HTML content of a webpage."""
    try:
        headers = {'User-Agent': 'Mozilla/5.0 (compatible; AccessibilityGrader/1.0)'}
        r = requests.get(url, headers=headers, timeout=7)
        r.raise_for_status()
        return r.text
    except Exception as e:
        return f"Error: Could not fetch page at {url}: {e}"

# --- 2. TOOL: Analyze accessibility (WCAG simulation) ---
def analyze_accessibility(html: str) -> Dict:
    """
    Analyze HTML for common accessibility issues and assign a WCAG grade.
    Returns a dictionary: {'grade': 'A'|'AA'|'AAA', 'issues': [str], 'score': int}
    """
    issues = []
    score = 100  # Start with perfect

    soup = BeautifulSoup(html, "html.parser")

    # 1. Low contrast (simulate by looking for style attributes)
    if "color" in html and "background-color" in html:
        # Simulate: real check would use color parsing
        issues.append("Potential low-contrast text detected")
        score -= 10

    # 2. Missing alternative text on images
    for img in soup.find_all("img"):
        if not img.get("alt"):
            issues.append("Image missing alt text")
            score -= 7

    # 3. Empty links
    for a in soup.find_all("a"):
        if not a.text.strip():
            issues.append("Empty link found")
            score -= 5

    # 4. Inputs without labels
    for inp in soup.find_all("input"):
        if not inp.get("aria-label") and not inp.get("placeholder"):
            issues.append("Form input missing label or placeholder")
            score -= 5

    # 5. Empty buttons
    for btn in soup.find_all("button"):
        if not btn.text.strip():
            issues.append("Empty button found")
            score -= 5

    # Assign a grade
    if score >= 90:
        grade = "AAA"
    elif score >= 75:
        grade = "AA"
    elif score >= 60:
        grade = "A"
    else:
        grade = "Not WCAG compliant"

    return {"grade": grade, "issues": issues, "score": score}

# --- 3. TOOL: Summarize accessibility findings ---
def format_grade(grade: str, issues: List[str], url: str) -> str:
    """Create a human-readable report of accessibility for a page."""
    if grade == "Not WCAG compliant":
        summary = f"❌ {url} does not meet minimum WCAG accessibility standards."
    else:
        summary = f"✅ {url} is graded {grade} for accessibility."
    if issues:
        summary += "\nFound issues:\n" + "\n".join(f"- {issue}" for issue in issues)
    else:
        summary += "\nNo major accessibility issues detected."
    return summary

# --- 4. TOOL: Re-rank a batch of results by grade ---
def rerank_results(results: List[Tuple[str, str]]) -> List[Tuple[str, str]]:
    """
    Sort list of (url, grade) pairs by grade (AAA > AA > A > Not compliant).
    """
    grade_order = {"AAA": 3, "AA": 2, "A": 1, "Not WCAG compliant": 0}
    return sorted(results, key=lambda x: grade_order.get(x[1], 0), reverse=True)

# --- 5. AGENT SYSTEM PROMPT (markdown file recommended) ---
# Place this in 'prompts/accessibility_grader.md'
# If you want to inline it for a hackathon, you can do:


# --- 6. AGENT DEFINITION ---
agent = Agent(
    name="webpage_accessibility_grader",
    system_prompt="prompts/accessibility_grader.md",
    tools=[scrape_page, analyze_accessibility, format_grade, rerank_results, store_result_json],
    max_iterations=15
)

# --- 7. EXAMPLE USAGE FOR BACKEND ---
if __name__ == "__main__":
    # Example: Grade a single webpage
    url = "https://www.wikipedia.org/"
    html = scrape_page(url)
    analysis = analyze_accessibility(html)

    # Store result in JSON
    store_result_json(url, analysis['grade'], analysis['issues'], analysis['score'])
    report = format_grade(analysis['grade'], analysis['issues'], url)
    print(report)

    # Example: Grade and re-rank multiple search results
    urls = [
        "https://www.wikipedia.org/",
        "https://www.example.com/",
        "https://www.apple.com/"
    ]
    grades = []
    for u in urls:
        h = scrape_page(u)
        a = analyze_accessibility(h)
        store_result_json(u, a['grade'], a['issues'], a['score'])
        grades.append((u, a['grade']))
    ranked = rerank_results(grades)
    print("\nRe-ranked by accessibility:")
    for url, grade in ranked:
        print(f"{url}: {grade}")