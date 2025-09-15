#!/usr/bin/env python3
"""
Test script to verify AI integration with PDF generation.
"""

import sys
import os

# Add the current directory to the path
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(current_dir)

from html_to_pdf_converter import generate_pdf_from_html_template

def test_ai_pdf_integration():
    """Test the AI-integrated PDF generation."""
    
    # Test data similar to what the analysis would produce
    test_analysis_result = {
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
    output_path = 'test_ai_integrated_report.pdf'
    
    print("🧪 Testing AI-integrated PDF generation...")
    print(f"📄 Template: {template_path}")
    print(f"📤 Output: {output_path}")
    print(f"🌐 Test URL: {test_analysis_result['url']}")
    print(f"📊 Test Score: {test_analysis_result['score']}%")
    
    try:
        success = generate_pdf_from_html_template(test_analysis_result, template_path, output_path)
        
        if success:
            print(f"✅ AI-integrated PDF generation successful!")
            print(f"📁 Generated: {output_path}")
            
            # Check if file exists and get size
            if os.path.exists(output_path):
                file_size = os.path.getsize(output_path)
                print(f"📏 File size: {file_size:,} bytes")
        else:
            print(f"❌ AI-integrated PDF generation failed")
            
    except Exception as e:
        print(f"❌ Error during test: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_ai_pdf_integration()
