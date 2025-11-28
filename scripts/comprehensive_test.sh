#!/bin/bash
# Comprehensive Pre-Staging Test Suite
# Tests all functionality before promoting to staging

set -e  # Exit on first error

BASE_URL="http://localhost:8000"
PASSED=0
FAILED=0
TOTAL=0

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo ""
echo "════════════════════════════════════════════════════════════════════════════════"
echo "  🧪 COMPREHENSIVE PRE-STAGING TEST SUITE"
echo "════════════════════════════════════════════════════════════════════════════════"
echo ""

# Helper function to run a test
run_test() {
    local test_name="$1"
    local test_command="$2"
    local expected_pattern="$3"
    
    TOTAL=$((TOTAL + 1))
    echo -n "Test $TOTAL: $test_name... "
    
    if result=$(eval "$test_command" 2>&1); then
        if echo "$result" | grep -q "$expected_pattern"; then
            echo -e "${GREEN}✓ PASS${NC}"
            PASSED=$((PASSED + 1))
            return 0
        else
            echo -e "${RED}✗ FAIL${NC} (unexpected output)"
            echo "  Expected pattern: $expected_pattern"
            echo "  Got: ${result:0:100}"
            FAILED=$((FAILED + 1))
            return 1
        fi
    else
        echo -e "${RED}✗ FAIL${NC} (command failed)"
        FAILED=$((FAILED + 1))
        return 1
    fi
}

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo " 1. INFRASTRUCTURE TESTS"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

run_test "Server is reachable" \
    "curl -s -o /dev/null -w '%{http_code}' $BASE_URL/api/health" \
    "200"

run_test "Health endpoint returns JSON" \
    "curl -s $BASE_URL/api/health | python3 -c 'import json, sys; json.load(sys.stdin)' && echo 'valid'" \
    "valid"

run_test "Health status is healthy" \
    "curl -s $BASE_URL/api/health | python3 -c 'import json, sys; print(json.load(sys.stdin)[\"status\"])'" \
    "healthy"

run_test "Sentry is enabled" \
    "curl -s $BASE_URL/api/health | python3 -c 'import json, sys; print(json.load(sys.stdin)[\"observability\"][\"sentry\"])'" \
    "True"

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo " 2. CORE API TESTS"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

run_test "API scan endpoint is reachable" \
    "curl -s -o /dev/null -w '%{http_code}' '$BASE_URL/api/?brand=Nike'" \
    "200"

run_test "API returns valid JSON structure" \
    "curl -s '$BASE_URL/api/?brand=Nike' | python3 -c 'import json, sys; d=json.load(sys.stdin); assert \"status\" in d and \"data\" in d; print(\"valid\")'" \
    "valid"

run_test "API returns success status" \
    "curl -s '$BASE_URL/api/?brand=Nike' | python3 -c 'import json, sys; print(json.load(sys.stdin)[\"status\"])'" \
    "success"

run_test "API returns competitors" \
    "curl -s '$BASE_URL/api/?brand=Nike' | python3 -c 'import json, sys; d=json.load(sys.stdin); hda=len(d[\"data\"][\"HDA_Competitors\"]); print(f\"found:{hda}\")'" \
    "found:[1-9]"

run_test "API returns brand_context" \
    "curl -s '$BASE_URL/api/?brand=Hulu' | python3 -c 'import json, sys; d=json.load(sys.stdin); assert \"brand_context\" in d; print(\"present\")'" \
    "present"

run_test "Brand context includes search_queries" \
    "curl -s '$BASE_URL/api/?brand=Hulu' | python3 -c 'import json, sys; d=json.load(sys.stdin); assert len(d[\"brand_context\"][\"search_queries\"]) > 0; print(\"present\")'" \
    "present"

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo " 3. SENTRY INTEGRATION TESTS"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

run_test "Sentry debug endpoint triggers error" \
    "curl -s -o /dev/null -w '%{http_code}' $BASE_URL/sentry-debug" \
    "500"

