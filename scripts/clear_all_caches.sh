#!/bin/bash
# Clear Redis cache for all environments

set -e

echo "════════════════════════════════════════════════════════════════════════"
echo "  🧹 CLEARING REDIS CACHE - ALL ENVIRONMENTS"
echo "════════════════════════════════════════════════════════════════════════"
echo ""

# Change to project root
cd "$(dirname "$0")/.."

# Function to clear cache for an environment
clear_env_cache() {
    local env_name=$1
    local env_file=$2
    
    echo "📍 Clearing $env_name cache..."
    echo "────────────────────────────────────────────────────────────────────────"
    
    if [ ! -f "$env_file" ]; then
        echo "⚠️  $env_file not found. Downloading from Vercel..."
        vercel env pull "$env_file" --environment "$env_name" --yes
    fi
    
    # Extract REDIS_URL from env file
    REDIS_URL=$(grep "^REDIS_URL=" "$env_file" | cut -d '=' -f2- | tr -d '"')
    
    if [ -z "$REDIS_URL" ]; then
        echo "❌ REDIS_URL not found in $env_file"
        return 1
    fi
    
    # Run cache cleaner
    REDIS_URL="$REDIS_URL" uv run python scripts/clear_redis_cache.py --env "$env_name" --manual
    echo ""
}

# 1. Clear LOCAL cache (if Redis is running)
echo "📍 Clearing LOCAL cache..."
echo "────────────────────────────────────────────────────────────────────────"
uv run python scripts/clear_redis_cache.py --env local || echo "⚠️  Local Redis not available"
echo ""

# 2. Clear DEVELOPMENT cache
clear_env_cache "development" ".env.development"

# 3. Clear PREVIEW (Staging) cache
clear_env_cache "preview" ".env.preview"

# 4. Clear PRODUCTION cache
clear_env_cache "production" ".env.production"

# Cleanup env files (security)
echo "🧹 Cleaning up temporary env files..."
rm -f .env.development .env.preview .env.production
echo "✅ Temporary files removed"
echo ""

echo "════════════════════════════════════════════════════════════════════════"
echo "  ✅ CACHE CLEARING COMPLETED"
echo "════════════════════════════════════════════════════════════════════════"

