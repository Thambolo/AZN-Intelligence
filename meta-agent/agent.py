from fpdf import FPDF
# --- PDF REPORT GENERATION ---
def save_pdf_report(url: str, analysis: dict, ai_feedback: str, filename: str = None):
    def to_ascii(text):
        # Replace curly quotes and other common Unicode with ASCII equivalents
        replacements = {
            '\u201c': '"', '\u201d': '"',  # left/right double quote
            '\u2018': "'", '\u2019': "'",  # left/right single quote
            '\u2013': '-', '\u2014': '-',    # en dash, em dash
            '\u2026': '...',                  # ellipsis
            '\u00a0': ' ',                    # non-breaking space
        }
        for uni, asc in replacements.items():
            text = text.replace(uni, asc)
        # Remove any other non-ASCII chars
        return text.encode('ascii', errors='ignore').decode('ascii')
    """Save a nicely formatted PDF report for the accessibility analysis."""
    if filename is None:
        safe_url = url.replace('https://', '').replace('http://', '').replace('/', '_').replace(':', '_')
        filename = f"accessibility_report_{safe_url}.pdf"
    from fpdf import XPos, YPos
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Times", 'B', 16)
    pdf.cell(0, 10, "Accessibility Report", new_x=XPos.LMARGIN, new_y=YPos.NEXT, align="C")
    pdf.set_font("Times", '', 12)
    pdf.cell(0, 10, f"URL: {url}", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    pdf.cell(0, 10, f"Score: {analysis['score']}/100", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    pdf.cell(0, 10, f"Grade: {analysis['grade']}", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    pdf.ln(5)
    pdf.set_font("Times", 'B', 12)
    pdf.cell(0, 10, "Accessibility Issues:", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    pdf.set_font("Times", '', 11)
    issues = analysis.get('issues', [])
    filtered = [i for i in issues if i.get('passed', 0) != i.get('total', 1)]
    if filtered:
        pdf.set_fill_color(230, 230, 230)
        pdf.set_font("Times", 'B', 11)
        pdf.cell(60, 8, to_ascii("Component"), border=1, fill=True)
        pdf.cell(80, 8, to_ascii("Issue"), border=1, fill=True)
        pdf.cell(30, 8, to_ascii("Pass/Total"), border=1, new_x=XPos.LMARGIN, new_y=YPos.NEXT, fill=True)
        pdf.set_font("Times", '', 11)
        for i in filtered:
            comp = to_ascii(i.get('component', '')[:28])
            msg = to_ascii(i.get('message', '')[:38])
            pt = to_ascii(f"{i.get('passed', 0)}/{i.get('total', 1)}")
            pdf.cell(60, 8, comp, border=1)
            pdf.cell(80, 8, msg, border=1)
            pdf.cell(30, 8, pt, border=1, new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    else:
        pdf.cell(0, 8, to_ascii("All accessibility checks passed!"), new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    pdf.ln(5)
    pdf.set_font("Times", 'B', 12)
    pdf.cell(0, 10, to_ascii("AI Accessibility Feedback:"), new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    pdf.set_font("Times", '', 11)
    pdf.multi_cell(0, 8, to_ascii(ai_feedback))
    pdf.output(filename)
    print(f"PDF report saved to {filename}")
import openai
# --- AI TOOL: Analyze accessibility with OpenAI ---
def ai_accessibility_analysis(html: str, url: str = "") -> dict:
    """Use OpenAI to analyze HTML for accessibility issues and grade the page."""
    import os
    prompt = f"""
You are an expert in web accessibility and WCAG compliance. Analyze the following HTML for accessibility issues. List specific problems, suggest improvements, and assign a grade (A, AA, AAA) based on WCAG. If possible, provide a short summary for developers and users.

URL: {url}
HTML:
{html[:6000]}
"""
    # Read from environment or use defaults
    try:
        max_tokens = int(os.getenv("max_completion_tokens", 600))
    except Exception:
        max_tokens = 600
    # try:
    #     temperature = float(os.getenv("TEMPERATURE", 0.2))
    # except Exception:
    #     temperature = 0.2
    model = os.getenv("MODEL", "gpt-5-nano")
    try:
        client = openai.OpenAI()
        response = client.chat.completions.create(
            model=model,
            messages=[{"role": "system", "content": "You are a helpful accessibility auditor."},
                      {"role": "user", "content": prompt}],
            max_completion_tokens=max_tokens,
            # temperature=temperature
        )
        content = response.choices[0].message.content.strip()
        print("\nAI Accessibility Feedback (from ai_accessibility_analysis):\n" + content)
        return {"ai_feedback": content}
    except Exception as e:
        return {"ai_feedback": f"AI analysis failed: {e}"}
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
    import datetime
    timestamp = datetime.datetime.now(datetime.UTC).isoformat()
    new_entry = {
        "timestamp": timestamp,
        "grade": grade,
        "score": score,
        "issues": issues
    }
    # Load existing data as a dict keyed by url
    if os.path.exists(filename):
        with open(filename, "r", encoding="utf-8") as f:
            try:
                data = json.load(f)
            except Exception:
                data = {}
    else:
        data = {}
    # Ensure structure: { url: { "analyses": [ ... ] } }
    if url not in data:
        data[url] = {"analyses": []}
    data[url]["analyses"].append(new_entry)
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
    issues = []  # Will be a list of dicts: {component, message, passed, total}
    soup = BeautifulSoup(html, "html.parser")

    # --- Checklist Components ---
    # Each component is a tuple: (component_name, num_passed, num_total, [issues])
    components = []

    # 1. Images: alt text
    imgs = soup.find_all("img")
    total_imgs = len(imgs)
    alt_ok = 0
    alt_empty_ok = 0
    for img in imgs:
        alt = img.get("alt")
        if alt is not None and alt.strip() != "":
            alt_ok += 1
        if alt == "":
            alt_empty_ok += 1
    # All images alt
    if total_imgs > 0:
        components.append(("Images with alt text", alt_ok, total_imgs, [] if alt_ok == total_imgs else [{"component": "Images with alt text", "passed": alt_ok, "total": total_imgs, "message": f"{alt_ok}/{total_imgs} images have alt text."}]))
        components.append(("Decorative images with empty alt", alt_empty_ok, total_imgs, [] if alt_empty_ok == total_imgs else [{"component": "Decorative images with empty alt", "passed": alt_empty_ok, "total": total_imgs, "message": f"{alt_empty_ok}/{total_imgs} images have empty alt for decorative."}]))

    # 2. Empty links
    links = soup.find_all("a")
    total_links = len(links)
    nonempty_links = sum(1 for a in links if a.text.strip())
    if total_links > 0:
        components.append(("Links with text", nonempty_links, total_links, [] if nonempty_links == total_links else [{"component": "Links with text", "passed": nonempty_links, "total": total_links, "message": f"{nonempty_links}/{total_links} links have text."}]))

    # 3. Inputs with label or placeholder
    inputs = soup.find_all("input")
    total_inputs = len(inputs)
    labeled_inputs = 0
    for inp in inputs:
        if inp.get("aria-label") or inp.get("placeholder"):
            labeled_inputs += 1
    if total_inputs > 0:
        components.append(("Inputs with label or placeholder", labeled_inputs, total_inputs, [] if labeled_inputs == total_inputs else [{"component": "Inputs with label or placeholder", "passed": labeled_inputs, "total": total_inputs, "message": f"{labeled_inputs}/{total_inputs} inputs have label or placeholder."}]))

    # 4. Buttons with text
    buttons = soup.find_all("button")
    total_buttons = len(buttons)
    nonempty_buttons = sum(1 for btn in buttons if btn.text.strip())
    if total_buttons > 0:
        components.append(("Buttons with text", nonempty_buttons, total_buttons, [] if nonempty_buttons == total_buttons else [{"component": "Buttons with text", "passed": nonempty_buttons, "total": total_buttons, "message": f"{nonempty_buttons}/{total_buttons} buttons have text."}]))

    # 5. Headings: only one h1
    h1s = soup.find_all("h1")
    total_h1s = len(h1s)
    components.append(("Single <h1> per page", 1 if total_h1s == 1 else 0, 1, [] if total_h1s == 1 else [{"component": "Single <h1> per page", "passed": 1 if total_h1s == 1 else 0, "total": 1, "message": f"{total_h1s} <h1> tags found; should be 1."}]))

    # 6. Table: th headers
    tables = soup.find_all("table")
    th_count = 0
    th_total = 0
    for table in tables:
        ths = table.find_all("th")
        th_total += len(ths)
        th_count += sum(1 for th in ths if th.get("scope") in ("col", "row"))
    if th_total > 0:
        components.append(("Table headers with scope", th_count, th_total, [] if th_count == th_total else [{"component": "Table headers with scope", "passed": th_count, "total": th_total, "message": f"{th_count}/{th_total} table headers have scope."}]))

    # --- Calculate Score ---
    total_components = len(components)
    if total_components == 0:
        score = 100
        grade = "AAA"
        issues = [{"component": "General", "message": "No accessibility components detected.", "passed": 1, "total": 1}]
    else:
        # Each component is equally weighted
        component_scores = []
        for name, passed, total, comp_issues in components:
            if total > 0:
                component_score = passed / total
            else:
                component_score = 1.0
            component_scores.append(component_score)
            issues.extend(comp_issues)
        avg_score = sum(component_scores) / total_components
        score = int(round(avg_score * 100))
        # Grade assignment
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
    summary = f"\n{'='*60}\nURL: {url}\nGrade: {grade}\n"
    if issues:
        filtered = [i for i in issues if i.get('passed', 0) != i.get('total', 1)]
        if filtered:
            summary += "\nComponent                        | Issue                                      | Pass/Total\n"
            summary += "-"*75 + "\n"
            for i in filtered:
                comp = i.get('component', '')[:30].ljust(30)
                msg = i.get('message', '')[:40].ljust(40)
                pt = f"{i.get('passed', 0)}/{i.get('total', 1)}".ljust(10)
                summary += f"{comp} | {msg} | {pt}\n"
        else:
            summary += "All accessibility checks passed!"
    else:
        summary += "No major accessibility issues detected."
    summary += f"\n{'='*60}"
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
    tools=[scrape_page, analyze_accessibility, ai_accessibility_analysis, format_grade, rerank_results, store_result_json],
    max_iterations=15
)

# --- 7. EXAMPLE USAGE FOR BACKEND ---
if __name__ == "__main__":


    # Example: Grade a single webpage
    # url = "https://www.wikipedia.org/"
    # html = scrape_page(url)
    # analysis = analyze_accessibility(html)
    # ai_result = ai_accessibility_analysis(html, url)

    # Store result in JSON (now includes AI feedback)
    # store_result_json(url, analysis['grade'], analysis['issues'], analysis['score'])
    # ai_feedback = ai_result.get("ai_feedback", "No AI feedback.")
    # save_pdf_report(url, analysis, ai_feedback)

    # Example: Grade and re-rank multiple search results
    urls = [
        # "https://www.wikipedia.org/",
        "https://www.example.com/",
        # "https://www.apple.com/"
    ]
    grades = []
    for u in urls:
        h = scrape_page(u)
        a = analyze_accessibility(h)
        ai_result = ai_accessibility_analysis(h, u)
        store_result_json(u, a['grade'], a['issues'], a['score'])
        grades.append((u, a['grade']))
    ai_feedback = ai_result.get("ai_feedback", "No AI feedback.")
    print(f"\nAI Accessibility Feedback for {u}:\n" + ai_feedback)
    save_pdf_report(u, a, ai_feedback)
    ranked = rerank_results(grades)
    print("\nRe-ranked by accessibility:")
    for url, grade in ranked:
        print(f"{url}: {grade}")
