"""
Redis Caching Module for CompasScan

Provides async caching functionality for:
- Gemini AI results (24h TTL)
- Google Search results (1h TTL)
- Brand context (6h TTL)
"""

import hashlib
import json
import os
from typing import Any, Optional

from redis import asyncio as aioredis


class CacheManager:
    """Async Redis cache manager with TTL support."""

    def __init__(self):
        self.client: Optional[aioredis.Redis] = None
        self.enabled = bool(os.environ.get("REDIS_URL"))
        self.redis_url = os.environ.get("REDIS_URL", "redis://localhost:6379")

        # TTL configurations (in seconds)
        self.TTL_GEMINI = int(os.environ.get("REDIS_TTL_GEMINI", 86400))  # 24 hours
        self.TTL_GOOGLE = int(os.environ.get("REDIS_TTL_GOOGLE", 3600))  # 1 hour
        self.TTL_CONTEXT = int(os.environ.get("REDIS_TTL_CONTEXT", 21600))  # 6 hours

    async def connect(self):
        """Initialize Redis connection."""
        if not self.enabled:
            print("ℹ️  Redis no configurado. Cache deshabilitado.")
            return

        try:
            # Upstash requires SSL/TLS - convert redis:// to rediss://
            redis_url = self.redis_url
            if "upstash.io" in redis_url and redis_url.startswith("redis://"):
                redis_url = redis_url.replace("redis://", "rediss://", 1)
                print("🔐 Upstash detectado - usando SSL/TLS")

            self.client = await aioredis.from_url(redis_url, encoding="utf-8", decode_responses=True)
            await self.client.ping()
            print("✅ Redis connected successfully.")
        except Exception as e:
            print(f"⚠️  Error conectando a Redis: {e}")
            self.enabled = False
            self.client = None

    async def close(self):
        """Close Redis connection."""
        if self.client:
            await self.client.aclose()
            print("✅ Redis desconectado.")

    def _generate_key(self, prefix: str, data: str) -> str:
        """Generate cache key with hash to avoid special characters."""
        hash_suffix = hashlib.md5(data.encode()).hexdigest()[:12]
        return f"compas:{prefix}:{hash_suffix}"

    async def get(self, key: str) -> Optional[dict]:
        """Get value from cache."""
        if not self.enabled or not self.client:
            return None

        try:
            value = await self.client.get(key)
            if value:
                print(f"✅ Cache HIT: {key}")
                return json.loads(value)
            print(f"❌ Cache MISS: {key}")
            return None
        except Exception as e:
            print(f"⚠️  Error obteniendo cache: {e}")
            return None

    async def set(self, key: str, value: Any, ttl: int):
        """Set value in cache with TTL."""
        if not self.enabled or not self.client:
            return

        try:
            await self.client.setex(key, ttl, json.dumps(value))
            print(f"💾 Cache SET: {key} (TTL: {ttl}s)")
        except Exception as e:
            print(f"⚠️  Error guardando en cache: {e}")

    async def delete(self, pattern: str):
        """Delete keys matching pattern."""
        if not self.enabled or not self.client:
            return

        try:
            keys = await self.client.keys(pattern)
            if keys:
                await self.client.delete(*keys)
                print(f"🗑️  Eliminadas {len(keys)} entradas de cache: {pattern}")
        except Exception as e:
            print(f"⚠️  Error eliminando cache: {e}")

    # === Métodos Específicos de Negocio ===

    async def get_gemini_results(self, brand: str) -> Optional[list]:
        """Get cached Gemini AI results."""
        key = self._generate_key("gemini", brand.lower())
        return await self.get(key)

    async def set_gemini_results(self, brand: str, results: list):
        """Cache Gemini AI results (24h TTL)."""
        key = self._generate_key("gemini", brand.lower())
        await self.set(key, results, self.TTL_GEMINI)

    async def get_google_search(self, query: str) -> Optional[list]:
        """Get cached Google Search results."""
        key = self._generate_key("google", query.lower())
        return await self.get(key)

    async def set_google_search(self, query: str, results: list):
        """Cache Google Search results (1h TTL)."""
        key = self._generate_key("google", query.lower())
        await self.set(key, results, self.TTL_GOOGLE)

    async def get_brand_context(self, brand: str) -> Optional[dict]:
        """Get cached brand context."""
        key = self._generate_key("context", brand.lower())
        return await self.get(key)

    async def set_brand_context(self, brand: str, context: dict):
        """Cache brand context (6h TTL)."""
        key = self._generate_key("context", brand.lower())
        await self.set(key, context, self.TTL_CONTEXT)

    async def invalidate_brand(self, brand: str):
        """Invalidate all cache entries for a specific brand."""
        pattern = f"compas:*:{hashlib.md5(brand.lower().encode()).hexdigest()[:12]}"
        await self.delete(pattern)


# Global cache instance
cache = CacheManager()
