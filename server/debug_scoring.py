#!/usr/bin/env python3

import sys
import os

# Add the auto-analyse directory to Python path
current_dir = os.path.dirname(__file__)
auto_analyse_dir = os.path.join(current_dir, 'auto-analyse')
sys.path.insert(0, auto_analyse_dir)

from web_analyser import comprehensive_analyse_url
import json

def detailed_analysis_debug(url):
    """Debug function to show detailed scoring breakdown"""
    print(f"\n{'='*60}")
    print(f"DETAILED ANALYSIS DEBUG: {url}")
    print(f"{'='*60}")
    
    result = comprehensive_analyse_url(url, timeout=15)
    
    if result.get('grade') == 'Error':
        print(f"❌ ERROR: {result.get('error', 'Unknown error')}")
        return
    
    print(f"🎯 OVERALL RESULT:")
    print(f"   Grade: {result['grade']}")
    print(f"   Score: {result['score']}")
    print(f"   SPA Detected: {result.get('spa_detected', 'Unknown')}")
    print(f"   Time: {result['analysis_time_seconds']}s")
    
    print(f"\n📊 PRINCIPLE SCORES:")
    principles = result.get('principle_scores', {})
    for principle, score in principles.items():
        print(f"   {principle}: {score}")
    
    print(f"\n🔍 WEIGHTED CALCULATION:")
    p1 = principles.get('principle1_perceivable', 0)
    p2 = principles.get('principle2_operable', 0)  
    p3 = principles.get('principle3_understandable', 0)
    p4 = principles.get('principle4_robust', 0)
    
    print(f"   P1 (35%): {p1} × 0.35 = {p1 * 0.35:.2f}")
    print(f"   P2 (35%): {p2} × 0.35 = {p2 * 0.35:.2f}")
    print(f"   P3 (15%): {p3} × 0.15 = {p3 * 0.15:.2f}")
    print(f"   P4 (15%): {p4} × 0.15 = {p4 * 0.15:.2f}")
    
    weighted = (p1 * 0.35) + (p2 * 0.35) + (p3 * 0.15) + (p4 * 0.15)
    print(f"   Total: {weighted:.2f} → {int(weighted)}")
    
    print(f"\n🔧 DETAILED ISSUES (first 10):")
    issues = result.get('all_issues', [])
    for i, issue in enumerate(issues[:10]):
        component = issue.get('component', 'Unknown')
        message = issue.get('message', 'No message')
        passed = issue.get('passed', 0)
        total = issue.get('total', 1)
        print(f"   {i+1}. {component}: {passed}/{total} - {message}")
    
    if len(issues) > 10:
        print(f"   ... and {len(issues) - 10} more issues")
    
    return result

if __name__ == "__main__":
    # Test the problematic sites that return 68
    test_urls = [
        "https://openai.com",
        "https://pydantic.dev", 
        "https://google.com",
        "https://example.com"  # Compare with a different score
    ]
    
    for url in test_urls:
        detailed_analysis_debug(url)
