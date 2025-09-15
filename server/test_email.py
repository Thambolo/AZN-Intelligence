#!/usr/bin/env python3
"""
Dynamic test script for the email report functionality.
Usage: python test_email.py <email> <url>
Example: python test_email.py evadtham1@gmail.com www.example.com
"""

import requests
import json
import sys
import os
import glob
import re
from datetime import datetime

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

def send_email_report(email: str, url: str):
    """Send email report via the API endpoint."""
    api_url = "http://localhost:8000/send-report"
    
    data = {
        "email": email,
        "url": url
    }
    
    print(f"📧 Sending report for '{url}' to '{email}'...")
    
    try:
        response = requests.post(api_url, json=data)
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Email sent successfully!")
            print(f"📁 Report file: {result.get('report_file', 'Unknown')}")
            print(f"📅 Report date: {result.get('report_date', 'Unknown')}")
            return True
        else:
            error_info = response.json()
            print("❌ Failed to send email")
            print(f"Error: {error_info.get('detail', 'Unknown error')}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("❌ Could not connect to server. Make sure the app is running on http://localhost:8000")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

def list_available_reports():
    """List all available PDF reports."""
    reports_dir = os.path.join(os.path.dirname(__file__), 'reports')
    if not os.path.exists(reports_dir):
        print("❌ Reports directory not found")
        return []
    
    pdf_files = glob.glob(os.path.join(reports_dir, "*.pdf"))
    if not pdf_files:
        print("❌ No PDF reports found in the reports directory")
        return []
    
    print(f"📁 Found {len(pdf_files)} report(s):")
    for pdf_file in sorted(pdf_files):
        filename = os.path.basename(pdf_file)
        # Extract datetime if possible
        datetime_match = re.search(r'_(\d{14})\.pdf$', filename)
        if datetime_match:
            datetime_str = datetime_match.group(1)
            try:
                file_datetime = datetime.strptime(datetime_str, '%Y%m%d%H%M%S')
                formatted_date = file_datetime.strftime('%Y-%m-%d %H:%M:%S UTC')
                print(f"  • {filename} (Generated: {formatted_date})")
            except ValueError:
                print(f"  • {filename}")
        else:
            print(f"  • {filename}")
    
    return pdf_files

def check_report_exists(url: str):
    """Check if a report exists for the given URL."""
    latest_report = find_latest_report(url)
    if latest_report:
        filename = os.path.basename(latest_report)
        print(f"✅ Report found for '{url}': {filename}")
        return True
    else:
        print(f"❌ No report found for '{url}'")
        return False

def main():
    print("📧 Dynamic Email Report Tester")
    print("=" * 50)
    
    # Check command line arguments
    if len(sys.argv) < 3:
        print("Usage: python test_email.py <email> <url>")
        print("Examples:")
        print("  python test_email.py evadtham1@gmail.com www.example.com")
        print("  python test_email.py user@domain.com https://www.google.com")
        print("\nAvailable reports:")
        list_available_reports()
        return
    
    email = sys.argv[1]
    url = sys.argv[2]
    
    # Clean up URL (remove protocol if present)
    clean_url = url.replace('https://', '').replace('http://', '')
    
    print(f"🎯 Target Email: {email}")
    print(f"🌐 Target URL: {clean_url}")
    print()
    
    # First check if a report exists
    print("1. Checking for existing reports...")
    if not check_report_exists(clean_url):
        print("\n💡 Tip: Make sure you have generated a report for this URL first using the /audit endpoint")
        print("Example: POST to http://localhost:8000/audit with {'urls': ['" + clean_url + "']}")
        return
    
    print("\n2. Sending email...")
    success = send_email_report(email, clean_url)
    
    if success:
        print("\n🎉 Test completed successfully!")
        print("Check your email inbox for the accessibility report.")
    else:
        print("\n❌ Test failed. Please check the error messages above.")

if __name__ == "__main__":
    main()
