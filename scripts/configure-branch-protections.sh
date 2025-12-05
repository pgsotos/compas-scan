#!/bin/bash
# Script to configure branch protection rules according to Gitflow best practices
# Uses GitHub API to set protection rules for develop, staging, and main branches

set -e

OWNER="pgsotos"
REPO="compas-scan"

echo "🛡️  Configurando protecciones de rama según Gitflow..."
echo ""

# Function to configure branch protection
configure_branch() {
    local BRANCH=$1
    local REVIEWS=$2
    local ENFORCE_ADMINS=$3
    local STRICT_CHECKS=$4
    local CONTEXTS=$5
    
    echo "📋 Configurando rama: $BRANCH"
    echo "   Reviews requeridos: $REVIEWS"
    echo "   Enforce admins: $ENFORCE_ADMINS"
    echo "   Status checks strict: $STRICT_CHECKS"
    echo ""
    
    # Build the protection payload
    local PAYLOAD="{
        \"required_pull_request_reviews\": {
            \"required_approving_review_count\": $REVIEWS,
            \"dismiss_stale_reviews\": true
        },
        \"enforce_admins\": $ENFORCE_ADMINS,
        \"required_status_checks\": {
            \"strict\": $STRICT_CHECKS,
            \"contexts\": $CONTEXTS
        },
        \"allow_force_pushes\": false,
        \"allow_deletions\": false,
        \"restrictions\": null
    }"
    
    # Apply protection
    if gh api -X PUT "repos/$OWNER/$REPO/branches/$BRANCH/protection" \
        --input - <<< "$PAYLOAD" 2>&1; then
        echo "✅ Protección configurada para $BRANCH"
    else
        echo "⚠️  Error configurando $BRANCH (puede que la rama no exista o ya esté protegida)"
    fi
    echo ""
}

# Configure develop branch (0 reviews, fast iteration)
echo "🔧 Configurando rama 'develop'..."
configure_branch "develop" 0 false false "[]"

# Configure staging branch (1 review, QA validation)
echo "🔧 Configurando rama 'staging'..."
configure_branch "staging" 1 false true "[\"Vercel\"]"

# Configure main branch (2 reviews, production safety)
echo "🔧 Configurando rama 'main'..."
configure_branch "main" 2 true true "[\"Vercel\", \"Tests\"]"

echo "✅ Configuración completada"
echo ""
echo "📊 Verificar configuración:"
echo "   gh api repos/$OWNER/$REPO/branches/develop/protection | jq"
echo "   gh api repos/$OWNER/$REPO/branches/staging/protection | jq"
echo "   gh api repos/$OWNER/$REPO/branches/main/protection | jq"

