import requests_cache

SESSION = requests_cache.CachedSession(expire_after=60 * 60, backend="memory")

