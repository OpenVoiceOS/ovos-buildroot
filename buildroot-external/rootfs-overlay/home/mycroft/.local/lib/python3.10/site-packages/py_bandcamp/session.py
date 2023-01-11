import requests_cache

SESSION = requests_cache.CachedSession(expire_after=5 * 60, backend="memory")
