#!/usr/bin/env python3
"""
Script to clear Redis cache across all environments.

Usage:
    python scripts/clear_redis_cache.py --env all
    python scripts/clear_redis_cache.py --env production
    python scripts/clear_redis_cache.py --env preview
    python scripts/clear_redis_cache.py --env development
"""

import argparse
import asyncio
import os
import sys
from pathlib import Path

# Add project root to Python path
sys.path.insert(0, str(Path(__file__).parent.parent))

from redis import asyncio as aioredis


async def clear_redis_cache(redis_url: str, env_name: str):
    """Clear all CompasScan cache entries from Redis."""
    if not redis_url:
        print(f"⚠️  No REDIS_URL found for {env_name}")
        return False

    try:
        # Upstash requires SSL/TLS
        if "upstash.io" in redis_url and redis_url.startswith("redis://"):
            redis_url = redis_url.replace("redis://", "rediss://", 1)
            print(f"🔐 {env_name}: Upstash detected - using SSL/TLS")

        # Connect to Redis
        client = await aioredis.from_url(redis_url, encoding="utf-8", decode_responses=True)
        await client.ping()
        print(f"✅ {env_name}: Connected to Redis")

        # Get all CompasScan keys
        pattern = "compas:*"
        keys = await client.keys(pattern)

        if not keys:
            print(f"ℹ️  {env_name}: No cache entries found (pattern: {pattern})")
            await client.aclose()
            return True

        # Delete all keys
        deleted_count = await client.delete(*keys)
        print(f"🗑️  {env_name}: Deleted {deleted_count} cache entries")

        # Show breakdown by type
        gemini_keys = [k for k in keys if k.startswith("compas:gemini:")]
        google_keys = [k for k in keys if k.startswith("compas:google:")]
        context_keys = [k for k in keys if k.startswith("compas:context:")]

        print(f"   📊 Breakdown:")
        print(f"      - Gemini results: {len(gemini_keys)}")
        print(f"      - Google searches: {len(google_keys)}")
        print(f"      - Brand contexts: {len(context_keys)}")

        await client.aclose()
        return True

    except Exception as e:
        print(f"❌ {env_name}: Error clearing cache: {e}")
        return False


async def get_vercel_env(environment: str, var_name: str) -> str:
    """Get environment variable from Vercel using CLI."""
    try:
        proc = await asyncio.create_subprocess_exec(
            "vercel",
            "env",
            "ls",
            environment,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        stdout, stderr = await proc.communicate()

        if proc.returncode != 0:
            print(f"⚠️  Error getting {var_name} from Vercel {environment}: {stderr.decode()}")
            return ""

        # Parse output (simplified - assumes standard format)
        output = stdout.decode()
        for line in output.split("\n"):
            if var_name in line:
                print(f"✅ Found {var_name} in Vercel {environment}")
                # Note: Vercel CLI shows "Encrypted" not actual value
                # We need to pull the env file instead
                return "vercel_encrypted"

        return ""

    except Exception as e:
        print(f"⚠️  Error accessing Vercel CLI: {e}")
        return ""


async def clear_vercel_env_cache(environment: str):
    """
    Clear cache for Vercel environment.
    Note: This requires manual env var access or direct Redis URL.
    """
    print(f"\n🔍 {environment.upper()}: Attempting to clear cache...")
    print(f"ℹ️  Note: Vercel encrypts env vars, so you need to:")
    print(f"   1. Go to Vercel Dashboard → Project → Settings → Environment Variables")
    print(f"   2. Copy the REDIS_URL for {environment}")
    print(f"   3. Run: REDIS_URL='<your-url>' python scripts/clear_redis_cache.py --env {environment} --manual")
    return False


async def main():
    parser = argparse.ArgumentParser(description="Clear Redis cache for CompasScan")
    parser.add_argument(
        "--env",
        choices=["all", "local", "development", "preview", "production"],
        default="local",
        help="Environment to clear cache from",
    )
    parser.add_argument("--manual", action="store_true", help="Use REDIS_URL from environment variable")

    args = parser.parse_args()

    print("=" * 70)
    print("  🧹 COMPAS-SCAN CACHE CLEANER")
    print("=" * 70)
    print()

    results = {}

    if args.env == "local" or args.env == "all":
        print("📍 LOCAL ENVIRONMENT")
        print("-" * 70)
        redis_url = os.environ.get("REDIS_URL", "redis://localhost:6379")
        results["local"] = await clear_redis_cache(redis_url, "Local")
        print()

    if args.env == "all":
        print("⚠️  VERCEL ENVIRONMENTS (Development, Preview, Production)")
        print("-" * 70)
        print("For Vercel environments, you need to manually provide REDIS_URL:")
        print()
        print("Option 1: Pull env vars from Vercel")
        print("  vercel env pull .env.production")
        print("  source .env.production")
        print("  python scripts/clear_redis_cache.py --env production --manual")
        print()
        print("Option 2: Copy REDIS_URL from Vercel Dashboard")
        print("  REDIS_URL='<url>' python scripts/clear_redis_cache.py --env production --manual")
        print()

    elif args.env in ["development", "preview", "production"]:
        if args.manual:
            print(f"📍 VERCEL {args.env.upper()} ENVIRONMENT")
            print("-" * 70)
            redis_url = os.environ.get("REDIS_URL", "")
            if not redis_url:
                print("❌ REDIS_URL not found in environment variables")
                print("Please set it first:")
                print(f"  export REDIS_URL='<your-redis-url>'")
                sys.exit(1)
            results[args.env] = await clear_redis_cache(redis_url, f"Vercel {args.env.title()}")
        else:
            print(f"\n⚠️  To clear {args.env} cache, use --manual flag:")
            print(f"  1. vercel env pull .env.{args.env}")
            print(f"  2. source .env.{args.env}")
            print(f"  3. python scripts/clear_redis_cache.py --env {args.env} --manual")
            sys.exit(1)

    print()
    print("=" * 70)
    print("  📊 SUMMARY")
    print("=" * 70)

    success_count = sum(1 for v in results.values() if v)
    total_count = len(results)

    for env_name, success in results.items():
        status = "✅" if success else "❌"
        print(f"{status} {env_name.title()}: {'Cleared' if success else 'Failed'}")

    print()
    print(f"Result: {success_count}/{total_count} environments cleared successfully")
    print()

    return 0 if success_count == total_count else 1


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))

