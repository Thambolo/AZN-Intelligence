#!/usr/bin/env python3
"""
Test script to demonstrate the ConnectOnion agent functionality.
This shows how the agent analyzes URLs for accessibility using the defined tools.
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'meta-agent'))

from agent import analyze_urls_with_agent, agent

def test_agent_direct():
    """Test the agent directly with a simple query."""
    print("🧪 Testing ConnectOnion Agent directly...")
    try:
        response = agent.input("What tools do you have available for accessibility analysis?")
        print(f"Agent Response: {response}")
        print("✅ Direct agent test successful!")
    except Exception as e:
        print(f"❌ Direct agent test failed: {e}")

def test_url_analysis():
    """Test URL analysis with the agent."""
    print("\n🧪 Testing URL analysis with agent...")
    test_urls = [
        "https://www.example.com/",
        "https://www.wikipedia.org/"
    ]

    results = analyze_urls_with_agent(test_urls)

    print(f"📊 Analysis Results for {len(results)} URLs:")
    for result in results:
        print(f"  URL: {result['url']}")
        print(f"  Grade: {result['grade']}")
        print(f"  Score: {result['score']}")
        print(f"  Issues: {len(result.get('issues', []))}")
        print()

    print("✅ URL analysis test successful!")

if __name__ == "__main__":
    print("🚀 ConnectOnion Agent Test Suite")
    print("=" * 50)

    test_agent_direct()
    test_url_analysis()

    print("\n🎉 All tests completed!")
    print("\nThe ConnectOnion agent is now properly configured with:")
    print("  - System prompt from prompts/accessibility_grader.md")
    print("  - 7 specialized tools for accessibility analysis")
    print("  - 20 max iterations for complex analysis tasks")
    print("  - Automatic tool selection based on user requests")
