#!/usr/bin/env python3
"""
Clean HTML-to-PDF converter that preserves the beautiful CSS styling from the template.
Uses weasyprint for proper CSS rendering, with fallback options.
"""

import os
import tempfile
from datetime import datetime

def generate_pdf_from_html_template(analysis_result, template_path, output_path):
    """
    Generate PDF from HTML template while preserving all CSS styling.
    
    Args:
        analysis_result: Dictionary containing analysis data
        template_path: Path to the HTML template file
        output_path: Path where PDF should be saved
        
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        # Read the HTML template
        with open(template_path, 'r', encoding='utf-8') as f:
            html_template = f.read()
        
        # Prepare data for template substitution
        template_data = prepare_template_data(analysis_result)
        
        # Substitute placeholders in template
        html_content = substitute_template_placeholders(html_template, template_data)
        
        # Try multiple PDF conversion methods - Playwright priority
        success = False
        
        # Method 1: Try playwright (excellent CSS support, handles async properly)
        if not success:
            success = convert_with_playwright(html_content, output_path)
        
        # Method 2: Try weasyprint (good CSS support, fallback)
        if not success:
            success = convert_with_weasyprint(html_content, output_path)
        
        # Method 3: Try pdfkit (wkhtmltopdf wrapper, last resort)
        if not success:
            success = convert_with_pdfkit(html_content, output_path)
        
        if success:
            print(f"✅ PDF generated successfully: {output_path}")
            return True
        else:
            print(f"❌ All PDF conversion methods failed: {output_path}")
            return False
            
    except Exception as e:
        print(f"❌ Error in PDF generation: {e}")
        import traceback
        traceback.print_exc()
        return False

def convert_with_weasyprint(html_content, output_path):
    """Convert HTML to PDF using WeasyPrint (best CSS support)."""
    try:
        import weasyprint
        from weasyprint import HTML, CSS
        from weasyprint.text.fonts import FontConfiguration
        
        print("🔄 Trying WeasyPrint conversion...")
        
        # Configure fonts
        font_config = FontConfiguration()
        
        # Add custom CSS to fix layout issues while preserving multi-page structure
        custom_css = CSS(string="""
            @page {
                size: A4;
                margin: 0;
            }
            
            /* Fix title styling - white background with purple text */
            html body .page .main-title,
            .main-title {
                background: white !important;
                background-color: white !important;
                color: #667eea !important;
                -webkit-background-clip: unset !important;
                -webkit-text-fill-color: #667eea !important;
                background-clip: unset !important;
                letter-spacing: 2px !important;
                word-spacing: 8px !important;
                font-size: 3.5rem !important;
                line-height: 1.2 !important;
                margin-bottom: 2rem !important;
                text-shadow: none !important;
                background-image: none !important;
            }
            
            .subtitle {
                font-size: 1.2rem !important;
                margin-bottom: 3rem !important;
                letter-spacing: 3px !important;
            }
            
            /* Ensure page breaks work correctly */
            .page-break {
                page-break-before: always !important;
            }
            
            /* Better page styling with proper padding */
            .page {
                box-shadow: none !important;
                margin: 0 !important;
                page-break-after: always !important;
            }
            
            .page:last-child {
                page-break-after: avoid !important;
            }
            
            /* Site info grid improvements */
            .site-info {
                display: grid !important;
                grid-template-columns: 1fr 1fr !important;
                gap: 1rem !important;
                padding: 1.5rem !important;
                margin: 1.5rem 0 2rem 0 !important;
                background: #f8fafc !important;
                border-radius: 12px !important;
            }
            
            .info-item {
                padding: 0.75rem !important;
                text-align: center !important;
            }
            
            .info-label {
                font-size: 0.8rem !important;
                font-weight: 600 !important;
                color: #718096 !important;
                text-transform: uppercase !important;
                letter-spacing: 1px !important;
                margin-bottom: 0.5rem !important;
                display: block !important;
            }
            
            .info-value {
                font-size: 1.3rem !important;
                font-weight: 700 !important;
                color: #2d3748 !important;
                line-height: 1.2 !important;
            }
            
            .url-value {
                font-size: 0.9rem !important;
                line-height: 1.3 !important;
                word-break: break-all !important;
                background: #667eea !important;
                color: white !important;
                padding: 0.75rem !important;
                border-radius: 6px !important;
                font-family: monospace !important;
            }
            
            /* Grade styling */
            .grade-aa {
                background: #48bb78 !important;
                color: white !important;
                padding: 0.5rem 1rem !important;
                border-radius: 6px !important;
                font-weight: 700 !important;
            }
            
            .grade-a {
                background: #ed8936 !important;
                color: white !important;
                padding: 0.5rem 1rem !important;
                border-radius: 6px !important;
                font-weight: 700 !important;
            }
            
            .grade-fail {
                background: #f56565 !important;
                color: white !important;
                padding: 0.5rem 1rem !important;
                border-radius: 6px !important;
                font-weight: 700 !important;
            }
            
            /* Section spacing */
            .section-title {
                margin-top: 4rem !important;
                margin-bottom: 2rem !important;
                font-size: 1.8rem !important;
                page-break-before: avoid !important;
                clear: both !important;
            }
            
            /* Special spacing for AI sections to prevent overlap */
            .section-title:contains("AI-Generated") {
                margin-top: 5rem !important;
                padding-top: 2rem !important;
            }
            
            .content-section {
                margin: 2rem 0 4rem 0 !important;
                padding: 2rem !important;
                page-break-inside: avoid !important;
            }
            
            /* AI feedback section specific spacing */
            .ai-feedback-section {
                margin-bottom: 4rem !important;
                padding-bottom: 3rem !important;
            }
            
            /* Table styling */
            .table-container {
                margin: 2rem 0 !important;
            }
            
            table {
                width: 100% !important;
                border-collapse: collapse !important;
                margin: 1rem 0 !important;
            }
            
            th, td {
                padding: 1rem !important;
                text-align: left !important;
                border-bottom: 1px solid #e2e8f0 !important;
                color: #2d3748 !important;
            }
            
            th {
                background: #f7fafc !important;
                font-weight: 600 !important;
                color: #2d3748 !important;
            }
            
            /* Fix table text colors */
            td {
                color: #2d3748 !important;
            }
            
            td strong {
                color: #1a202c !important;
            }
            
            /* Status cell styling */
            .status-cell {
                font-weight: 600 !important;
            }
            
            .status-pass {
                color: #38a169 !important;
            }
            
            .status-fail {
                color: #e53e3e !important;
            }
            
            /* Principle titles */
            .principle-title {
                font-size: 1.2rem !important;
                word-wrap: -0.5 !important;
                margin: 3rem 0 2rem 0 !important;
                padding: 1rem !important;
                border-left: 4px solid #667eea !important;
                background: #f7fafc !important;
                color: #2d3748 !important;
            }
            
            /* Ensure all text elements have proper color */
            .page * {
                color: #2d3748 !important;
            }
            
            /* Override specific elements that should have different colors */
            .grade-aa, .grade-a, .grade-fail {
                color: white !important;
            }
            
            .url-value {
                color: white !important;
            }
            
            /* Footer logo styling - purple text with white background */
            .footer-logo {
                background: white !important;
                background-color: white !important;
                color: #667eea !important;
                -webkit-text-fill-color: #667eea !important;
                padding: 0.2rem 0.5rem !important;
                border-radius: 4px !important;
                font-weight: 600 !important;
                background-image: none !important;
            }
        """)
        
        # Create WeasyPrint HTML object
        html_doc = HTML(string=html_content, base_url='.')
        
        # Generate PDF with custom CSS
        html_doc.write_pdf(output_path, stylesheets=[custom_css], font_config=font_config)
        
        print("✅ WeasyPrint conversion successful")
        return True
        
    except ImportError:
        print("⚠️ WeasyPrint not available")
        return False
    except Exception as e:
        print(f"❌ WeasyPrint conversion failed: {e}")
        return False

def convert_with_playwright(html_content, output_path):
    """Convert HTML to PDF using Playwright (good CSS support)."""
    try:
        import asyncio
        
        # Run the async playwright function in a new event loop
        try:
            # Try to get existing loop
            loop = asyncio.get_event_loop()
            if loop.is_running():
                # If we're in an async context, run in a thread
                import concurrent.futures
                with concurrent.futures.ThreadPoolExecutor() as executor:
                    future = executor.submit(asyncio.run, _playwright_convert_async(html_content, output_path))
                    return future.result()
            else:
                # Safe to run directly
                return asyncio.run(_playwright_convert_async(html_content, output_path))
        except RuntimeError:
            # No event loop, safe to create one
            return asyncio.run(_playwright_convert_async(html_content, output_path))
        
    except ImportError:
        print("⚠️ Playwright not available")
        return False
    except Exception as e:
        print(f"❌ Playwright conversion failed: {e}")
        return False

async def _playwright_convert_async(html_content, output_path):
    """Async helper for Playwright PDF conversion."""
    try:
        from playwright.async_api import async_playwright
        
        print("🔄 Trying Playwright conversion...")
        
        # Add custom CSS to fix positioning and title styling
        custom_css = """
        <style>
            body { margin: 0 !important; padding: 0 !important; }
            .page { margin: 0 !important; padding: 20mm !important; box-shadow: none !important; }
            .main-title { 
                background: white !important; 
                color: #667eea !important;
                -webkit-background-clip: unset !important;
                -webkit-text-fill-color: unset !important;
                background-clip: unset !important;
                text-shadow: none !important;
                letter-spacing: -2px !important;
                word-spacing: -5px !important;
            }
            .subtitle { margin-bottom: 4rem !important; }
            .section-title { margin-top: 4rem !important; margin-bottom: 2rem !important; page-break-before: avoid !important; }
            .content-section { 
                margin-top: 2rem !important; 
                margin-bottom: 4rem !important; 
                padding: 2rem !important; 
                page-break-inside: avoid !important;
            }
            .ai-feedback { margin-bottom: 3rem !important; padding-bottom: 2rem !important; }
            .recommendations li { margin: 1.5rem 0 !important; padding: 1.5rem !important; }
            .chart-container { margin-top: 2rem !important; margin-bottom: 3rem !important; padding: 2rem !important; }
        </style>
        """
        
        # Inject custom CSS into HTML
        html_with_fixes = html_content.replace('<head>', f'<head>{custom_css}')
        
        async with async_playwright() as p:
            browser = await p.chromium.launch()
            page = await browser.new_page()
            
            # Set content
            await page.set_content(html_with_fixes)
            
            # Generate PDF with proper settings
            await page.pdf(
                path=output_path,
                format='A4',
                margin={
                    'top': '0mm',
                    'bottom': '0mm',
                    'left': '0mm',
                    'right': '0mm'
                },
                print_background=True,  # Important for gradients and backgrounds
                display_header_footer=False
            )
            
            browser.close()
        
        print("✅ Playwright conversion successful")
        return True
        
    except ImportError:
        print("⚠️ Playwright not available")
        return False
    except Exception as e:
        print(f"❌ Playwright conversion failed: {e}")
        return False

def convert_with_pdfkit(html_content, output_path):
    """Convert HTML to PDF using pdfkit (wkhtmltopdf wrapper)."""
    try:
        import pdfkit
        
        print("🔄 Trying pdfkit conversion...")
        
        # Add custom CSS to fix positioning and title styling
        custom_css = """
        <style>
            body { margin: 0 !important; padding: 0 !important; }
            .page { margin: 0 !important; padding: 20mm !important; box-shadow: none !important; }
            .main-title { 
                background: white !important; 
                color: #667eea !important;
                -webkit-background-clip: unset !important;
                -webkit-text-fill-color: unset !important;
                background-clip: unset !important;
                text-shadow: none !important;
                letter-spacing: -2px !important;
                word-spacing: -5px !important;
                margin-bottom: 2rem !important;
            }
            .subtitle { margin-bottom: 4rem !important; }
            .section-title { margin-top: 4rem !important; margin-bottom: 2rem !important; page-break-before: avoid !important; }
            .content-section { 
                margin-top: 2rem !important; 
                margin-bottom: 4rem !important; 
                padding: 2rem !important; 
                page-break-inside: avoid !important;
            }
            .ai-feedback { margin-bottom: 3rem !important; padding-bottom: 2rem !important; }
            .recommendations li { margin: 1.5rem 0 !important; padding: 1.5rem !important; }
            .chart-container { margin-top: 2rem !important; margin-bottom: 3rem !important; padding: 2rem !important; }
        </style>
        """
        
        # Inject custom CSS into HTML
        html_with_fixes = html_content.replace('<head>', f'<head>{custom_css}')
        
        options = {
            'page-size': 'A4',
            'margin-top': '0mm',
            'margin-right': '0mm',
            'margin-bottom': '0mm',
            'margin-left': '0mm',
            'encoding': "UTF-8",
            'enable-local-file-access': None,
            'print-media-type': None,
            'no-outline': None,
            'disable-smart-shrinking': None,
            'enable-forms': None,
            'lowquality': False,
            'enable-javascript': None,
            'javascript-delay': 2000,
            'load-error-handling': 'ignore',
            'load-media-error-handling': 'ignore'
        }
        
        pdfkit.from_string(html_with_fixes, output_path, options=options)
        
        print("✅ pdfkit conversion successful")
        return True
        
    except ImportError:
        print("⚠️ pdfkit not available")
        return False
    except Exception as e:
        print(f"❌ pdfkit conversion failed: {e}")
        return False

def get_ai_feedback_and_recommendations(analysis_result):
    """
    Get AI-generated feedback and recommendations from the meta-agent.
    
    Args:
        analysis_result: Dictionary containing analysis data
        
    Returns:
        dict: Contains feedback and recommendations from AI agent
    """
    try:
        # Import the agent function
        import sys
        import os
        meta_agent_path = os.path.join(os.path.dirname(__file__), 'meta-agent')
        if meta_agent_path not in sys.path:
            sys.path.append(meta_agent_path)
        
        from agent import generate_feedback_and_recommendations
        
        print("🤖 Generating AI feedback and recommendations...")
        ai_content = generate_feedback_and_recommendations(analysis_result)
        print(f"✅ AI content generated successfully")
        
        return ai_content
        
    except Exception as e:
        print(f"❌ Error generating AI content: {e}")
        return {
            'feedback': f"Error generating AI feedback: {str(e)}",
            'recommendations': ['Unable to generate AI recommendations at this time.']
        }

def format_recommendations_as_html(recommendations):
    """
    Format AI recommendations as HTML list items.
    
    Args:
        recommendations: List of recommendation strings or single string
        
    Returns:
        str: HTML formatted recommendations
    """
    try:
        if isinstance(recommendations, str):
            # If it's a single string, try to split by common delimiters
            if '\n' in recommendations:
                recommendations = [r.strip() for r in recommendations.split('\n') if r.strip()]
            elif '. ' in recommendations:
                recommendations = [r.strip() + '.' for r in recommendations.split('. ') if r.strip()]
            else:
                recommendations = [recommendations]
        
        if not recommendations:
            return '<li>No specific recommendations available.</li>'
        
        html_items = []
        for rec in recommendations:
            if rec.strip():
                # Escape HTML and clean up the recommendation
                clean_rec = escape_html(rec.strip())
                # Remove bullet points or numbers if they exist
                clean_rec = clean_rec.lstrip('•-*123456789. ')
                html_items.append(f'<li>{clean_rec}</li>')
        
        return '\n          '.join(html_items) if html_items else '<li>No specific recommendations available.</li>'
        
    except Exception as e:
        print(f"❌ Error formatting recommendations: {e}")
        return f'<li>Error formatting recommendations: {str(e)}</li>'

def prepare_template_data(analysis_result):
    """Prepare data dictionary for template substitution with AI-generated content."""
    
    # Extract basic info
    url = analysis_result.get('url', 'Unknown URL')
    overall_grade = analysis_result.get('grade', 'Unknown')
    overall_score = str(analysis_result.get('score', 0))
    
    # Format timestamp
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')
    
    # Determine grade and score classes for styling
    grade_class = get_grade_class(overall_grade)
    score_class = get_score_class(int(overall_score) if overall_score.isdigit() else 0)
    compliance_level = get_compliance_level(overall_grade)
    
    # Extract principle data
    principle_scores = analysis_result.get('principle_scores', {})
    principle_grades = analysis_result.get('principle_grades', {})
    detailed_results = analysis_result.get('detailed_results', {})
    
    # Generate AI feedback and recommendations
    ai_content = get_ai_feedback_and_recommendations(analysis_result)
    
    # Prepare template data dictionary
    template_data = {
        'URL': url,
        'OVERALL_GRADE': overall_grade,
        'OVERALL_SCORE': overall_score,
        'TIMESTAMP': timestamp,
        'GRADE_CLASS': grade_class,
        'SCORE_CLASS': score_class,
        'COMPLIANCE_LEVEL': compliance_level,
        
        # AI-generated content
        'AI_FEEDBACK': ai_content.get('feedback', 'AI feedback unavailable'),
        'AI_RECOMMENDATIONS_HTML': format_recommendations_as_html(ai_content.get('recommendations', [])),
        
        # Principle 1 data
        'P1_GRADE': principle_grades.get('principle1_perceivable', 'Unknown'),
        'P1_SCORE': str(principle_scores.get('principle1_perceivable', 0)),
        'P1_GRADE_CLASS': get_grade_class(principle_grades.get('principle1_perceivable', '')),
        'P1_ISSUES_HTML': generate_issues_table_html(detailed_results.get('principle1', {})),
        
        # Principle 2 data
        'P2_GRADE': principle_grades.get('principle2_operable', 'Unknown'),
        'P2_SCORE': str(principle_scores.get('principle2_operable', 0)),
        'P2_GRADE_CLASS': get_grade_class(principle_grades.get('principle2_operable', '')),
        'P2_ISSUES_HTML': generate_issues_table_html(detailed_results.get('principle2', {})),
        
        # Principle 3 data
        'P3_GRADE': principle_grades.get('principle3_understandable', 'Unknown'),
        'P3_SCORE': str(principle_scores.get('principle3_understandable', 0)),
        'P3_GRADE_CLASS': get_grade_class(principle_grades.get('principle3_understandable', '')),
        'P3_ISSUES_HTML': generate_issues_table_html(detailed_results.get('principle3', {})),
        
        # Principle 4 data
        'P4_GRADE': principle_grades.get('principle4_robust', 'Unknown'),
        'P4_SCORE': str(principle_scores.get('principle4_robust', 0)),
        'P4_GRADE_CLASS': get_grade_class(principle_grades.get('principle4_robust', '')),
        'P4_ISSUES_HTML': generate_issues_table_html(detailed_results.get('principle4', {})),
    }
    
    return template_data

def get_grade_class(grade):
    """Get CSS class name for grade styling."""
    grade_str = str(grade).upper()
    if grade_str == 'AAA':
        return 'aaa'
    elif grade_str == 'AA':
        return 'aa'
    elif grade_str == 'A':
        return 'a'
    else:
        return 'fail'

def get_score_class(score):
    """Get CSS class name for score styling."""
    if score >= 80:
        return 'high'
    elif score >= 60:
        return 'medium'
    else:
        return 'low'

def get_compliance_level(grade):
    """Get compliance level description."""
    grade_str = str(grade).upper()
    if grade_str == 'AAA':
        return 'excellent'
    elif grade_str == 'AA':
        return 'good'
    elif grade_str == 'A':
        return 'basic'
    else:
        return 'poor'

def generate_issues_table_html(principle_data):
    """Generate HTML table rows for principle issues."""
    if not principle_data or 'issues' not in principle_data:
        return '<tr><td colspan="3" style="text-align: center; color: #718096;">No data available</td></tr>'
    
    html_rows = []
    issues = principle_data.get('issues', [])
    
    if not issues:
        return '<tr><td colspan="3" style="text-align: center; color: #718096;">No issues found</td></tr>'
    
    for issue in issues:
        component = issue.get('component', 'Unknown')
        message = issue.get('message', 'No message')
        passed = issue.get('passed', 0)
        total = issue.get('total', 1)
        
        # Determine status
        if passed == total and total > 0:
            status = f"✓ {passed}/{total}"
            status_class = "status-pass"
        elif passed == 1 and total == 1:
            status = "✓ Pass"
            status_class = "status-pass"
        elif str(message).upper() == 'N/A' or 'N/A' in str(message):
            status = "N/A"
            status_class = "status-pass"
        else:
            status = f"✗ {passed}/{total}"
            status_class = "status-fail"
        
        # Escape HTML characters in text
        component = escape_html(component)
        message = escape_html(message)
        
        row_html = f'''
        <tr>
            <td><strong>{component}</strong></td>
            <td>{message}</td>
            <td class="status-cell {status_class}">{status}</td>
        </tr>'''
        
        html_rows.append(row_html.strip())
    
    return '\n'.join(html_rows)

def escape_html(text):
    """Escape HTML special characters."""
    if not isinstance(text, str):
        text = str(text)
    return (text.replace('&', '&amp;')
               .replace('<', '&lt;')
               .replace('>', '&gt;')
               .replace('"', '&quot;')
               .replace("'", '&#x27;'))

def substitute_template_placeholders(html_template, template_data):
    """Replace template placeholders with actual data."""
    html_content = html_template
    
    for placeholder, value in template_data.items():
        html_content = html_content.replace(f'{{{{{placeholder}}}}}', str(value))
    
    return html_content

# Test function
if __name__ == "__main__":
    # Test data
    test_data = {
        'url': 'https://example.com',
        'grade': 'AA',
        'score': 85,
        'principle_scores': {
            'principle1_perceivable': 90,
            'principle2_operable': 85,
            'principle3_understandable': 80,
            'principle4_robust': 85
        },
        'principle_grades': {
            'principle1_perceivable': 'AA',
            'principle2_operable': 'AA',
            'principle3_understandable': 'A',
            'principle4_robust': 'AA'
        },
        'detailed_results': {
            'principle1': {
                'issues': [
                    {'component': 'Non-text Content', 'message': 'All images have alt text', 'passed': 1, 'total': 1},
                    {'component': 'Time-based Media', 'message': 'No media found', 'passed': 1, 'total': 1}
                ]
            },
            'principle2': {
                'issues': [
                    {'component': 'Keyboard Accessible', 'message': 'All interactive elements are keyboard accessible', 'passed': 1, 'total': 1},
                    {'component': 'No Seizures', 'message': 'No flashing content detected', 'passed': 1, 'total': 1}
                ]
            },
            'principle3': {
                'issues': [
                    {'component': 'Readable', 'message': 'Text is readable and understandable', 'passed': 1, 'total': 1},
                    {'component': 'Predictable', 'message': 'Website behavior is predictable', 'passed': 1, 'total': 1}
                ]
            },
            'principle4': {
                'issues': [
                    {'component': 'Compatible', 'message': 'Content is compatible with assistive technologies', 'passed': 1, 'total': 1},
                    {'component': 'Valid Code', 'message': 'HTML markup is valid', 'passed': 1, 'total': 1}
                ]
            }
        }
    }
    
    template_path = 'accessibility_report_template.html'
    output_path = 'test_html_to_pdf.pdf'
    
    success = generate_pdf_from_html_template(test_data, template_path, output_path)
    print(f"Test completed: {'Success' if success else 'Failed'}")
