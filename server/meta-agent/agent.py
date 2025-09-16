
from datetime import datetime

def save_pdf_report(url: str, analysis: dict, ai_result: dict, filename: str = None):
    """Save a comprehensive PDF report for developers with AI analysis and improvement suggestions."""
    if filename is None:
        safe_url = url.replace('https://', '').replace('http://', '').replace('/', '_').replace(':', '_').replace('.', '_').replace('?', '_').replace('&', '_').replace('=', '_').replace('-', '_').replace('#', '_')
        filename = f"accessibility_report_{safe_url}.pdf"
    
    print(f"🔍 DEBUG: save_pdf_report called with URL: {url}")
    print(f"🔍 DEBUG: Generated filename: {filename}")
    print(f"🔍 DEBUG: analysis keys: {list(analysis.keys()) if analysis else 'None'}")
    print(f"🔍 DEBUG: ai_result keys: {list(ai_result.keys()) if ai_result else 'None'}")
    
    try:
        # Create a new PDF document
        doc = fitz.open()
        page = doc.new_page()
        
        # Set up initial position and font
        y_position = 72  # Start 1 inch from top
        margin = 72  # 1 inch margins
        line_height = 20
        page_width = page.rect.width - 2 * margin
        
        def add_text(page, text, x, y, font_size=12, bold=False, color=(0, 0, 0)):
            """Add text to the page and return new y position"""
            fontname = "helv" if not bold else "helv"  # Use same font for now
            
            # Split text into lines that fit within page width
            words = text.split(' ')
            lines = []
            current_line = ""
            
            for word in words:
                test_line = current_line + (" " if current_line else "") + word
                text_width = fitz.get_text_length(test_line, fontsize=font_size)
                
                if text_width <= page_width:
                    current_line = test_line
                else:
                    if current_line:
                        lines.append(current_line)
                        current_line = word
                    else:
                        lines.append(word)  # Word is too long but we need to include it
            
            if current_line:
                lines.append(current_line)
            
            # Add each line to the page
            for line in lines:
                if y > page.rect.height - margin:  # Check if we need a new page
                    page = doc.new_page()
                    y = margin
                
                # Simple text insertion
                page.insert_text((x, y), line, fontsize=font_size, color=color)
                y += line_height
            
            return page, y
        
        # Title
        page, y_position = add_text(page, "WCAG Compliance Report", margin, y_position, 18, bold=True)
        page, y_position = add_text(page, "Developer Accessibility Analysis", margin, y_position + 5, 14, bold=True)
        y_position += 20
        
        # URL and timestamp
        page, y_position = add_text(page, f"Website: {url}", margin, y_position, 10)
        page, y_position = add_text(page, f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", margin, y_position, 10)
        y_position += 20
        
        # Executive Summary from AI
        if ai_result and 'summary' in ai_result:
            page, y_position = add_text(page, "EXECUTIVE SUMMARY", margin, y_position, 14, bold=True)
            y_position += 5
            page, y_position = add_text(page, ai_result['summary'], margin, y_position, 10)
            y_position += 15
        
        # Accessibility Issues - handle both 'violations' and 'issues' formats
        issues_to_display = []
        if analysis and 'violations' in analysis:
            # New format with violations
            violations = analysis['violations']
            page, y_position = add_text(page, f"ACCESSIBILITY VIOLATIONS ({len(violations)} found)", margin, y_position, 14, bold=True)
            y_position += 10
            
            for i, violation in enumerate(violations[:20], 1):  # Limit to 20 violations
                rule_id = violation.get('id', 'Unknown')
                description = violation.get('description', 'No description')
                impact = violation.get('impact', 'Unknown')
                
                page, y_position = add_text(page, f"{i}. {rule_id} (Impact: {impact})", margin, y_position, 11, bold=True)
                page, y_position = add_text(page, description, margin + 20, y_position, 10)
                
                # Add affected elements
                nodes = violation.get('nodes', [])
                if nodes:
                    page, y_position = add_text(page, f"Affected elements: {len(nodes)}", margin + 20, y_position, 9)
                    
                    # Show first few examples
                    for j, node in enumerate(nodes[:3]):
                        target = ', '.join(node.get('target', ['Unknown']))
                        page, y_position = add_text(page, f"- {target}", margin + 40, y_position, 9)
                
                y_position += 10
        elif analysis and 'issues' in analysis:
            # Current format with issues
            issues = analysis['issues']
            failed_issues = [issue for issue in issues if issue.get('passed', 0) < issue.get('total', 1)]
            page, y_position = add_text(page, f"ACCESSIBILITY ISSUES ({len(failed_issues)} found)", margin, y_position, 14, bold=True)
            y_position += 10
            
            if failed_issues:
                for i, issue in enumerate(failed_issues[:20], 1):  # Limit to 20 issues
                    component = issue.get('component', 'Unknown')
                    message = issue.get('message', 'No description')
                    passed = issue.get('passed', 0)
                    total = issue.get('total', 1)
                    
                    page, y_position = add_text(page, f"{i}. {component}", margin, y_position, 11, bold=True)
                    page, y_position = add_text(page, f"Issue: {message}", margin + 20, y_position, 10)
                    page, y_position = add_text(page, f"Status: {passed}/{total} passed", margin + 20, y_position, 9)
                    y_position += 10
            else:
                page, y_position = add_text(page, "No accessibility issues found!", margin, y_position, 10)
                y_position += 10
        
        # AI Recommendations - handle different AI result formats
        ai_recommendations = []
        if ai_result and 'ai_analysis' in ai_result and ai_result['ai_analysis']:
            ai_data = ai_result['ai_analysis']
            # Check for recommendations
            if 'recommendations' in ai_data:
                ai_recommendations = ai_data['recommendations']
            elif 'improvement_suggestions' in ai_data:
                ai_recommendations = ai_data['improvement_suggestions']
            elif 'critical_issues' in ai_data:
                ai_recommendations = ai_data['critical_issues']
        elif ai_result and 'recommendations' in ai_result:
            ai_recommendations = ai_result['recommendations']
        
        if ai_recommendations and isinstance(ai_recommendations, list):
            page, y_position = add_text(page, "AI RECOMMENDATIONS", margin, y_position, 14, bold=True)
            y_position += 10
            
            for i, rec in enumerate(ai_recommendations[:10], 1):  # Limit to 10 recommendations
                if isinstance(rec, dict):
                    title = rec.get('title', rec.get('issue', f'Recommendation {i}'))
                    description = rec.get('description', rec.get('developer_guidance', 'No description'))
                    priority = rec.get('priority', rec.get('fix_priority', 'Medium'))
                    
                    page, y_position = add_text(page, f"{i}. {title} (Priority: {priority})", margin, y_position, 11, bold=True)
                    page, y_position = add_text(page, description, margin + 20, y_position, 10)
                    y_position += 10
        elif ai_result and 'raw_feedback' in ai_result and ai_result['raw_feedback']:
            # Show raw AI feedback if structured data is not available
            page, y_position = add_text(page, "AI ANALYSIS", margin, y_position, 14, bold=True)
            y_position += 10
            feedback = ai_result['raw_feedback']
            if len(feedback) > 500:
                feedback = feedback[:500] + "..."
            page, y_position = add_text(page, feedback, margin, y_position, 10)
            y_position += 15
        
        # Performance Summary - handle both data formats
        if analysis:
            page, y_position = add_text(page, "SUMMARY STATISTICS", margin, y_position, 14, bold=True)
            y_position += 10
            
            # Handle new format with violations/passes/incomplete
            if 'violations' in analysis or 'passes' in analysis or 'incomplete' in analysis:
                total_violations = len(analysis.get('violations', []))
                total_passes = len(analysis.get('passes', []))
                total_incomplete = len(analysis.get('incomplete', []))
                
                page, y_position = add_text(page, f"Total Violations: {total_violations}", margin, y_position, 10)
                page, y_position = add_text(page, f"Passed Tests: {total_passes}", margin, y_position, 10)
                page, y_position = add_text(page, f"Incomplete Tests: {total_incomplete}", margin, y_position, 10)
            
            # Handle current format with grade/score/issues
            if 'grade' in analysis and 'score' in analysis:
                grade = analysis.get('grade', 'Unknown')
                score = analysis.get('score', 0)
                page, y_position = add_text(page, f"WCAG Grade: {grade}", margin, y_position, 10)
                page, y_position = add_text(page, f"Compliance Score: {score}/100", margin, y_position, 10)
            
            if 'issues' in analysis:
                issues = analysis['issues']
                total_issues = len(issues)
                failed_issues = len([issue for issue in issues if issue.get('passed', 0) < issue.get('total', 1)])
                passed_issues = total_issues - failed_issues
                
                page, y_position = add_text(page, f"Total Components Tested: {total_issues}", margin, y_position, 10)
                page, y_position = add_text(page, f"Components Passed: {passed_issues}", margin, y_position, 10)
                page, y_position = add_text(page, f"Components Failed: {failed_issues}", margin, y_position, 10)
        
        # Save the PDF
        doc.save(filename)
        doc.close()
        
        print(f"✅ PDF successfully generated: {filename}")
        return filename
        
    except Exception as e:
        print(f"❌ ERROR in PDF generation: {str(e)}")
        print(f"📄 Falling back to JSON report")
        
        # Fallback to JSON
        import json
        json_filename = filename.replace('.pdf', '.json') if filename.endswith('.pdf') else f"{filename}.json"
        
        report_data = {
            "url": url,
            "timestamp": datetime.now().isoformat(),
            "analysis": analysis,
            "ai_result": ai_result
        }
        
        with open(json_filename, 'w', encoding='utf-8') as f:
            json.dump(report_data, f, indent=2, ensure_ascii=False)
        
        print(f"📄 JSON report saved: {json_filename}")
        return json_filename
    
    # Footer
    pdf.ln(10)
    pdf.set_font("Times", 'I', 8)
    pdf.cell(0, 4, "Generated by AZN-Intelligence Accessibility Grader", new_x=XPos.LMARGIN, new_y=YPos.NEXT, align="C")
    pdf.cell(0, 4, "For developer accessibility optimization", new_x=XPos.LMARGIN, new_y=YPos.NEXT, align="C")
    
    pdf.output(filename)
    print(f"📄 Comprehensive PDF report saved to {filename}")
def ai_accessibility_analysis(html: str, url: str = "", automated_results: dict = None) -> dict:
    """Use AI to provide comprehensive WCAG analysis, developer-focused feedback, and improvement suggestions."""
    import os

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
import openai
import litellm

# Fix for O-series models that don't support temperature parameter
litellm.drop_params = True

load_dotenv()
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

def scrape_page(url: str) -> str:
    """Download the HTML content of a webpage."""
    try:
        headers = {'User-Agent': 'Mozilla/5.0 (compatible; AccessibilityGrader/1.0)'}
        r = requests.get(url, headers=headers, timeout=7)
        r.raise_for_status()
        return r.text
    except Exception as e:
        return f"Error: Could not fetch page at {url}: {e}"

def analyze_accessibility(html: str) -> Dict:
    """
    Analyze HTML for comprehensive WCAG compliance based on rules.md guidelines.
    Returns a dictionary: {'grade': 'A'|'AA'|'AAA', 'issues': [dict], 'score': int}
    """
    issues = []  # Will be a list of dicts: {component, message, passed, total}
    soup = BeautifulSoup(html, "html.parser")

    # WCAG Compliance Components
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

    # Calculate WCAG Compliance Score
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

def rerank_results(results: List[Tuple[str, str]]) -> List[Tuple[str, str]]:
    """
    Sort list of (url, grade) pairs by grade (AAA > AA > A > Not compliant).
    """
    grade_order = {"AAA": 3, "AA": 2, "A": 1, "Not WCAG compliant": 0}
    return sorted(results, key=lambda x: grade_order.get(x[1], 0), reverse=True)

def generate_accessibility_feedback(analysis_result: dict) -> str:
    """
    Generate a 150-word max feedback using ConnectOnion's llm_do function for faster execution.
    Uses a structured template prompt for consistent results.
    
    Expected analysis_result format:
    {
        "url": "https://example.com",
        "grade": "AA",
        "score": 85,
        "principle_scores": {
            "principle1_perceivable": 80,
            "principle2_operable": 85,
            "principle3_understandable": 90,
            "principle4_robust": 85
        },
        "spa_detected": false
    }
    """
    if not analysis_result or "principle_scores" not in analysis_result:
        return "Unable to generate feedback: Invalid analysis result provided."
    
    from connectonion import llm_do
    
    url = analysis_result.get("url", "the website")
    grade = analysis_result.get("grade", "Unknown")
    score = analysis_result.get("score", 0)
    principle_scores = analysis_result.get("principle_scores", {})
    spa_detected = analysis_result.get("spa_detected", False)
    
    # Create structured prompt for consistent feedback generation
    prompt = f"""Generate a concise accessibility feedback (maximum 150 words) for this WCAG analysis:

URL: {url}
Overall Grade: {grade}
Overall Score: {score}/100
SPA Detected: {spa_detected}

Principle Scores:
- Perceivable: {principle_scores.get('principle1_perceivable', 0)}/100
- Operable: {principle_scores.get('principle2_operable', 0)}/100  
- Understandable: {principle_scores.get('principle3_understandable', 0)}/100
- Robust: {principle_scores.get('principle4_robust', 0)}/100

Structure your feedback as follows:
1. Opening: Domain + overall assessment tone based on score
2. SPA note (if applicable): Mention analysis limitations for SPAs
3. Principle insights: Group principles by performance (strong 85+, good 70-84, weak <70)
4. Keep under 150 words total

Focus on being informative yet concise. Use professional accessibility consultant tone."""

    try:
        feedback = llm_do(prompt)
        # Ensure word limit
        words = feedback.split()
        if len(words) > 150:
            feedback = " ".join(words[:150]) + "..."
        return feedback
    except Exception as e:
        return f"Error generating feedback: {str(e)}"


def generate_accessibility_recommendations(analysis_result: dict) -> str:
    """
    Generate up to 5 specific recommendations using ConnectOnion's llm_do function.
    Uses structured prompting for consistent, actionable recommendations.
    
    Expected analysis_result format: Same as generate_accessibility_feedback()
    """
    if not analysis_result or "principle_scores" not in analysis_result:
        return "Unable to generate recommendations: Invalid analysis result provided."
    
    from connectonion import llm_do
    
    principle_scores = analysis_result.get("principle_scores", {})
    detailed_results = analysis_result.get("detailed_results", {})
    overall_score = analysis_result.get("score", 100)
    
    # Extract issues for context
    issues_context = ""
    for principle, data in detailed_results.items():
        if isinstance(data, dict) and "issues" in data:
            issues = data["issues"]
            if issues:
                issues_context += f"{principle}: {', '.join(map(str, issues[:3]))}\n"
    
    prompt = f"""Generate exactly 5 specific accessibility recommendations based on this WCAG analysis.

ANALYSIS DATA:
Overall Score: {overall_score}/100

Principle Scores:
- Principle 1 (Perceivable): {principle_scores.get('principle1_perceivable', 100)}/100
- Principle 2 (Operable): {principle_scores.get('principle2_operable', 100)}/100
- Principle 3 (Understandable): {principle_scores.get('principle3_understandable', 100)}/100
- Principle 4 (Robust): {principle_scores.get('principle4_robust', 100)}/100

Detected Issues:
{issues_context if issues_context else "No specific issues provided"}

REQUIREMENTS:
- Generate EXACTLY 5 numbered recommendations (1-5)
- Focus on lowest scoring principles first
- Be specific and actionable
- Include WCAG guideline references where relevant
- Only use information from the provided analysis data
- If no issues, provide general best practices

Format: Each recommendation on a new line, numbered 1-5."""

    try:
        recommendations = llm_do(prompt)
        return recommendations
    except Exception as e:
        return f"Error generating recommendations: {str(e)}"


# Agent Definition
agent = Agent(
    name="wcag_feedback_generator",
    system_prompt="You are an accessibility expert that generates concise feedback and actionable recommendations based strictly on WCAG analysis results. Only use information provided in the analysis data.",
    tools=[
        generate_accessibility_feedback,
        generate_accessibility_recommendations
    ],
    max_iterations=10
)

def analyze_urls_with_agent(urls: List[str]) -> List[Dict]:
    """
    Use the ConnectOnion AI agent to generate feedback and recommendations for accessibility analysis results.
    This function expects the analysis to be done separately using the auto-analyse tools.
    """
    # This function is now simplified - it's meant to work with pre-analyzed data
    # The actual analysis should be done using comprehensive_analyse_url from auto-analyse
    return []

def generate_feedback_and_recommendations(analysis_result: dict) -> dict:
    """
    Generate both feedback and recommendations using the ConnectOnion agent with optimized tool calls.
    Uses direct tool execution instead of agent.input() for much faster performance.
    
    Args:
        analysis_result (dict): The result from comprehensive_analyse_url containing WCAG analysis
        
    Returns:
        dict: Contains both feedback and recommendations
    """
    try:
        # Call the tools directly from the agent's tool map for maximum speed
        # This bypasses the LLM tool selection overhead
        feedback = agent.tool_map["generate_accessibility_feedback"](analysis_result)
        recommendations = agent.tool_map["generate_accessibility_recommendations"](analysis_result)
        
        return {
            "feedback": feedback,
            "recommendations": recommendations,
            "url": analysis_result.get("url", "Unknown"),
            "grade": analysis_result.get("grade", "Unknown"),
            "score": analysis_result.get("score", 0)
        }
        
    except Exception as e:
        return {
            "feedback": f"Error generating feedback: {str(e)}",
            "recommendations": f"Error generating recommendations: {str(e)}",
            "url": analysis_result.get("url", "Unknown"),
            "grade": "Error",
            "score": 0
        }


# Example usage function
def example_usage():
    """
    Example of how to use the new meta-agent with analysis results from auto-analyse.
    """
    # This would typically come from comprehensive_analyse_url
    sample_analysis = {
        "url": "https://example.com",
        "grade": "AA",
        "score": 82,
        "principle_scores": {
            "principle1_perceivable": 80,
            "principle2_operable": 85, 
            "principle3_understandable": 90,
            "principle4_robust": 75
        },
        "principle_grades": {
            "principle1_perceivable": "AA",
            "principle2_operable": "AA",
            "principle3_understandable": "AAA", 
            "principle4_robust": "A"
        },
        "detailed_results": {
            "principle1": {"issues": ["Missing alt text on 2 images"], "score": 80},
            "principle2": {"issues": ["Some buttons lack keyboard focus"], "score": 85},
            "principle3": {"issues": [], "score": 90},
            "principle4": {"issues": ["Minor HTML validation errors"], "score": 75}
        },
        "spa_detected": False
    }
    
    result = generate_feedback_and_recommendations(sample_analysis)
    print("Feedback:", result["feedback"])
    print("Recommendations:", result["recommendations"])


if __name__ == "__main__":
    # Example usage
    example_usage()
