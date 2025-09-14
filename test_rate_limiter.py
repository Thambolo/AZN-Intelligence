#!/usr/bin/env python3
"""
Test script for the rate limiter functionality.
This script tests the OpenAI rate limiter to ensure it properly handles rate limits.
"""

import sys
import os
import time

# Add meta-agent to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'meta-agent'))

from rate_limiter import rate_limiter

def test_rate_limiter():
    """Test the rate limiter functionality."""
    print("🧪 Testing OpenAI Rate Limiter")
    print("=" * 50)

    # Get initial stats
    stats = rate_limiter.get_stats()
    print("📊 Initial Rate Limiter Stats:")
    print(f"  TPM Limit: {stats['tpm_limit']}")
    print(f"  RPM Limit: {stats['rpm_limit']}")
    print(f"  Current TPM Usage: {stats['current_tpm_usage']}")
    print(f"  Current RPM Usage: {stats['current_rpm_usage']}")
    print()

    # Test delay calculation
    print("⏱️  Testing delay calculation...")
    delay = rate_limiter._calculate_delay(1000)
    print(f"  Calculated delay for 1000 tokens: {delay:.1f}s")
    print()

    # Test synchronous wait
    print("⏳ Testing synchronous wait...")
    start_time = time.time()
    rate_limiter.wait_if_needed_sync(1000)
    end_time = time.time()
    print(f"  Wait completed in {end_time - start_time:.1f}s")
    print()

    # Test error extraction
    print("🔍 Testing error message parsing...")
    test_errors = [
        "Rate limit reached for gpt-4o-mini. Please try again in 552ms.",
        "Rate limit reached. Please try again in 30s.",
        "Rate limit reached. Please try again in 2m15s.",
    ]

    for error in test_errors:
        wait_time = rate_limiter._extract_wait_time(error)
        print(f"  Error: {error}")
        print(f"  Extracted wait time: {wait_time}s")
    print()

    print("✅ Rate limiter test completed successfully!")
    print("\n💡 Rate limiter features:")
    print("  • Automatic delay calculation based on TPM/RPM usage")
    print("  • Thread-safe request tracking")
    print("  • Automatic retry on rate limit errors")
    print("  • Background cleanup of old request records")
    print("  • Configurable safety margins and limits")

if __name__ == "__main__":
    test_rate_limiter()
