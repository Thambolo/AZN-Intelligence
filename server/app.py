from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, EmailStr, HttpUrl
from typing import List, Optional
import sys
import os
import time
import glob
import re
from datetime import datetime
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication
import asyncio
import tempfile
import fitz  # PyMuPDF
from bs4 import BeautifulSoup

# Import template PDF generator
from html_to_pdf_converter import generate_pdf_from_html_template

# Import from meta-agent subdirectory
sys.path.append(os.path.join(os.path.dirname(__file__), 'meta-agent'))

from agent import analyze_urls_with_agent
from cache_manager import cache

sys.path.append(os.path.join(os.path.dirname(__file__), 'auto-analyse'))
from web_analyser import comprehensive_analyse_url

app = FastAPI(
    title="WCAG Accessibility Analyzer",
    description="API for analyzing website accessibility compliance with WCAG 2.2 guidelines",
    version="1.0.0"
)

# Add CORS middleware to handle cross-origin requests from Chrome extension
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for now (Chrome extensions need this)
    allow_credentials=False,  # Set to False when using allow_origins=["*"]
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=[
        "Accept",
        "Accept-Language", 
        "Content-Language",
        "Content-Type",
        "Authorization",
    ],
)

class AuditRequest(BaseModel):
    url: HttpUrl
    timeout: Optional[int] = 30

class EmailReportRequest(BaseModel):
    email: EmailStr
    url: str

def save_accessibility_report(analysis_result, reports_dir="reports"):
    """Save accessibility report as PDF and return the file path."""
    # Ensure reports directory exists
    os.makedirs(reports_dir, exist_ok=True)
    
    # Generate safe filename from URL
    url = analysis_result.get('url', 'unknown')
    safe_url = url.replace('https://', '').replace('http://', '')
    safe_url = safe_url.replace('.', '_').replace('/', '_').replace(':', '_').replace('?', '_').replace('&', '_').replace('=', '_').replace('-', '_')
    
    # Add timestamp to filename
    timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
    filename = f"accessibility_report_{safe_url}_{timestamp}.pdf"
    pdf_path = os.path.join(reports_dir, filename)
    
    try:
        # Generate PDF directly from template with proper CSS styling
        template_path = os.path.join(os.path.dirname(__file__), 'accessibility_report_template.html')
        
        if generate_pdf_from_html_template(analysis_result, template_path, pdf_path):
            print(f"✅ PDF report saved: {pdf_path}")
            return pdf_path
        else:
            print(f"❌ Failed to generate PDF: {pdf_path}")
            return None
            
    except Exception as e:
        print(f"❌ Error saving report: {e}")
        return None

def find_latest_report(url: str) -> str:
    """Find the latest PDF report for a given URL."""
    # Normalize URL for filename matching - convert ALL symbols to underscores
    safe_url = url.replace('https://', '').replace('http://', '')
    # Replace all common URL symbols with underscores
    safe_url = safe_url.replace('.', '_').replace('/', '_').replace(':', '_').replace('?', '_').replace('&', '_').replace('=', '_').replace('-', '_')
    
    # Pattern to match files: urlname_datetimestamputc.pdf
    reports_dir = os.path.join(os.path.dirname(__file__), 'reports')
    pattern = os.path.join(reports_dir, f"{safe_url}_*.pdf")
    
    matching_files = glob.glob(pattern)
    if not matching_files:
        return None
    
    # Extract datetime from filenames and find the latest
    latest_file = None
    latest_datetime = None
    
    for file_path in matching_files:
        filename = os.path.basename(file_path)
        # Extract datetime from filename: urlname_YYYYMMDDHHMMSS.pdf
        datetime_match = re.search(r'_(\d{14})\.pdf$', filename)
        if datetime_match:
            datetime_str = datetime_match.group(1)
            try:
                file_datetime = datetime.strptime(datetime_str, '%Y%m%d%H%M%S')
                if latest_datetime is None or file_datetime > latest_datetime:
                    latest_datetime = file_datetime
                    latest_file = file_path
            except ValueError:
                continue
    
    return latest_file

