"""
Test suite for the in-memory product cache.

This module verifies cache retrieval, storage, deletion, and
clearing operations using the MemoryCache class.
"""
from cache import MemoryCache

memory_cache = MemoryCache()

key = "product_0_10"
value = {"product":"Laptop","price":800,"stock":10}
key2 = "product_10_10"
value2 = {"product":"PC","price":80,"stock":10}

def test_cache():
    """Verify cache retrieval, storage, and handling of different values."""
    data = memory_cache.get_cache(key)
    assert data is None

    memory_cache.set_cache(key,value)
    data = memory_cache.get_cache(key)
    assert data == value

    memory_cache.set_cache(key2,value=[])
    data = memory_cache.get_cache(key2)
    assert data == []
    
def test_del_cache():
    """Verify that cached entries can be deleted successfully."""
    memory_cache.delete_cache(key)
    data = memory_cache.get_cache(key)
    assert data is None

    memory_cache.set_cache(key2,value2)
    data = memory_cache.get_cache(key2)
    assert data == value2

def test_clear_cache():
    """Verify that clearing the cache removes all stored entries."""
    memory_cache.clear_cache()
    data = memory_cache.get_cache(key2)
    assert data is None
