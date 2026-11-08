"""
In-memory caching module for the product management application.

Provides a thread-safe cache using TTLCache with automatic expiration
and a maximum storage capacity. Cache operations are protected by a lock
and application events are recorded through the configured logger.
"""

from threading import Lock
from cachetools import TTLCache

from configs import get_logger

logger = get_logger("memory_cache")

class MemoryCache:
    """Manage thread-safe in-memory caching with automatic expiration."""
    def __init__(self):
        """Initialize the thread lock and TTL-based in-memory cache."""
        self.lock = Lock()
        self._cache = TTLCache(maxsize=1000,ttl=30)

    def get_cache(self,key):
        """
        Retrieve a cached value using its key.

        Returns the cached value when available, or None when the key is missing
        or the entry has expired.
        """
        with self.lock:
            data = self._cache.get(key)
        
            if data is not None:
                logger.debug("Cache hit!")
                return data
            
            logger.debug("Cache miss!")
            return None

    def set_cache(self,key, value):
        """Store a value in the cache using the supplied key."""
        with self.lock:
            logger.debug("Setting a cache.")
            self._cache[key] = value

    def delete_cache(self,key):
        """Remove a specific entry from the cache if it exists."""
        with self.lock:
            logger.debug("Removing a cache.")
            self._cache.pop(key,None)

    def clear_cache(self):
        """Remove all entries currently stored in the cache."""
        with self.lock:
            logger.debug("Clearing cache memory.")
            self._cache.clear()