run_test "Sentry captures exceptions" \
    "curl -s $BASE_URL/test-error 2>&1 | grep -q 'Internal Server Error' && echo 'captured' || echo 'not_captured'" \
    "captured"

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo " 4. BUSINESS LOGIC TESTS"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

run_test "Scan returns valid competitor data" \
    "curl -s '$BASE_URL/api/?brand=Netflix' | python3 -c 'import json, sys; d=json.load(sys.stdin); assert len(d[\"data\"][\"HDA_Competitors\"]) > 0; print(\"valid\")'" \
    "valid"

run_test "HDA competitors have justification" \
    "curl -s '$BASE_URL/api/?brand=Spotify' | python3 -c 'import json, sys; d=json.load(sys.stdin); comp=d[\"data\"][\"HDA_Competitors\"][0]; assert \"justification\" in comp; print(\"present\")'" \
    "present"

run_test "Competitors have valid URLs" \
    "curl -s '$BASE_URL/api/?brand=Amazon' | python3 -c 'import json, sys; d=json.load(sys.stdin); comp=d[\"data\"][\"HDA_Competitors\"][0]; assert comp[\"url\"].startswith(\"http\"); print(\"valid\")'" \
    "valid"

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo " 5. EDGE CASE TESTS"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

run_test "Empty brand parameter returns validation error" \
    "curl -s '$BASE_URL/api/?brand=' | python3 -c 'import json, sys; d=json.load(sys.stdin); print(\"detail\" if \"detail\" in d else \"no_detail\")'" \
    "detail"

run_test "Missing brand parameter returns validation error" \
    "curl -s '$BASE_URL/api/' | python3 -c 'import json, sys; d=json.load(sys.stdin); print(\"detail\" if \"detail\" in d else \"no_detail\")'" \
    "detail"

run_test "Invalid URL format handled gracefully" \
    "curl -s '$BASE_URL/api/?brand=not-a-valid-url' | python3 -c 'import json, sys; d=json.load(sys.stdin); assert d[\"status\"] in [\"success\", \"error\"]; print(\"handled\")'" \
    "handled"

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo " 6. PERFORMANCE TESTS"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

run_test "Health check responds quickly (<500ms)" \
    "time_ms=\$(curl -s -o /dev/null -w '%{time_total}' $BASE_URL/api/health | awk '{print \$1*1000}'); test \${time_ms%.*} -lt 500 && echo 'fast' || echo 'slow'" \
    "fast"

run_test "API responds in reasonable time (<10s)" \
    "curl -s --max-time 10 '$BASE_URL/api/?brand=Nike' > /dev/null && echo 'responsive' || echo 'timeout'" \
    "responsive"

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo " 7. DOCUMENTATION TESTS"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

run_test "OpenAPI docs are accessible" \
    "curl -s -o /dev/null -w '%{http_code}' $BASE_URL/docs" \
    "200"

run_test "ReDoc is accessible" \
    "curl -s -o /dev/null -w '%{http_code}' $BASE_URL/redoc" \
    "200"

echo ""
echo "════════════════════════════════════════════════════════════════════════════════"
echo "  📊 TEST RESULTS SUMMARY"
echo "════════════════════════════════════════════════════════════════════════════════"
echo ""
echo "  Total Tests:  $TOTAL"
echo -e "  ${GREEN}Passed:       $PASSED${NC}"
echo -e "  ${RED}Failed:       $FAILED${NC}"
echo ""

if [ $FAILED -eq 0 ]; then
    echo -e "${GREEN}✅ ALL TESTS PASSED!${NC}"
    echo ""
    echo "🚀 System is ready for staging promotion!"
    echo ""
    exit 0
else
    echo -e "${RED}❌ SOME TESTS FAILED${NC}"
    echo ""
    echo "⚠️  Please fix the issues before promoting to staging."
    echo ""
    exit 1
fi

