"""
Persistent storage utility for accessibility analysis results.
Uses JSON files to store and retrieve cached analysis data.
"""

import json
import os
from typing import Dict, Optional
from datetime import datetime, timedelta
from pathlib import Path

class PersistentCache:
    """Thread-safe persistent cache using JSON files."""

    def __init__(self, cache_dir: str = "cache", cache_file: str = "accessibility_cache.json", max_age_days: int = 7):
        self.cache_dir = Path(cache_dir)
        self.cache_file = self.cache_dir / cache_file
        self.max_age_days = max_age_days
        self._cache: Dict[str, Dict] = {}

        # Create cache directory if it doesn't exist
        self.cache_dir.mkdir(exist_ok=True)

        # Load existing cache
        self._load_cache()

    def _load_cache(self) -> None:
        """Load cache from JSON file."""
        try:
            if self.cache_file.exists():
                with open(self.cache_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    # Clean expired entries
                    self._cache = self._clean_expired_entries(data)
                    print(f"📂 Loaded {len(self._cache)} cached results from {self.cache_file}")
            else:
                self._cache = {}
                print(f"📂 Created new cache file: {self.cache_file}")
        except Exception as e:
            print(f"⚠️  Error loading cache: {e}")
            self._cache = {}

    def _save_cache(self) -> None:
        """Save cache to JSON file."""
        try:
            with open(self.cache_file, 'w', encoding='utf-8') as f:
                json.dump(self._cache, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"⚠️  Error saving cache: {e}")

    def _clean_expired_entries(self, cache_data: Dict[str, Dict]) -> Dict[str, Dict]:
        """Remove expired cache entries."""
        cleaned_cache = {}
        now = datetime.now()

        for url, data in cache_data.items():
            if 'timestamp' in data:
                try:
                    timestamp = datetime.fromisoformat(data['timestamp'])
                    if now - timestamp < timedelta(days=self.max_age_days):
                        cleaned_cache[url] = data
                except (ValueError, TypeError):
                    # If timestamp is invalid, keep the entry
                    cleaned_cache[url] = data
            else:
                # If no timestamp, keep the entry
                cleaned_cache[url] = data

        return cleaned_cache

    def get(self, url: str) -> Optional[Dict]:
        """Get cached result for URL."""
        if url in self._cache:
            data = self._cache[url]
            # Update last accessed timestamp
            data['last_accessed'] = datetime.now().isoformat()
            self._save_cache()  # Save updated timestamp
            print(f"✅ Cache hit for {url}")
            return data
        return None

    def set(self, url: str, data: Dict) -> None:
        """Store result for URL in cache."""
        # If result is Grade Error don't cache it
        if data.get('grade') == 'Error':
            print(f"⚠️  Not caching error result for {url}")
            return
        # Add timestamps
        data_copy = data.copy()
        data_copy['timestamp'] = datetime.now().isoformat()
        data_copy['last_accessed'] = datetime.now().isoformat()

        self._cache[url] = data_copy
        self._save_cache()
        print(f"💾 Cached result for {url}")

    def has(self, url: str) -> bool:
        """Check if URL is in cache."""
        return url in self._cache

    def clear(self) -> None:
        """Clear all cached data."""
        self._cache = {}
        self._save_cache()
        print("🗑️  Cache cleared")

    def get_stats(self) -> Dict:
        """Get cache statistics."""
        total_entries = len(self._cache)
        total_size = sum(len(json.dumps(data)) for data in self._cache.values())

        return {
            'total_entries': total_entries,
            'total_size_bytes': total_size,
            'cache_file': str(self.cache_file),
            'max_age_days': self.max_age_days
        }

    def cleanup_expired(self) -> int:
        """Clean up expired entries and return number removed."""
        original_count = len(self._cache)
        self._cache = self._clean_expired_entries(self._cache)
        removed_count = original_count - len(self._cache)

        if removed_count > 0:
            self._save_cache()
            print(f"🧹 Cleaned up {removed_count} expired cache entries")

        return removed_count

# Global cache instance
cache = PersistentCache()

# Convenience functions for backward compatibility
def get_cached_result(url: str) -> Optional[Dict]:
    """Get cached result for URL (backward compatibility)."""
    return cache.get(url)

def set_cached_result(url: str, data: Dict) -> None:
    """Store result for URL (backward compatibility)."""
    cache.set(url, data)

def is_cached(url: str) -> bool:
    """Check if URL is cached (backward compatibility)."""
    return cache.has(url)
