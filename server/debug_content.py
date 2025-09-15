#!/usr/bin/env python3

import requests
from bs4 import BeautifulSoup

def check_raw_content(url):
    """Check what HTML content we're actually getting"""
    print(f"\n{'='*60}")
    print(f"RAW HTML ANALYSIS: {url}")
    print(f"{'='*60}")
    
    try:
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
        
        session = requests.Session()
        session.headers.update(headers)
        
        response = session.get(url, timeout=10, allow_redirects=True)
        response.raise_for_status()
        
        print(f"📡 Response status: {response.status_code}")
        print(f"📏 Content length: {len(response.content)} bytes")
        print(f"🔤 Content type: {response.headers.get('content-type', 'Unknown')}")
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Check basic structure
        print(f"\n🔍 HTML STRUCTURE:")
        print(f"   Title tag: {soup.find('title')}")
        print(f"   Lang attribute: {soup.find('html', attrs={'lang': True})}")
        print(f"   Images: {len(soup.find_all('img'))}")
        print(f"   Links: {len(soup.find_all('a'))}")
        print(f"   Forms: {len(soup.find_all('form'))}")
        print(f"   Input elements: {len(soup.find_all('input'))}")
        print(f"   Buttons: {len(soup.find_all('button'))}")
        print(f"   Headings: {len(soup.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6']))}")
        
        # Show first 500 chars of body text
        body = soup.find('body')
        body_text = body.get_text(strip=True) if body else ""
        print(f"\n📝 BODY TEXT (first 500 chars):")
        print(f"   {repr(body_text[:500])}")
        
        # Check for JavaScript frameworks
        scripts = soup.find_all('script')
        js_frameworks = []
        for script in scripts:
            src = script.get('src', '')
            if any(fw in src.lower() for fw in ['react', 'vue', 'angular', 'next', 'gatsby']):
                js_frameworks.append(src)
        
        print(f"\n⚡ JAVASCRIPT FRAMEWORKS DETECTED:")
        if js_frameworks:
            for fw in js_frameworks[:5]:
                print(f"   - {fw}")
        else:
            print("   - None detected in script src attributes")
        
        # Check meta tags for framework clues
        meta_tags = soup.find_all('meta')
        print(f"\n🏷️ META TAGS (first 5):")
        for meta in meta_tags[:5]:
            name = meta.get('name', meta.get('property', 'unknown'))
            content = meta.get('content', '')
            print(f"   {name}: {content[:100]}")
        
    except Exception as e:
        print(f"❌ ERROR: {str(e)}")

if __name__ == "__main__":
    # Check the problematic sites
    test_urls = [
        "https://openai.com",
        "https://example.com"  # Compare with a static site
    ]
    
    for url in test_urls:
        check_raw_content(url)
