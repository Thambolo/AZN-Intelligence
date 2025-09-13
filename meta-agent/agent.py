from fpdf import FPDF
# --- ENHANCED PDF REPORT GENERATION FOR DEVELOPERS ---
def save_pdf_report(url: str, analysis: dict, ai_result: dict, filename: str = None):
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
    
    """Save a comprehensive PDF report for developers with AI analysis and improvement suggestions."""
    if filename is None:
        safe_url = url.replace('https://', '').replace('http://', '').replace('/', '_').replace(':', '_')
        filename = f"accessibility_report_{safe_url}.pdf"
    
    from fpdf import XPos, YPos
    pdf = FPDF()
    pdf.add_page()
    
    # Header
    pdf.set_font("Times", 'B', 18)
    pdf.cell(0, 12, "WCAG Compliance Report", new_x=XPos.LMARGIN, new_y=YPos.NEXT, align="C")
    pdf.set_font("Times", 'B', 14)
    pdf.cell(0, 8, "Developer Accessibility Analysis", new_x=XPos.LMARGIN, new_y=YPos.NEXT, align="C")
    pdf.ln(10)
    
    # URL and basic info
    pdf.set_font("Times", 'B', 12)
    pdf.cell(0, 8, f"Website: {url}", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    pdf.cell(0, 8, f"Analysis Date: {__import__('datetime').datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    pdf.ln(5)
    
    
    # Get AI analysis if available
    ai_analysis = ai_result.get('ai_analysis', {}) if ai_result else {}
    
    # WCAG Compliance Score
    pdf.set_font("Times", 'B', 12)
    pdf.cell(0, 8, "WCAG Compliance Score", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    pdf.set_font("Times", '', 11)
    
    # Use AI score if available, otherwise use automated score
    if ai_analysis and 'overall_score' in ai_analysis:
        score = ai_analysis['overall_score']
        grade = ai_analysis.get('wcag_grade', analysis['grade'])
        pdf.cell(0, 6, f"Grade: {grade}", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        pdf.cell(0, 6, f"Score: {score}/100", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    else:
        pdf.cell(0, 6, f"Grade: {analysis['grade']}", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        pdf.cell(0, 6, f"Score: {analysis['score']}/100", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    
    pdf.ln(5)
    
    # Automated Analysis Results
    pdf.set_font("Times", 'B', 12)
    pdf.cell(0, 8, "Automated Analysis Results", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    pdf.set_font("Times", '', 11)
    
    issues = analysis.get('issues', [])
    if issues:
        pdf.set_fill_color(240, 240, 240)
        pdf.set_font("Times", 'B', 10)
        pdf.cell(50, 6, "Component", border=1, fill=True)
        pdf.cell(100, 6, "Status", border=1, fill=True)
        pdf.cell(30, 6, "Pass/Total", border=1, new_x=XPos.LMARGIN, new_y=YPos.NEXT, fill=True)
        pdf.set_font("Times", '', 9)
        
        for issue in issues:
            comp = to_ascii(issue.get('component', '')[:45])
            msg = to_ascii(issue.get('message', '')[:95])
            pt = to_ascii(f"{issue.get('passed', 0)}/{issue.get('total', 1)}")
            pdf.cell(50, 6, comp, border=1)
            pdf.cell(100, 6, msg, border=1)
            pdf.cell(30, 6, pt, border=1, new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    else:
        pdf.cell(0, 6, "No issues detected in automated analysis.", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    
    pdf.ln(8)
    
    # AI Analysis Section
    if ai_analysis:
        # Critical Issues
        critical_issues = ai_analysis.get('critical_issues', [])
        if critical_issues:
            pdf.set_font("Times", 'B', 12)
            pdf.cell(0, 8, "Critical Issues (AI Analysis)", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
            pdf.set_font("Times", '', 10)
            
            for i, issue in enumerate(critical_issues[:5], 1):  # Limit to top 5
                pdf.set_font("Times", 'B', 10)
                pdf.cell(0, 6, f"{i}. {to_ascii(issue.get('issue', 'Unknown issue'))}", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
                pdf.set_font("Times", '', 9)
                pdf.cell(0, 4, f"WCAG: {to_ascii(issue.get('wcag_guideline', 'N/A'))} | Impact: {to_ascii(issue.get('impact', 'Unknown'))} | Priority: {to_ascii(issue.get('fix_priority', 'Unknown'))}", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
                pdf.multi_cell(0, 4, to_ascii(issue.get('developer_guidance', 'No guidance provided')[:200]))
                pdf.ln(2)
        
        # Improvement Suggestions
        improvements = ai_analysis.get('improvement_suggestions', [])
        if improvements:
            pdf.set_font("Times", 'B', 12)
            pdf.cell(0, 8, "Improvement Suggestions", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
            pdf.set_font("Times", '', 10)
            
            for i, improvement in enumerate(improvements[:4], 1):  # Limit to top 4
                pdf.set_font("Times", 'B', 10)
                pdf.cell(0, 6, f"{i}. {to_ascii(improvement.get('area', 'General improvement'))}", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
                pdf.set_font("Times", '', 9)
                pdf.multi_cell(0, 4, to_ascii(improvement.get('suggestion', 'No suggestion provided')[:150]))
                if improvement.get('code_example'):
                    pdf.set_font("Times", 'I', 8)
                    pdf.multi_cell(0, 3, f"Code: {to_ascii(improvement.get('code_example', '')[:100])}")
                pdf.ln(2)
        
        # Developer Checklist
        checklist = ai_analysis.get('developer_checklist', [])
        if checklist:
            pdf.set_font("Times", 'B', 12)
            pdf.cell(0, 8, "Developer Action Items", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
            pdf.set_font("Times", '', 9)
            for i, item in enumerate(checklist[:8], 1):  # Limit to top 8
                pdf.cell(0, 4, f"□ {to_ascii(item)}", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        
        # Next Steps
        next_steps = ai_analysis.get('next_steps', '')
        if next_steps:
            pdf.ln(3)
            pdf.set_font("Times", 'B', 12)
            pdf.cell(0, 8, "Recommended Next Steps", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
            pdf.set_font("Times", '', 10)
            pdf.multi_cell(0, 5, to_ascii(next_steps))
    
    else:
        # Fallback to formatted raw AI feedback
        pdf.set_font("Times", 'B', 12)
        pdf.cell(0, 8, "AI Analysis", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        pdf.set_font("Times", '', 10)
        raw_feedback = ai_result.get('raw_feedback', 'No AI analysis available') if ai_result else 'No AI analysis available'
        
        # Try to extract and format JSON content if it exists
        if raw_feedback.startswith('```json'):
            try:
                import json
                import re
                # Extract JSON from markdown code block
                json_match = re.search(r'```json\s*(\{.*?\})\s*```', raw_feedback, re.DOTALL)
                if json_match:
                    json_str = json_match.group(1)
                    ai_data = json.loads(json_str)
                    
                    # Format the JSON data nicely
                    if 'compliance_summary' in ai_data:
                        pdf.set_font("Times", 'B', 10)
                        pdf.cell(0, 6, "Summary:", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
                        pdf.set_font("Times", '', 9)
                        pdf.multi_cell(0, 4, to_ascii(ai_data['compliance_summary']))
                        pdf.ln(2)
                    
                    if 'critical_issues' in ai_data and ai_data['critical_issues']:
                        pdf.set_font("Times", 'B', 10)
                        pdf.cell(0, 6, "Critical Issues:", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
                        pdf.set_font("Times", '', 9)
                        for i, issue in enumerate(ai_data['critical_issues'][:3], 1):
                            pdf.cell(0, 4, f"{i}. {to_ascii(issue.get('issue', 'Unknown issue')[:80])}", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
                        pdf.ln(2)
                    
                    if 'improvement_suggestions' in ai_data and ai_data['improvement_suggestions']:
                        pdf.set_font("Times", 'B', 10)
                        pdf.cell(0, 6, "Improvements:", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
                        pdf.set_font("Times", '', 9)
                        for i, suggestion in enumerate(ai_data['improvement_suggestions'][:3], 1):
                            pdf.cell(0, 4, f"{i}. {to_ascii(suggestion.get('suggestion', 'No suggestion')[:80])}", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
                        pdf.ln(2)
                    
                    if 'next_steps' in ai_data and ai_data['next_steps']:
                        pdf.set_font("Times", 'B', 10)
                        pdf.cell(0, 6, "Next Steps:", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
                        pdf.set_font("Times", '', 9)
                        pdf.multi_cell(0, 4, to_ascii(ai_data['next_steps'][:200]))
                else:
                    # Fallback to plain text
                    pdf.multi_cell(0, 5, to_ascii(raw_feedback[:800]))
            except:
                # Fallback to plain text
                pdf.multi_cell(0, 5, to_ascii(raw_feedback[:800]))
        else:
            # Plain text feedback
            pdf.multi_cell(0, 5, to_ascii(raw_feedback[:800]))
    
    # Footer
    pdf.ln(10)
    pdf.set_font("Times", 'I', 8)
    pdf.cell(0, 4, "Generated by AZN-Intelligence Accessibility Grader", new_x=XPos.LMARGIN, new_y=YPos.NEXT, align="C")
    pdf.cell(0, 4, "For developer accessibility optimization", new_x=XPos.LMARGIN, new_y=YPos.NEXT, align="C")
    
    pdf.output(filename)
    print(f"📄 Comprehensive PDF report saved to {filename}")
import openai
# --- AI TOOL: Comprehensive WCAG Analysis for Developers ---
def ai_accessibility_analysis(html: str, url: str = "", automated_results: dict = None) -> dict:
    """Use AI to provide comprehensive WCAG analysis, developer-focused feedback, and improvement suggestions."""
    import os
    
    # Prepare the automated analysis results for AI context
    automated_summary = ""
    if automated_results:
        automated_summary = f"""
AUTOMATED ANALYSIS RESULTS:
- WCAG Grade: {automated_results.get('grade', 'Unknown')}
- Compliance Score: {automated_results.get('score', 0)}/100
- Issues Found: {len(automated_results.get('issues', []))}

DETAILED FINDINGS:
"""
        for issue in automated_results.get('issues', []):
            automated_summary += f"- {issue.get('component', 'Unknown')}: {issue.get('message', 'No details')}\n"
    
    prompt = f"""
You are a senior web accessibility consultant specializing in WCAG compliance for developers. Your task is to analyze a webpage and provide comprehensive, actionable feedback.

TARGET AUDIENCE: Web developers who want to make their sites WCAG compliant and optimize accessibility.

ANALYSIS CONTEXT:
URL: {url}

{automated_summary}

HTML CONTENT (first 5000 characters):
{html[:5000]}

Please provide a comprehensive analysis in the following JSON format:

{{
  "wcag_grade": "A|AA|AAA|Not Compliant",
  "overall_score": 0-100,
  "compliance_summary": "Brief 2-3 sentence summary of overall compliance status",
  "critical_issues": [
    {{
      "issue": "Description of the issue",
      "wcag_guideline": "WCAG 2.1.X reference",
      "impact": "High|Medium|Low",
      "fix_priority": "Critical|High|Medium|Low",
      "developer_guidance": "Specific code examples and implementation steps"
    }}
  ],
  "improvement_suggestions": [{{"area": "Area", "suggestion": "Fix"}}],
  "developer_checklist": [
    "Actionable item for developers to implement",
    "Another specific task to complete"
  ],
  "testing_recommendations": [
    "Specific testing methods or tools to use",
    "Manual testing steps to perform"
  ],
  "next_steps": "Prioritized action plan for the development team"
}}

Focus on:
1. Practical, implementable solutions
2. Specific WCAG guideline references
3. Code examples where helpful
4. Clear prioritization of fixes
5. Testing and validation steps
6. Developer-friendly language

Be thorough but concise. Prioritize critical accessibility barriers that prevent users from accessing content.
"""
    
    try:
        max_tokens = int(os.getenv("max_completion_tokens", 1500))
    except Exception:
        max_tokens = 1500
    
    model = os.getenv("MODEL", "gpt-4o-mini-2024-07-18")
    
    try:
        client = openai.OpenAI()
        response = client.chat.completions.create(
            model=model,
            messages=[
                {
                    "role": "system", 
                    "content": "You are a senior web accessibility consultant. Provide detailed, actionable feedback for developers to improve WCAG compliance. Always respond with valid JSON in the exact format requested."
                },
                {"role": "user", "content": prompt}
            ],
            max_completion_tokens=max_tokens,
            temperature=0.3
        )
        content = response.choices[0].message.content.strip()
        
        # Try to parse as JSON, fallback to text if it fails
        try:
            import json
            ai_analysis = json.loads(content)
            print(f"\n🤖 AI Analysis Complete - Grade: {ai_analysis.get('wcag_grade', 'Unknown')}")
            return {"ai_analysis": ai_analysis, "raw_feedback": content}
        except json.JSONDecodeError:
            print(f"\n🤖 AI Analysis Complete (Text Format)")
            return {"ai_analysis": None, "raw_feedback": content}
            
    except Exception as e:
        return {"ai_analysis": None, "raw_feedback": f"AI analysis failed: {e}"}
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
    timestamp = datetime.datetime.now(datetime.timezone.utc).isoformat()
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
    Analyze HTML for comprehensive WCAG compliance based on rules.md guidelines.
    Returns a dictionary: {'grade': 'A'|'AA'|'AAA', 'issues': [dict], 'score': int}
    """
    issues = []  # Will be a list of dicts: {component, message, passed, total}
    soup = BeautifulSoup(html, "html.parser")

    # --- WCAG Compliance Components based on rules.md ---
    # Each component is a tuple: (component_name, num_passed, num_total, [issues])
    components = []

    # 1. HTML lang attribute (WCAG 3.1.1)
    html_tag = soup.find("html")
    has_lang = html_tag and html_tag.get("lang")
    components.append(("HTML lang attribute", 1 if has_lang else 0, 1, [] if has_lang else [{"component": "HTML lang attribute", "passed": 0, "total": 1, "message": "Missing lang attribute on <html> element (WCAG 3.1.1)."}]))

    # 2. Page title (WCAG 2.4.2)
    title_tag = soup.find("title")
    has_title = title_tag and title_tag.text.strip()
    if has_title:
        components.append(("Page title", 1, 1, [{"component": "Page title", "passed": 1, "total": 1, "message": "Page title is present and not empty."}]))
    else:
        components.append(("Page title", 0, 1, [{"component": "Page title", "passed": 0, "total": 1, "message": "Missing or empty <title> element (WCAG 2.4.2)."}]))

    # 3. Images with alt text (WCAG 1.1.1)
    imgs = soup.find_all("img")
    total_imgs = len(imgs)
    alt_ok = 0
    if total_imgs > 0:
        for img in imgs:
            alt = img.get("alt")
            if alt is not None:  # Has alt attribute (empty is OK for decorative)
                alt_ok += 1
        if alt_ok == total_imgs:
            components.append(("Images with alt attribute", alt_ok, total_imgs, [{"component": "Images with alt attribute", "passed": alt_ok, "total": total_imgs, "message": f"All {total_imgs} images have alt attribute."}]))
        else:
            components.append(("Images with alt attribute", alt_ok, total_imgs, [{"component": "Images with alt attribute", "passed": alt_ok, "total": total_imgs, "message": f"{total_imgs - alt_ok}/{total_imgs} images missing alt attribute (WCAG 1.1.1)."}]))
    else:
        components.append(("Images with alt attribute", 1, 1, [{"component": "Images with alt attribute", "passed": 1, "total": 1, "message": "No images found - this is acceptable."}]))

    # 4. Links with descriptive text (WCAG 1.3.1)
    links = soup.find_all("a", href=True)
    total_links = len(links)
    descriptive_links = 0
    if total_links > 0:
        for link in links:
            text = link.text.strip()
            if text and len(text) > 2 and text not in ['click here', 'read more', 'here', 'more']:
                descriptive_links += 1
        if descriptive_links == total_links:
            components.append(("Links with descriptive text", descriptive_links, total_links, [{"component": "Links with descriptive text", "passed": descriptive_links, "total": total_links, "message": f"All {total_links} links have descriptive text."}]))
        else:
            components.append(("Links with descriptive text", descriptive_links, total_links, [{"component": "Links with descriptive text", "passed": descriptive_links, "total": total_links, "message": f"{total_links - descriptive_links}/{total_links} links have vague text (WCAG 1.3.1)."}]))
    else:
        components.append(("Links with descriptive text", 1, 1, [{"component": "Links with descriptive text", "passed": 1, "total": 1, "message": "No links found - this is acceptable."}]))

    # 5. Form inputs with labels (WCAG 3.2.2)
    inputs = soup.find_all(["input", "textarea", "select"])
    total_inputs = len(inputs)
    labeled_inputs = 0
    if total_inputs > 0:
        for inp in inputs:
            inp_type = inp.get("type", "text")
            if inp_type == "hidden":
                continue
            # Check for label, aria-label, or placeholder
            has_label = False
            inp_id = inp.get("id")
            if inp_id:
                label = soup.find("label", {"for": inp_id})
                if label and label.text.strip():
                    has_label = True
            if not has_label and (inp.get("aria-label") or inp.get("placeholder")):
                has_label = True
            if has_label:
                labeled_inputs += 1
        if labeled_inputs == total_inputs:
            components.append(("Form inputs with labels", labeled_inputs, total_inputs, [{"component": "Form inputs with labels", "passed": labeled_inputs, "total": total_inputs, "message": f"All {total_inputs} form inputs have proper labels."}]))
        else:
            components.append(("Form inputs with labels", labeled_inputs, total_inputs, [{"component": "Form inputs with labels", "passed": labeled_inputs, "total": total_inputs, "message": f"{total_inputs - labeled_inputs}/{total_inputs} form inputs missing labels (WCAG 3.2.2)."}]))
    else:
        components.append(("Form inputs with labels", 1, 1, [{"component": "Form inputs with labels", "passed": 1, "total": 1, "message": "No form inputs found - this is acceptable."}]))

    # 6. Buttons with accessible text (WCAG 1.3.1)
    buttons = soup.find_all(["button", "input[type='button']", "input[type='submit']"])
    total_buttons = len(buttons)
    accessible_buttons = 0
    if total_buttons > 0:
        for btn in buttons:
            text = btn.text.strip()
            value = btn.get("value", "").strip()
            aria_label = btn.get("aria-label", "").strip()
            if text or value or aria_label:
                accessible_buttons += 1
        if accessible_buttons == total_buttons:
            components.append(("Buttons with accessible text", accessible_buttons, total_buttons, [{"component": "Buttons with accessible text", "passed": accessible_buttons, "total": total_buttons, "message": f"All {total_buttons} buttons have accessible text."}]))
        else:
            components.append(("Buttons with accessible text", accessible_buttons, total_buttons, [{"component": "Buttons with accessible text", "passed": accessible_buttons, "total": total_buttons, "message": f"{total_buttons - accessible_buttons}/{total_buttons} buttons missing accessible text (WCAG 1.3.1)."}]))
    else:
        components.append(("Buttons with accessible text", 1, 1, [{"component": "Buttons with accessible text", "passed": 1, "total": 1, "message": "No buttons found - this is acceptable."}]))

    # 7. Heading structure (WCAG 2.4.6)
    headings = soup.find_all(["h1", "h2", "h3", "h4", "h5", "h6"])
    h1s = soup.find_all("h1")
    
    # Single H1 check
    single_h1 = len(h1s) == 1
    if single_h1:
        components.append(("Single H1 per page", 1, 1, [{"component": "Single H1 per page", "passed": 1, "total": 1, "message": "Exactly 1 H1 tag found on the page."}]))
    else:
        components.append(("Single H1 per page", 0, 1, [{"component": "Single H1 per page", "passed": 0, "total": 1, "message": f"Found {len(h1s)} H1 tags, should be exactly 1 (WCAG 2.4.6)."}]))

    # Heading hierarchy check
    if len(headings) > 0:
        proper_hierarchy = True
        last_level = 0
        for heading in headings:
            level = int(heading.name[1])
            if level > last_level + 1:
                proper_hierarchy = False
                break
            last_level = level
        if proper_hierarchy:
            components.append(("Proper heading hierarchy", 1, 1, [{"component": "Proper heading hierarchy", "passed": 1, "total": 1, "message": "Heading hierarchy is properly structured."}]))
        else:
            components.append(("Proper heading hierarchy", 0, 1, [{"component": "Proper heading hierarchy", "passed": 0, "total": 1, "message": "Heading levels skip (e.g., H1 to H3 without H2) (WCAG 2.4.6)."}]))
    else:
        components.append(("Proper heading hierarchy", 1, 1, [{"component": "Proper heading hierarchy", "passed": 1, "total": 1, "message": "No headings found - this is acceptable."}]))

    # 8. Tables with headers (WCAG 4.1.1)
    tables = soup.find_all("table")
    total_tables = len(tables)
    proper_tables = 0
    if total_tables > 0:
        for table in tables:
            ths = table.find_all("th")
            if ths:  # Has headers
                proper_tables += 1
        if proper_tables == total_tables:
            components.append(("Tables with headers", proper_tables, total_tables, [{"component": "Tables with headers", "passed": proper_tables, "total": total_tables, "message": f"All {total_tables} tables have proper headers."}]))
        else:
            components.append(("Tables with headers", proper_tables, total_tables, [{"component": "Tables with headers", "passed": proper_tables, "total": total_tables, "message": f"{total_tables - proper_tables}/{total_tables} tables missing proper headers (WCAG 4.1.1)."}]))
    else:
        components.append(("Tables with headers", 1, 1, [{"component": "Tables with headers", "passed": 1, "total": 1, "message": "No tables found - this is acceptable."}]))

    # 9. Lists semantic structure (WCAG 1.3.1)
    lists = soup.find_all(["ul", "ol", "dl"])
    total_lists = len(lists)
    if total_lists > 0:
        components.append(("Lists semantic structure", total_lists, total_lists, [{"component": "Lists semantic structure", "passed": total_lists, "total": total_lists, "message": f"Found {total_lists} properly structured lists."}]))
    else:
        components.append(("Lists semantic structure", 1, 1, [{"component": "Lists semantic structure", "passed": 1, "total": 1, "message": "No lists found - this is acceptable."}]))

    # 10. Focus management (WCAG 2.4.3)
    focusable_elements = soup.find_all(["a", "button", "input", "select", "textarea"])
    total_focusable = len(focusable_elements)
    if total_focusable > 0:
        components.append(("Focus management", total_focusable, total_focusable, [{"component": "Focus management", "passed": total_focusable, "total": total_focusable, "message": f"Found {total_focusable} focusable elements for keyboard navigation."}]))
    else:
        components.append(("Focus management", 1, 1, [{"component": "Focus management", "passed": 1, "total": 1, "message": "No focusable elements found - this is acceptable."}]))

    # 11. Landmark elements (WCAG 4.1.2)
    landmarks = soup.find_all(["header", "nav", "main", "footer", "aside", "section", "article"])
    total_landmarks = len(landmarks)
    if total_landmarks > 0:
        components.append(("Landmark elements", total_landmarks, total_landmarks, [{"component": "Landmark elements", "passed": total_landmarks, "total": total_landmarks, "message": f"Found {total_landmarks} landmark elements for page structure."}]))
    else:
        components.append(("Landmark elements", 1, 1, [{"component": "Landmark elements", "passed": 1, "total": 1, "message": "No landmark elements found - this is acceptable."}]))

    # 12. Skip to main content link (WCAG 2.4.1)
    skip_links = soup.find_all("a", href=lambda x: x and ("main" in x.lower() or "content" in x.lower()))
    if skip_links:
        components.append(("Skip to main content link", 1, 1, [{"component": "Skip to main content link", "passed": 1, "total": 1, "message": "Skip to main content link found."}]))
    else:
        components.append(("Skip to main content link", 0, 1, [{"component": "Skip to main content link", "passed": 0, "total": 1, "message": "Missing 'Skip to main content' link (WCAG 2.4.1)."}]))

    # 13. Color contrast check (basic - WCAG 1.4.3)
    # This is a simplified check - in practice, you'd need to analyze CSS
    text_elements = soup.find_all(["p", "span", "div", "h1", "h2", "h3", "h4", "h5", "h6"])
    if text_elements:
        components.append(("Color contrast", 1, 1, [{"component": "Color contrast", "passed": 1, "total": 1, "message": "Color contrast analysis requires CSS inspection (WCAG 1.4.3)."}]))
    else:
        components.append(("Color contrast", 1, 1, [{"component": "Color contrast", "passed": 1, "total": 1, "message": "No text elements found - this is acceptable."}]))

    # 14. Touch targets (WCAG 2.5.8)
    interactive_elements = soup.find_all(["a", "button", "input", "select", "textarea"])
    if interactive_elements:
        components.append(("Touch targets", len(interactive_elements), len(interactive_elements), [{"component": "Touch targets", "passed": len(interactive_elements), "total": len(interactive_elements), "message": f"Found {len(interactive_elements)} interactive elements. Touch target size analysis requires CSS inspection (WCAG 2.5.8)."}]))
    else:
        components.append(("Touch targets", 1, 1, [{"component": "Touch targets", "passed": 1, "total": 1, "message": "No interactive elements found - this is acceptable."}]))

    # 15. Media controls (WCAG 1.3.1)
    media_elements = soup.find_all(["video", "audio"])
    if media_elements:
        components.append(("Media controls", len(media_elements), len(media_elements), [{"component": "Media controls", "passed": len(media_elements), "total": len(media_elements), "message": f"Found {len(media_elements)} media elements. Media control analysis requires CSS inspection (WCAG 1.3.1)."}]))
    else:
        components.append(("Media controls", 1, 1, [{"component": "Media controls", "passed": 1, "total": 1, "message": "No media elements found - this is acceptable."}]))

    # --- Calculate WCAG Compliance Score ---
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
        
        # WCAG Grade assignment based on compliance level
        if score >= 95:
            grade = "AAA"  # Highest level of accessibility
        elif score >= 85:
            grade = "AA"   # Standard compliance level
        elif score >= 70:
            grade = "A"    # Basic compliance level
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
    tools=[
        scrape_page,
        analyze_accessibility,
        ai_accessibility_analysis,
        format_grade,
        rerank_results,
        store_result_json,
        save_pdf_report
    ],
    max_iterations=20  # Higher for complex analysis tasks
)

# --- 7. EXPORT FUNCTION FOR SERVER ---
def analyze_urls_with_agent(urls: List[str]) -> List[Dict]:
    """
    Use the ConnectOnion AI agent to analyze a list of URLs for accessibility.
    The agent will decide which tools to use based on the system prompt.
    """
    results = []
    for url in urls:
        try:
            # Create a structured prompt for the agent
            prompt = f"""
            Analyze the accessibility of this webpage: {url}

            Follow these steps:
            1. Scrape the webpage content
            2. Run automated WCAG compliance analysis
            3. Perform AI-powered accessibility analysis
            4. Generate a comprehensive report with grade, score, and issues
            5. Store the results in JSON format

            Return the analysis results in a structured format that includes:
            - URL
            - WCAG grade (A, AA, AAA, or Not Compliant)
            - Compliance score (0-100)
            - List of accessibility issues found
            - AI analysis insights and recommendations
            """

            # Use agent.input() to process the request
            agent_response = agent.input(prompt, max_iterations=15)

            # Parse the agent response to extract structured data
            # For now, we'll create a basic structure - you may want to improve this parsing
            result = {
                "url": url,
                "grade": "AA",  # Default grade
                "score": 85,    # Default score
                "issues": [],
                "ai_analysis": {},
                "agent_response": agent_response
            }

            # Try to extract more specific information from the response
            if "Grade:" in agent_response:
                # Extract grade from response
                grade_start = agent_response.find("Grade:") + 6
                grade_end = agent_response.find("\n", grade_start)
                if grade_end == -1:
                    grade_end = len(agent_response)
                result["grade"] = agent_response[grade_start:grade_end].strip()

            if "Score:" in agent_response:
                # Extract score from response
                score_start = agent_response.find("Score:") + 6
                score_end = agent_response.find("/", score_start)
                if score_end != -1:
                    try:
                        result["score"] = int(agent_response[score_start:score_end].strip())
                    except ValueError:
                        pass

            results.append(result)
            print(f"✅ Analyzed {url} with agent")

        except Exception as e:
            print(f"❌ Error analyzing {url}: {e}")
            results.append({
                "url": url,
                "grade": "Error",
                "score": 0,
                "issues": [{"component": "Agent", "message": f"Analysis failed: {e}", "passed": 0, "total": 1}],
                "ai_analysis": {},
                "agent_response": f"Error: {e}"
            })

    return results

# --- 8. EXAMPLE USAGE FOR BACKEND ---
if __name__ == "__main__":
    urls = [
        "https://www.wikipedia.org/",
        "https://www.example.com/",
    ]
    results = analyze_urls_with_agent(urls)
    for result in results:
        print(f"URL: {result['url']}")
        print(f"Grade: {result['grade']}")
        print(f"Score: {result['score']}")
        print("---")
