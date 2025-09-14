"""
MitraVerify Caching Layer
Advanced caching system for embeddings, reranking results, and API responses
"""

import os
import json
import logging
import time
import hashlib
import pickle
from typing import Any, Dict, Optional, Tuple, List
from datetime import datetime, timedelta
from functools import wraps
import threading
from concurrent.futures import ThreadPoolExecutor
import redis
import sqlite3

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class CacheEntry:
    """Cache entry with metadata"""

    def __init__(self, key: str, value: Any, ttl_seconds: int = 3600):
        """
        Initialize cache entry

        Args:
            key: Cache key
            value: Cached value
            ttl_seconds: Time to live in seconds
        """
        self.key = key
        self.value = value
        self.created_at = time.time()
        self.ttl_seconds = ttl_seconds
        self.access_count = 0
        self.last_accessed = time.time()

    def is_expired(self) -> bool:
        """Check if cache entry is expired"""
        return (time.time() - self.created_at) > self.ttl_seconds

    def access(self):
        """Record access to cache entry"""
        self.access_count += 1
        self.last_accessed = time.time()

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization"""
        return {
            'key': self.key,
            'value': self.value,
            'created_at': self.created_at,
            'ttl_seconds': self.ttl_seconds,
            'access_count': self.access_count,
            'last_accessed': self.last_accessed
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'CacheEntry':
        """Create from dictionary"""
        entry = cls(data['key'], data['value'], data['ttl_seconds'])
        entry.created_at = data['created_at']
        entry.access_count = data.get('access_count', 0)
        entry.last_accessed = data.get('last_accessed', data['created_at'])
        return entry

class BaseCache:
    """Base cache class with common functionality"""

    def __init__(self, default_ttl: int = 3600, max_size: int = 10000):
        """
        Initialize base cache

        Args:
            default_ttl: Default time to live in seconds
            max_size: Maximum number of cache entries
        """
        self.default_ttl = default_ttl
        self.max_size = max_size
        self._lock = threading.RLock()

    def _generate_key(self, *args, **kwargs) -> str:
        """Generate cache key from arguments"""
        key_data = str(args) + str(sorted(kwargs.items()))
        return hashlib.md5(key_data.encode()).hexdigest()

    def get(self, key: str) -> Optional[Any]:
        """Get value from cache"""
        raise NotImplementedError

    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        """Set value in cache"""
        raise NotImplementedError

    def delete(self, key: str) -> bool:
        """Delete value from cache"""
        raise NotImplementedError

    def clear(self) -> bool:
        """Clear all cache entries"""
        raise NotImplementedError

    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        raise NotImplementedError

class MemoryCache(BaseCache):
    """In-memory cache implementation"""

    def __init__(self, default_ttl: int = 3600, max_size: int = 10000):
        super().__init__(default_ttl, max_size)
        self._cache: Dict[str, CacheEntry] = {}
        self._cleanup_thread = None
        self._cleanup_interval = 300  # 5 minutes
        self._start_cleanup_thread()

    def _start_cleanup_thread(self):
        """Start background cleanup thread"""
        def cleanup_worker():
            while True:
                time.sleep(self._cleanup_interval)
                self._cleanup_expired()

        self._cleanup_thread = threading.Thread(target=cleanup_worker, daemon=True)
        self._cleanup_thread.start()

    def _cleanup_expired(self):
        """Remove expired entries"""
        with self._lock:
            expired_keys = [
                key for key, entry in self._cache.items()
                if entry.is_expired()
            ]

            for key in expired_keys:
                del self._cache[key]

            if expired_keys:
                logger.info(f"Cleaned up {len(expired_keys)} expired cache entries")

    def get(self, key: str) -> Optional[Any]:
        """Get value from cache"""
        with self._lock:
            entry = self._cache.get(key)
            if entry and not entry.is_expired():
                entry.access()
                return entry.value
            elif entry and entry.is_expired():
                del self._cache[key]
            return None

    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        """Set value in cache"""
        with self._lock:
            # Check size limit
            if len(self._cache) >= self.max_size:
                self._evict_lru()

            ttl_seconds = ttl or self.default_ttl
            self._cache[key] = CacheEntry(key, value, ttl_seconds)
            return True

    def _evict_lru(self):
        """Evict least recently used entries"""
        with self._lock:
            if not self._cache:
                return

            # Find entry with oldest last_accessed time
            lru_key = min(self._cache.keys(),
                         key=lambda k: self._cache[k].last_accessed)

            del self._cache[lru_key]
            logger.info("Evicted LRU cache entry")

    def delete(self, key: str) -> bool:
        """Delete value from cache"""
        with self._lock:
            if key in self._cache:
                del self._cache[key]
                return True
            return False

    def clear(self) -> bool:
        """Clear all cache entries"""
        with self._lock:
            self._cache.clear()
            return True

    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        with self._lock:
            total_entries = len(self._cache)
            expired_entries = sum(1 for entry in self._cache.values() if entry.is_expired())

            if total_entries > 0:
                avg_access_count = sum(entry.access_count for entry in self._cache.values()) / total_entries
                avg_age = sum(time.time() - entry.created_at for entry in self._cache.values()) / total_entries
            else:
                avg_access_count = 0
                avg_age = 0

            return {
                'cache_type': 'memory',
                'total_entries': total_entries,
                'expired_entries': expired_entries,
                'max_size': self.max_size,
                'default_ttl': self.default_ttl,
                'avg_access_count': round(avg_access_count, 2),
                'avg_age_seconds': round(avg_age, 2),
                'hit_rate_estimate': self._estimate_hit_rate()
            }

    def _estimate_hit_rate(self) -> float:
        """Estimate cache hit rate"""
        with self._lock:
            if not self._cache:
                return 0.0

            total_accesses = sum(entry.access_count for entry in self._cache.values())
            if total_accesses == 0:
                return 0.0

            # Simple estimation: assume each entry was accessed at least once
            return min(1.0, len(self._cache) / max(1, total_accesses))

class RedisCache(BaseCache):
    """Redis-based distributed cache"""

    def __init__(self, host: str = 'localhost', port: int = 6379,
                 db: int = 0, password: Optional[str] = None,
                 default_ttl: int = 3600, max_size: int = 10000):
        super().__init__(default_ttl, max_size)

        try:
            self.redis_client = redis.Redis(
                host=host,
                port=port,
                db=db,
                password=password,
                decode_responses=False  # Keep as bytes for pickle
            )
            self.redis_client.ping()  # Test connection
            logger.info("Connected to Redis cache")
        except redis.ConnectionError:
            logger.warning("Redis connection failed, falling back to memory cache")
            self.redis_client = None
            # Fallback to memory cache
            self.fallback_cache = MemoryCache(default_ttl, max_size)

    def get(self, key: str) -> Optional[Any]:
        """Get value from Redis cache"""
        if not self.redis_client:
            return self.fallback_cache.get(key)

        try:
            data = self.redis_client.get(key)
            if data:
                # Deserialize the cached entry
                entry_dict = pickle.loads(data)
                entry = CacheEntry.from_dict(entry_dict)

                if not entry.is_expired():
                    entry.access()
                    # Update access metadata in Redis
                    self._update_entry_metadata(key, entry)
                    return entry.value
                else:
                    # Remove expired entry
                    self.redis_client.delete(key)

            return None
        except Exception as e:
            logger.error(f"Redis get error: {e}")
            return None

    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        """Set value in Redis cache"""
        if not self.redis_client:
            return self.fallback_cache.set(key, value, ttl)

        try:
            ttl_seconds = ttl or self.default_ttl
            entry = CacheEntry(key, value, ttl_seconds)

            # Serialize and store
            data = pickle.dumps(entry.to_dict())
            return bool(self.redis_client.setex(key, ttl_seconds, data))
        except Exception as e:
            logger.error(f"Redis set error: {e}")
            return False

    def _update_entry_metadata(self, key: str, entry: CacheEntry):
        """Update entry metadata in Redis (async)"""
        try:
            data = pickle.dumps(entry.to_dict())
            self.redis_client.setex(key, entry.ttl_seconds, data)
        except Exception as e:
            logger.error(f"Redis metadata update error: {e}")

    def delete(self, key: str) -> bool:
        """Delete value from Redis cache"""
        if not self.redis_client:
            return self.fallback_cache.delete(key)

        try:
            return bool(self.redis_client.delete(key))
        except Exception as e:
            logger.error(f"Redis delete error: {e}")
            return False

    def clear(self) -> bool:
        """Clear all cache entries"""
        if not self.redis_client:
            return self.fallback_cache.clear()

        try:
            return bool(self.redis_client.flushdb())
        except Exception as e:
            logger.error(f"Redis clear error: {e}")
            return False

    def get_stats(self) -> Dict[str, Any]:
        """Get Redis cache statistics"""
        if not self.redis_client:
            return self.fallback_cache.get_stats()

        try:
            info = self.redis_client.info()
            return {
                'cache_type': 'redis',
                'connected': True,
                'total_keys': self.redis_client.dbsize(),
                'used_memory': info.get('used_memory_human', 'N/A'),
                'connected_clients': info.get('connected_clients', 0),
                'uptime_seconds': info.get('uptime_in_seconds', 0),
                'default_ttl': self.default_ttl
            }
        except Exception as e:
            logger.error(f"Redis stats error: {e}")
            return {
                'cache_type': 'redis',
                'connected': False,
                'error': str(e)
            }

class SQLiteCache(BaseCache):
    """SQLite-based persistent cache"""

    def __init__(self, db_path: str = "cache.db", default_ttl: int = 3600, max_size: int = 10000):
        super().__init__(default_ttl, max_size)
        self.db_path = db_path
        self._init_db()
        self._cleanup_thread = None
        self._cleanup_interval = 600  # 10 minutes
        self._start_cleanup_thread()

    def _init_db(self):
        """Initialize SQLite database"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute('''
                CREATE TABLE IF NOT EXISTS cache (
                    key TEXT PRIMARY KEY,
                    value BLOB,
                    created_at REAL,
                    ttl_seconds INTEGER,
                    access_count INTEGER DEFAULT 0,
                    last_accessed REAL
                )
            ''')
            conn.commit()

    def _start_cleanup_thread(self):
        """Start background cleanup thread"""
        def cleanup_worker():
            while True:
                time.sleep(self._cleanup_interval)
                self._cleanup_expired()

        self._cleanup_thread = threading.Thread(target=cleanup_worker, daemon=True)
        self._cleanup_thread.start()

    def _cleanup_expired(self):
        """Remove expired entries from database"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                current_time = time.time()
                cursor = conn.execute(
                    "DELETE FROM cache WHERE (created_at + ttl_seconds) < ?",
                    (current_time,)
                )
                deleted_count = cursor.rowcount
                conn.commit()

                if deleted_count > 0:
                    logger.info(f"Cleaned up {deleted_count} expired SQLite cache entries")
        except Exception as e:
            logger.error(f"SQLite cleanup error: {e}")

    def get(self, key: str) -> Optional[Any]:
        """Get value from SQLite cache"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.execute(
                    "SELECT value, created_at, ttl_seconds, access_count FROM cache WHERE key = ?",
                    (key,)
                )
                row = cursor.fetchone()

                if row:
                    value_blob, created_at, ttl_seconds, access_count = row
                    current_time = time.time()

                    # Check if expired
                    if (created_at + ttl_seconds) < current_time:
                        self.delete(key)
                        return None

                    # Update access metadata
                    new_access_count = access_count + 1
                    conn.execute(
                        "UPDATE cache SET access_count = ?, last_accessed = ? WHERE key = ?",
                        (new_access_count, current_time, key)
                    )
                    conn.commit()

                    # Deserialize value
                    return pickle.loads(value_blob)

                return None
        except Exception as e:
            logger.error(f"SQLite get error: {e}")
            return None

    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        """Set value in SQLite cache"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                # Check size limit
                cursor = conn.execute("SELECT COUNT(*) FROM cache")
                count = cursor.fetchone()[0]

                if count >= self.max_size:
                    self._evict_lru_sqlite(conn)

                ttl_seconds = ttl or self.default_ttl
                current_time = time.time()
                value_blob = pickle.dumps(value)

                conn.execute(
                    "INSERT OR REPLACE INTO cache (key, value, created_at, ttl_seconds, access_count, last_accessed) VALUES (?, ?, ?, ?, 0, ?)",
                    (key, value_blob, current_time, ttl_seconds, current_time)
                )
                conn.commit()
                return True
        except Exception as e:
            logger.error(f"SQLite set error: {e}")
            return False

    def _evict_lru_sqlite(self, conn: sqlite3.Connection):
        """Evict least recently used entry from SQLite"""
        try:
            # Find LRU entry
            cursor = conn.execute(
                "SELECT key FROM cache ORDER BY last_accessed ASC LIMIT 1"
            )
            row = cursor.fetchone()

            if row:
                lru_key = row[0]
                conn.execute("DELETE FROM cache WHERE key = ?", (lru_key,))
                logger.info("Evicted LRU SQLite cache entry")
        except Exception as e:
            logger.error(f"SQLite LRU eviction error: {e}")

    def delete(self, key: str) -> bool:
        """Delete value from SQLite cache"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.execute("DELETE FROM cache WHERE key = ?", (key,))
                conn.commit()
                return cursor.rowcount > 0
        except Exception as e:
            logger.error(f"SQLite delete error: {e}")
            return False

    def clear(self) -> bool:
        """Clear all cache entries"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute("DELETE FROM cache")
                conn.commit()
                return True
        except Exception as e:
            logger.error(f"SQLite clear error: {e}")
            return False

    def get_stats(self) -> Dict[str, Any]:
        """Get SQLite cache statistics"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.execute("SELECT COUNT(*), AVG(access_count), AVG(strftime('%s', 'now') - created_at) FROM cache")
                count, avg_access, avg_age = cursor.fetchone()

                return {
                    'cache_type': 'sqlite',
                    'total_entries': count or 0,
                    'db_path': self.db_path,
                    'max_size': self.max_size,
                    'default_ttl': self.default_ttl,
                    'avg_access_count': round(avg_access or 0, 2),
                    'avg_age_seconds': round(avg_age or 0, 2)
                }
        except Exception as e:
            logger.error(f"SQLite stats error: {e}")
            return {
                'cache_type': 'sqlite',
                'error': str(e)
            }

class MultiLevelCache:
    """Multi-level cache with L1 (memory) and L2 (persistent)"""

    def __init__(self, l1_cache: BaseCache, l2_cache: BaseCache):
        """
        Initialize multi-level cache

        Args:
            l1_cache: Level 1 cache (fast, small)
            l2_cache: Level 2 cache (slower, larger)
        """
        self.l1_cache = l1_cache
        self.l2_cache = l2_cache

    def get(self, key: str) -> Optional[Any]:
        """Get value from multi-level cache"""
        # Try L1 cache first
        value = self.l1_cache.get(key)
        if value is not None:
            return value

        # Try L2 cache
        value = self.l2_cache.get(key)
        if value is not None:
            # Promote to L1 cache
            self.l1_cache.set(key, value)
            return value

        return None

    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        """Set value in multi-level cache"""
        # Set in both caches
        l1_success = self.l1_cache.set(key, value, ttl)
        l2_success = self.l2_cache.set(key, value, ttl)

        return l1_success and l2_success

    def delete(self, key: str) -> bool:
        """Delete value from multi-level cache"""
        l1_deleted = self.l1_cache.delete(key)
        l2_deleted = self.l2_cache.delete(key)

        return l1_deleted or l2_deleted

    def clear(self) -> bool:
        """Clear all cache levels"""
        l1_cleared = self.l1_cache.clear()
        l2_cleared = self.l2_cache.clear()

        return l1_cleared and l2_cleared

    def get_stats(self) -> Dict[str, Any]:
        """Get multi-level cache statistics"""
        return {
            'cache_type': 'multi_level',
            'l1_cache': self.l1_cache.get_stats(),
            'l2_cache': self.l2_cache.get_stats()
        }

class CacheManager:
    """Cache manager with automatic cache selection and monitoring"""

    def __init__(self, cache_config: Dict[str, Any] = None):
        """
        Initialize cache manager

        Args:
            cache_config: Cache configuration
        """
        self.cache_config = cache_config or self._default_config()
        self.cache = self._initialize_cache()
        self.monitoring_enabled = True
        self.stats = {
            'hits': 0,
            'misses': 0,
            'sets': 0,
            'deletes': 0,
            'errors': 0
        }

    def _default_config(self) -> Dict[str, Any]:
        """Get default cache configuration"""
        return {
            'type': 'memory',  # memory, redis, sqlite, multi_level
            'default_ttl': 3600,
            'max_size': 10000,
            'redis_config': {
                'host': 'localhost',
                'port': 6379,
                'db': 0
            },
            'sqlite_config': {
                'db_path': 'cache.db'
            }
        }

    def _initialize_cache(self) -> BaseCache:
        """Initialize cache based on configuration"""
        cache_type = self.cache_config.get('type', 'memory')

        if cache_type == 'redis':
            redis_config = self.cache_config.get('redis_config', {})
            return RedisCache(
                host=redis_config.get('host', 'localhost'),
                port=redis_config.get('port', 6379),
                db=redis_config.get('db', 0),
                password=redis_config.get('password'),
                default_ttl=self.cache_config.get('default_ttl', 3600),
                max_size=self.cache_config.get('max_size', 10000)
            )
        elif cache_type == 'sqlite':
            sqlite_config = self.cache_config.get('sqlite_config', {})
            return SQLiteCache(
                db_path=sqlite_config.get('db_path', 'cache.db'),
                default_ttl=self.cache_config.get('default_ttl', 3600),
                max_size=self.cache_config.get('max_size', 10000)
            )
        elif cache_type == 'multi_level':
            l1_cache = MemoryCache(
                default_ttl=self.cache_config.get('default_ttl', 3600),
                max_size=self.cache_config.get('max_size', 1000)  # Smaller L1
            )
            l2_cache = self._initialize_cache_from_config('sqlite')  # L2 as SQLite
            return MultiLevelCache(l1_cache, l2_cache)
        else:  # memory
            return MemoryCache(
                default_ttl=self.cache_config.get('default_ttl', 3600),
                max_size=self.cache_config.get('max_size', 10000)
            )

    def _initialize_cache_from_config(self, cache_type: str) -> BaseCache:
        """Initialize specific cache type"""
        config = self.cache_config.copy()
        config['type'] = cache_type
        temp_manager = CacheManager(config)
        return temp_manager.cache

    def get(self, key: str) -> Optional[Any]:
        """Get value from cache with monitoring"""
        try:
            value = self.cache.get(key)
            if value is not None:
                self.stats['hits'] += 1
            else:
                self.stats['misses'] += 1
            return value
        except Exception as e:
            self.stats['errors'] += 1
            logger.error(f"Cache get error: {e}")
            return None

    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        """Set value in cache with monitoring"""
        try:
            success = self.cache.set(key, value, ttl)
            if success:
                self.stats['sets'] += 1
            return success
        except Exception as e:
            self.stats['errors'] += 1
            logger.error(f"Cache set error: {e}")
            return False

    def delete(self, key: str) -> bool:
        """Delete value from cache with monitoring"""
        try:
            success = self.cache.delete(key)
            if success:
                self.stats['deletes'] += 1
            return success
        except Exception as e:
            self.stats['errors'] += 1
            logger.error(f"Cache delete error: {e}")
            return False

    def clear(self) -> bool:
        """Clear cache with monitoring"""
        try:
            return self.cache.clear()
        except Exception as e:
            self.stats['errors'] += 1
            logger.error(f"Cache clear error: {e}")
            return False

    def get_stats(self) -> Dict[str, Any]:
        """Get comprehensive cache statistics"""
        cache_stats = self.cache.get_stats()

        total_requests = self.stats['hits'] + self.stats['misses']
        hit_rate = (self.stats['hits'] / total_requests) if total_requests > 0 else 0

        return {
            'cache_stats': cache_stats,
            'monitoring_stats': {
                'hits': self.stats['hits'],
                'misses': self.stats['misses'],
                'sets': self.stats['sets'],
                'deletes': self.stats['deletes'],
                'errors': self.stats['errors'],
                'total_requests': total_requests,
                'hit_rate': round(hit_rate, 4)
            }
        }

def cached(ttl_seconds: Optional[int] = None, key_prefix: str = ""):
    """
    Decorator for caching function results

    Args:
        ttl_seconds: Cache TTL in seconds
        key_prefix: Prefix for cache keys
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Get cache manager from global context (would be set up in app)
            cache_manager = getattr(wrapper, '_cache_manager', None)
            if not cache_manager:
                # Fallback to direct function call if no cache
                return func(*args, **kwargs)

            # Generate cache key
            key_data = f"{key_prefix}:{func.__name__}:{args}:{sorted(kwargs.items())}"
            cache_key = hashlib.md5(key_data.encode()).hexdigest()

            # Try cache first
            cached_result = cache_manager.get(cache_key)
            if cached_result is not None:
                return cached_result

            # Execute function
            result = func(*args, **kwargs)

            # Cache result
            cache_manager.set(cache_key, result, ttl_seconds)

            return result

        # Store cache manager reference (set externally)
        wrapper._cache_manager = None

        return wrapper
    return decorator

def main():
    """Test the caching system"""
    print("Testing MitraVerify Caching System...")

    try:
        # Test memory cache
        print("\n1. Testing Memory Cache...")
        memory_cache = MemoryCache(default_ttl=60, max_size=100)

        # Test basic operations
        memory_cache.set("test_key", "test_value")
        value = memory_cache.get("test_key")
        print(f"Memory cache get: {value}")

        stats = memory_cache.get_stats()
        print(f"Memory cache stats: {stats}")

        # Test SQLite cache
        print("\n2. Testing SQLite Cache...")
        sqlite_cache = SQLiteCache(db_path="test_cache.db", default_ttl=60)

        sqlite_cache.set("sqlite_key", {"data": "test"})
        sqlite_value = sqlite_cache.get("sqlite_key")
        print(f"SQLite cache get: {sqlite_value}")

        sqlite_stats = sqlite_cache.get_stats()
        print(f"SQLite cache stats: {sqlite_stats}")

        # Test cache manager
        print("\n3. Testing Cache Manager...")
        cache_manager = CacheManager({
            'type': 'memory',
            'default_ttl': 60,
            'max_size': 100
        })

        cache_manager.set("manager_key", "manager_value")
        manager_value = cache_manager.get("manager_key")
        print(f"Cache manager get: {manager_value}")

        manager_stats = cache_manager.get_stats()
        print(f"Cache manager stats: {manager_stats['monitoring_stats']}")

        print("\n✅ Caching system test completed successfully!")

        # Cleanup
        try:
            os.remove("test_cache.db")
        except:
            pass

    except Exception as e:
        print(f"❌ Test failed: {e}")

if __name__ == '__main__':
    main()