def send_email_with_pdf(email: str, url: str, pdf_path: str):
    """Send email with PDF attachment."""
    # Email configuration - you'll need to set these in your .env file
    smtp_server = os.getenv('SMTP_SERVER', 'smtp.gmail.com')
    smtp_port = int(os.getenv('SMTP_PORT', '587'))
    sender_email = os.getenv('SENDER_EMAIL')
    sender_password = os.getenv('SENDER_PASSWORD')
    
    if not sender_email or not sender_password:
        raise HTTPException(status_code=500, detail="Email configuration not set. Please configure SENDER_EMAIL and SENDER_PASSWORD.")
    
    # Create message with proper structure for HTML email
    msg = MIMEMultipart('mixed')  # For attachments
    msg['From'] = sender_email
    msg['To'] = email
    msg['Subject'] = f"🔍 Accessibility Report for {url}"
    
    # Create the email body part (HTML + plain text alternative)
    email_body = MIMEMultipart('alternative')
    
    # Create beautiful, mobile-friendly HTML email template
    html_body = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Accessibility Report</title>
        <style>
            @media only screen and (max-width: 600px) {{
                .container {{ width: 100% !important; margin: 0 !important; }}
                .content {{ padding: 20px !important; }}
                .header {{ padding: 30px 20px !important; }}
                .footer {{ padding: 20px !important; }}
                .feature-box {{ margin-bottom: 15px !important; }}
                h1 {{ font-size: 24px !important; }}
                h2 {{ font-size: 18px !important; }}
                h3 {{ font-size: 16px !important; }}
            }}
        </style>
    </head>
    <body style="margin: 0; padding: 0; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif; background-color: #f5f7fa; line-height: 1.6;">
        <!-- Outer wrapper for email clients -->
        <table role="presentation" cellspacing="0" cellpadding="0" border="0" width="100%" style="background-color: #f5f7fa;">
            <tr>
                <td align="center" style="padding: 20px 0;">
                    <!-- Main container -->
                    <div class="container" style="max-width: 600px; margin: 0 auto; background-color: #ffffff; border-radius: 12px; overflow: hidden; box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);">
                        
                        <!-- Header Section -->
                        <div class="header" style="background-color: #1e293b; padding: 40px 30px; text-align: center; border-bottom: 4px solid #3b82f6;">
                            <div style="font-size: 48px; margin-bottom: 16px;">🔍</div>
                            <h1 style="margin: 0 0 8px 0; font-size: 28px; font-weight: bold; color: #ffffff !important;">
                                Accessibility Analysis Complete
                            </h1>
                            <p style="margin: 0; font-size: 16px; color: #cbd5e1 !important;">
                                Professional Website Accessibility Report
                            </p>
                        </div>
                        
                        <!-- Main Content -->
                        <div class="content" style="padding: 40px 30px;">
                            
                            <!-- Website Info Box -->
                            <div style="background: linear-gradient(135deg, #eff6ff 0%, #f0f9ff 100%); border: 2px solid #3b82f6; border-radius: 12px; padding: 24px; margin-bottom: 32px; text-align: center;">
                                <h2 style="color: #1e40af; margin: 0 0 12px 0; font-size: 20px; font-weight: 600; display: flex; align-items: center; justify-content: center; gap: 8px;">
                                    <span>🌐</span> Website Analyzed
                                </h2>
                                <div style="background-color: #ffffff; border: 1px solid #cbd5e1; border-radius: 8px; padding: 16px; font-family: 'SF Mono', Monaco, Consolas, monospace; font-size: 16px; color: #374151; font-weight: 500; word-break: break-all;">
                                    {url}
                                </div>
                            </div>
                            
                            <!-- Features Section -->
                            <h2 style="color: #1f2937; margin: 0 0 24px 0; font-size: 22px; font-weight: 700; text-align: center;">
                                📋 What's Included in Your Report
                            </h2>
                            
                            <div style="margin-bottom: 32px;">
                                
                                <!-- Feature 1 -->
                                <div class="feature-box" style="background-color: #f8fafc; border-left: 4px solid #10b981; border-radius: 0 8px 8px 0; padding: 20px; margin-bottom: 20px; transition: all 0.3s ease;">
                                    <div style="display: flex; align-items: flex-start; gap: 12px;">
                                        <div style="font-size: 20px; line-height: 1;">✅</div>
                                        <div style="flex: 1;">
                                            <h3 style="color: #047857; margin: 0 0 8px 0; font-size: 18px; font-weight: 600;">
                                                WCAG 2.1 Compliance Analysis
                                            </h3>
                                            <p style="color: #4b5563; margin: 0; font-size: 15px; line-height: 1.5;">
                                                Comprehensive assessment against Web Content Accessibility Guidelines with detailed scoring and recommendations.
                                            </p>
                                        </div>
                                    </div>
                                </div>
                                
                                <!-- Feature 2 -->
                                <div class="feature-box" style="background-color: #fef7ff; border-left: 4px solid #a855f7; border-radius: 0 8px 8px 0; padding: 20px; margin-bottom: 20px;">
                                    <div style="display: flex; align-items: flex-start; gap: 12px;">
                                        <div style="font-size: 20px; line-height: 1;">🤖</div>
                                        <div style="flex: 1;">
                                            <h3 style="color: #7c2d92; margin: 0 0 8px 0; font-size: 18px; font-weight: 600;">
                                                AI-Powered Recommendations
                                            </h3>
                                            <p style="color: #4b5563; margin: 0; font-size: 15px; line-height: 1.5;">
                                                Smart, actionable suggestions powered by advanced AI to improve accessibility and enhance user experience.
                                            </p>
                                        </div>
                                    </div>
                                </div>
                                
                                <!-- Feature 3 -->
                                <div class="feature-box" style="background-color: #fff7ed; border-left: 4px solid #f59e0b; border-radius: 0 8px 8px 0; padding: 20px; margin-bottom: 20px;">
                                    <div style="display: flex; align-items: flex-start; gap: 12px;">
                                        <div style="font-size: 20px; line-height: 1;">🎯</div>
                                        <div style="flex: 1;">
                                            <h3 style="color: #d97706; margin: 0 0 8px 0; font-size: 18px; font-weight: 600;">
                                                Priority-Based Action Items
                                            </h3>
                                            <p style="color: #4b5563; margin: 0; font-size: 15px; line-height: 1.5;">
                                                Issues categorized by severity with clear, step-by-step resolution guides for efficient implementation.
                                            </p>
                                        </div>
                                    </div>
                                </div>
                                
                                <!-- Feature 4 -->
                                <div class="feature-box" style="background-color: #ecfdf5; border-left: 4px solid #06b6d4; border-radius: 0 8px 8px 0; padding: 20px; margin-bottom: 20px;">
                                    <div style="display: flex; align-items: flex-start; gap: 12px;">
                                        <div style="font-size: 20px; line-height: 1;">📊</div>
                                        <div style="flex: 1;">
                                            <h3 style="color: #0891b2; margin: 0 0 8px 0; font-size: 18px; font-weight: 600;">
                                                Detailed Compliance Metrics
                                            </h3>
                                            <p style="color: #4b5563; margin: 0; font-size: 15px; line-height: 1.5;">
                                                Quantified results with progress tracking capabilities and benchmark comparisons for measurable improvements.
                                            </p>
                                        </div>
                                    </div>
                                </div>
                            </div>
                            
                            <!-- Attachment Notice -->
                            <div style="background: linear-gradient(135deg, #fef3c7 0%, #fde68a 100%); border: 2px solid #f59e0b; border-radius: 12px; padding: 24px; margin-bottom: 32px; text-align: center;">
                                <div style="font-size: 32px; margin-bottom: 12px;">📎</div>
                                <h3 style="color: #92400e; margin: 0 0 8px 0; font-size: 20px; font-weight: 600;">
                                    Complete Report Attached
                                </h3>
                                <p style="color: #a16207; margin: 0; font-size: 15px; line-height: 1.4;">
                                    Your comprehensive accessibility analysis is attached as a professional PDF document
                                </p>
                            </div>
                            
                            <!-- Call to Action -->
                            <div style="text-align: center; padding: 24px; background-color: #f9fafb; border-radius: 12px; border: 1px solid #e5e7eb;">
                                <h3 style="color: #374151; margin: 0 0 12px 0; font-size: 18px; font-weight: 600;">
                                    Need Implementation Support?
                                </h3>
                                <p style="color: #6b7280; font-size: 15px; line-height: 1.5; margin: 0; max-width: 400px; margin: 0 auto;">
                                    Our accessibility experts are ready to help you create a more inclusive web experience for all users.
                                </p>
                            </div>
                        </div>
                        
                        <!-- Footer -->
                        <div class="footer" style="background-color: #1f2937; padding: 32px 30px; text-align: center; color: white;">
                            <div style="margin-bottom: 20px;">
                                <h3 style="color: #ffffff; margin: 0 0 8px 0; font-size: 22px; font-weight: 700; letter-spacing: -0.5px;">
                                    AZN Intelligence
                                </h3>
                                <p style="color: #9ca3af; margin: 0; font-size: 15px; font-weight: 400;">
                                    Advanced Accessibility Analysis & Web Intelligence
                                </p>
                            </div>
                            
                            <div style="border-top: 1px solid #374151; padding-top: 20px; margin-top: 20px;">
                                <p style="color: #9ca3af; margin: 0 0 12px 0; font-size: 13px; line-height: 1.5;">
                                    This report was generated by our AI-powered accessibility analysis system.<br>
                                    Questions? We're here to help you succeed.
                                </p>
                                <p style="color: #6b7280; margin: 0; font-size: 12px;">
                                    © 2025 AZN Intelligence • Making the web accessible for everyone
                                </p>
                            </div>
                        </div>
                        
                    </div>
                </td>
            </tr>
        </table>
    </body>
    </html>
    """
    
    # Plain text fallback for email clients that don't support HTML
    text_body = f"""
    ACCESSIBILITY REPORT FOR {url}
    ================================
    
    Hello,
    
    Your comprehensive accessibility analysis is complete! 
    
    📊 ANALYSIS SUMMARY:
    • WCAG 2.1 Compliance Assessment
    • AI-Powered Improvement Recommendations  
    • Priority-Based Action Items
    • Detailed Compliance Metrics
    
    📎 The complete report is attached as a PDF document.
    
    WHAT'S INCLUDED:
    ✅ Comprehensive assessment against Web Content Accessibility Guidelines
    🤖 Smart suggestions for improving accessibility and user experience
    🎯 Categorized issues with clear steps for resolution
    📊 Quantified results with progress tracking capabilities
    
    Need help implementing these improvements? Our accessibility experts are here to help you create a more inclusive web experience.
    
    Best regards,
    AZN Intelligence - Advanced Accessibility Analysis & Web Intelligence
    
    ---
    This report was generated by our AI-powered accessibility analysis system.
    © 2025 AZN Intelligence. Making the web accessible for everyone.
    """
    
    # Add text and HTML versions to the email body part
    email_body.attach(MIMEText(text_body, 'plain'))
    email_body.attach(MIMEText(html_body, 'html'))
    
    # Attach the email body to the main message
    msg.attach(email_body)
    
    # Attach PDF
    try:
        with open(pdf_path, 'rb') as f:
            pdf_attachment = MIMEApplication(f.read(), _subtype='pdf')
            pdf_filename = os.path.basename(pdf_path)
            pdf_attachment.add_header('Content-Disposition', 'attachment', filename=pdf_filename)
            msg.attach(pdf_attachment)
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="PDF report not found")
    
    # Send email
    try:
        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls()
        server.login(sender_email, sender_password)
        server.sendmail(sender_email, email, msg.as_string())
        server.quit()
        return True
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to send email: {str(e)}")

@app.post("/send-report")
async def send_accessibility_report(request: EmailReportRequest):
    """Send the latest accessibility report for a URL to the specified email."""
    try:
        # # Find the latest PDF report for the URL
        # latest_pdf = find_latest_report(request.url)
        
        # if not latest_pdf:
        #     raise HTTPException(
        #         status_code=404, 
        #         detail=f"No accessibility report found for URL: {request.url}"
        #     )

        # Generate a fresh report for the URL
        analysis_result = await comprehensive_analyse_url(str(request.url), timeout=30)
        latest_pdf = save_accessibility_report(analysis_result)
        if not latest_pdf:
            raise HTTPException(
                status_code=500, 
                detail=f"Failed to generate accessibility report for URL: {request.url}"
            ) 
        
        # Send email with PDF
        send_email_with_pdf(request.email, request.url, latest_pdf)
        
        # Get report info for response
        pdf_filename = os.path.basename(latest_pdf)
        datetime_match = re.search(r'_(\d{14})\.pdf$', pdf_filename)
        report_date = "Unknown"
        if datetime_match:
            datetime_str = datetime_match.group(1)
            try:
                report_datetime = datetime.strptime(datetime_str, '%Y%m%d%H%M%S')
                report_date = report_datetime.strftime('%Y-%m-%d %H:%M:%S UTC')
            except ValueError:
                pass
        
        return {
            "message": "Report sent successfully",
            "email": request.email,
            "url": request.url,
            "report_file": pdf_filename,
            "report_date": report_date
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")

@app.post("/audit")
async def audit_single_url(request: AuditRequest):
    """
    Audit a single URL for WCAG accessibility compliance.
    
    This endpoint analyzes a website against WCAG 2.2 Principles 1 (Perceivable) 
    and 2 (Operable) and returns a comprehensive accessibility report.
    
    - **url**: The website URL to analyze
    - **timeout**: Request timeout in seconds (default: 30)
    """
    url = str(request.url)
    timeout = request.timeout
    
    print(f"📥 Received audit request for URL: {url}")
    
    try:
        # Run the analysis asynchronously to support concurrent requests
        start_time = time.time()
        
        # Use asyncio.get_event_loop().run_in_executor to run the sync function in a thread pool
        loop = asyncio.get_event_loop()
        result = await loop.run_in_executor(
            None, 
            comprehensive_analyse_url,
            url, 
            timeout
        )
        
        end_time = time.time()
        analysis_time = end_time - start_time
        print("🚀 Analysis finished", result)


        print(f"⏱️ WCAG analysis completed for {url} in {analysis_time:.2f} seconds")
        print(f"📊 Result: Grade {result.get('grade', 'Unknown')}, Score {result.get('score', 0)}/100")
        
        # Add timing and URL info to the result
        result["url"] = url
        result["analysis_time_seconds"] = round(analysis_time, 2)
        result["timestamp"] = int(time.time())
        
        # # Generate and save PDF report
        # try:
        #     pdf_path = save_accessibility_report(result)
        #     if pdf_path:
        #         result["pdf_generated"] = True
        #         result["pdf_path"] = pdf_path
        #         print(f"📄 PDF report generated: {pdf_path}")
        #     else:
        #         result["pdf_generated"] = False
        #         print("⚠️ PDF generation failed, but analysis completed successfully")
        # except Exception as pdf_error:
        #     print(f"⚠️ PDF generation error: {pdf_error}")
        #     result["pdf_generated"] = False
        
        return {
            "success": True,
            "result": result
        }
        
    except Exception as e:
        print(f"❌ Error analyzing {url}: {e}")
        
        error_result = {
            "url": url,
            "grade": "Error",
            "score": 0,
            "issues": [
                {
                    "component": "Analysis Error", 
                    "message": f"Analysis failed: {str(e)}", 
                    "passed": 0, 
                    "total": 1
                }
            ],
            "error": str(e),
            "timestamp": int(time.time())
        }
        
        return {
            "success": False,
            "result": error_result
        }

@app.get("/health")
async def health_check():
    """Health check endpoint to verify the service is running."""
    return {
        "status": "healthy",
        "service": "WCAG Accessibility Analyzer",
        "version": "1.0.0",
        "timestamp": int(time.time())
    }

@app.get("/")
async def root():
    """Root endpoint with API information."""
    return {
        "message": "WCAG Accessibility Analyzer API",
        "description": "Analyze websites for WCAG 2.2 accessibility compliance",
        "endpoints": {
            "audit": "POST /audit - Analyze a single URL for accessibility",
            "health": "GET /health - Health check",
            "docs": "GET /docs - Interactive API documentation"
        },
        "supported_principles": [
            "WCAG 2.2 Principle 1: Perceivable",
            "WCAG 2.2 Principle 2: Operable"
        ]
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
