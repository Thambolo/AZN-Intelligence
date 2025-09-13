"""
Rate limiter for OpenAI API calls to prevent rate limit errors.
Implements token-based and request-based rate limiting with automatic retries.
"""

import time
import threading
from typing import Dict, List, Optional
from datetime import datetime, timedelta
import asyncio


class OpenAIRateLimiter:
    """
    Rate limiter for OpenAI API calls.

    Handles both TPM (tokens per minute) and RPM (requests per minute) limits.
    Automatically adds delays and retries when limits are approached.
    """

    def __init__(self,
                 tpm_limit: int = 200000,  # Tokens per minute
                 rpm_limit: int = 1000,    # Requests per minute (conservative estimate)
                 safety_margin: float = 0.8,  # Use 80% of limit to be safe
                 max_retries: int = 3,
                 base_delay: float = 1.0):
        """
        Initialize the rate limiter.

        Args:
            tpm_limit: Maximum tokens per minute
            rpm_limit: Maximum requests per minute
            safety_margin: Fraction of limit to actually use (0.8 = 80%)
            max_retries: Maximum number of retries on rate limit errors
            base_delay: Base delay in seconds between requests
        """
        self.tpm_limit = int(tpm_limit * safety_margin)
        self.rpm_limit = int(rpm_limit * safety_margin)
        self.max_retries = max_retries
        self.base_delay = base_delay

        # Thread-safe storage for request tracking
        self._lock = threading.Lock()
        self.requests: List[Dict] = []  # [{'timestamp': datetime, 'tokens': int}]
        self.cleanup_interval = 60  # seconds

        # Start cleanup thread
        self._cleanup_thread = threading.Thread(target=self._cleanup_loop, daemon=True)
        self._cleanup_thread.start()

    def _cleanup_loop(self):
        """Background thread to clean up old request records."""
        while True:
            time.sleep(self.cleanup_interval)
            self._cleanup_old_requests()

    def _cleanup_old_requests(self):
        """Remove request records older than 1 minute."""
        cutoff = datetime.now() - timedelta(minutes=1)
        with self._lock:
            self.requests = [r for r in self.requests if r['timestamp'] > cutoff]

    def _get_current_usage(self) -> Dict[str, int]:
        """Get current usage in the last minute."""
        now = datetime.now()
        cutoff = now - timedelta(minutes=1)

        with self._lock:
            recent_requests = [r for r in self.requests if r['timestamp'] > cutoff]
            total_tokens = sum(r['tokens'] for r in recent_requests)
            total_requests = len(recent_requests)

        return {
            'tokens': total_tokens,
            'requests': total_requests
        }

    def _calculate_delay(self, estimated_tokens: int = 1000) -> float:
        """Calculate how long to wait before making the next request."""
        usage = self._get_current_usage()

        # Check TPM limit
        if usage['tokens'] + estimated_tokens > self.tpm_limit:
            tokens_over = (usage['tokens'] + estimated_tokens) - self.tpm_limit
            tpm_delay = (tokens_over / self.tpm_limit) * 60  # seconds to wait
        else:
            tpm_delay = 0

        # Check RPM limit
        if usage['requests'] + 1 > self.rpm_limit:
            rpm_delay = ((usage['requests'] + 1 - self.rpm_limit) / self.rpm_limit) * 60
        else:
            rpm_delay = 0

        # Return the maximum delay needed
        return max(tpm_delay, rpm_delay, self.base_delay)

    def _record_request(self, tokens_used: int):
        """Record a completed request."""
        with self._lock:
            self.requests.append({
                'timestamp': datetime.now(),
                'tokens': tokens_used
            })

    async def wait_if_needed(self, estimated_tokens: int = 1000):
        """Wait if necessary to stay within rate limits."""
        delay = self._calculate_delay(estimated_tokens)
        if delay > 0:
            print(f"⏳ Rate limiter: waiting {delay:.1f}s before next request")
            await asyncio.sleep(delay)

    def wait_if_needed_sync(self, estimated_tokens: int = 1000):
        """Synchronous version of wait_if_needed."""
        delay = self._calculate_delay(estimated_tokens)
        if delay > 0:
            print(f"⏳ Rate limiter: waiting {delay:.1f}s before next request")
            time.sleep(delay)

    def record_and_retry_on_error(self, func, *args, estimated_tokens: int = 1000, **kwargs):
        """
        Execute a function with automatic retries on rate limit errors.

        Args:
            func: The function to call (should be an OpenAI API call)
            estimated_tokens: Estimated tokens this call will use
            *args, **kwargs: Arguments to pass to the function

        Returns:
            The result of the function call
        """
        last_error = None

        for attempt in range(self.max_retries + 1):
            try:
                # Wait if needed before making the call
                self.wait_if_needed_sync(estimated_tokens)

                # Make the API call
                result = func(*args, **kwargs)

                # Record the successful request (estimate tokens used)
                self._record_request(estimated_tokens)

                return result

            except Exception as e:
                error_str = str(e).lower()
                last_error = e

                # Check if this is a rate limit error
                if any(keyword in error_str for keyword in ['rate limit', 'rate_limit', '429']):
                    if attempt < self.max_retries:
                        # Extract wait time from error if available
                        wait_time = self._extract_wait_time(str(e))
                        if wait_time:
                            print(f"🚦 Rate limit hit, waiting {wait_time:.1f}s (attempt {attempt + 1}/{self.max_retries + 1})")
                            time.sleep(wait_time)
                        else:
                            # Fallback to calculated delay
                            delay = self._calculate_delay(estimated_tokens)
                            print(f"🚦 Rate limit hit, waiting {delay:.1f}s (attempt {attempt + 1}/{self.max_retries + 1})")
                            time.sleep(delay)
                        continue
                    else:
                        print(f"❌ Rate limit error after {self.max_retries + 1} attempts: {e}")
                        raise e
                else:
                    # Not a rate limit error, re-raise immediately
                    raise e

        # This should never be reached, but just in case
        raise last_error

    async def record_and_retry_on_error_async(self, func, *args, estimated_tokens: int = 1000, **kwargs):
        """
        Async version of record_and_retry_on_error.
        """
        last_error = None

        for attempt in range(self.max_retries + 1):
            try:
                # Wait if needed before making the call
                await self.wait_if_needed(estimated_tokens)

                # Make the API call
                result = await func(*args, **kwargs)

                # Record the successful request (estimate tokens used)
                self._record_request(estimated_tokens)

                return result

            except Exception as e:
                error_str = str(e).lower()
                last_error = e

                # Check if this is a rate limit error
                if any(keyword in error_str for keyword in ['rate limit', 'rate_limit', '429']):
                    if attempt < self.max_retries:
                        # Extract wait time from error if available
                        wait_time = self._extract_wait_time(str(e))
                        if wait_time:
                            print(f"🚦 Rate limit hit, waiting {wait_time:.1f}s (attempt {attempt + 1}/{self.max_retries + 1})")
                            await asyncio.sleep(wait_time)
                        else:
                            # Fallback to calculated delay
                            delay = self._calculate_delay(estimated_tokens)
                            print(f"🚦 Rate limit hit, waiting {delay:.1f}s (attempt {attempt + 1}/{self.max_retries + 1})")
                            await asyncio.sleep(delay)
                        continue
                    else:
                        print(f"❌ Rate limit error after {self.max_retries + 1} attempts: {e}")
                        raise e
                else:
                    # Not a rate limit error, re-raise immediately
                    raise e

        # This should never be reached, but just in case
        raise last_error

    def _extract_wait_time(self, error_message: str) -> Optional[float]:
        """Extract wait time from OpenAI rate limit error message."""
        import re

        # Look for patterns like "Please try again in 552ms" or "Please try again in 1m30s"
        patterns = [
            r'Please try again in (\d+)ms',
            r'Please try again in (\d+)s',
            r'Please try again in (\d+)m(\d+)s',
        ]

        for pattern in patterns:
            match = re.search(pattern, error_message, re.IGNORECASE)
            if match:
                if 'ms' in pattern:
                    return float(match.group(1)) / 1000  # Convert ms to seconds
                elif 'm' in pattern and 's' in pattern:
                    minutes = int(match.group(1))
                    seconds = int(match.group(2))
                    return minutes * 60 + seconds
                else:
                    return float(match.group(1))

        return None

    def get_stats(self) -> Dict:
        """Get current rate limiter statistics."""
        usage = self._get_current_usage()
        return {
            'current_tpm_usage': usage['tokens'],
            'current_rpm_usage': usage['requests'],
            'tpm_limit': self.tpm_limit,
            'rpm_limit': self.rpm_limit,
            'tpm_remaining': max(0, self.tpm_limit - usage['tokens']),
            'rpm_remaining': max(0, self.rpm_limit - usage['requests']),
            'total_requests_tracked': len(self.requests)
        }


# Global rate limiter instance
rate_limiter = OpenAIRateLimiter(
    tpm_limit=200000,  # OpenAI's TPM limit
    rpm_limit=1000,    # Conservative RPM estimate
    safety_margin=0.8, # Use 80% of limits
    max_retries=3,
    base_delay=1.0     # 1 second base delay
)
