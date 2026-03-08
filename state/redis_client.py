"""Simple Redis client wrapper for session state and caching."""

import redis


class RedisClient:
    def __init__(self, url):
        self._client = redis.from_url(url)

    def set(self, key, value, **kwargs):
        self._client.set(key, value, **kwargs)

    def get(self, key):
        return self._client.get(key)
