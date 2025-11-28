#!/bin/bash
# Test script for Sentry advanced features

BASE_URL="http://localhost:8000"

echo "════════════════════════════════════════════════════════════════"
echo "  🧪 SENTRY ADVANCED FEATURES TEST"
echo "════════════════════════════════════════════════════════════════"
echo ""

echo "📊 Testing different types of events..."
echo ""

# 1. Test error with breadcrumbs
echo "1️⃣  Error Event (ZeroDivisionError)"
echo "   Endpoint: GET /sentry-debug"
curl -s "$BASE_URL/sentry-debug" > /dev/null
echo "   ✅ Sent: Error with automatic breadcrumbs"
echo ""
sleep 1

# 2. Test successful scan with tracking
echo "2️⃣  Successful Scan Event (Business Logic Tracking)"
echo "   Endpoint: GET /api/?brand=Nike"
curl -s "$BASE_URL/api/?brand=Nike" > /dev/null
echo "   ✅ Sent: Scan event with:"
echo "      - Breadcrumb: 'Starting competitor scan for: Nike'"
echo "      - Breadcrumb: 'Scan completed: X competitors found'"
echo "      - Tag: scan_strategy=ai_first"
echo "      - Tag: scan_success=true"
echo "      - Context: scan_details (HDA/LDA counts)"
echo ""
sleep 1

# 3. Test another scan for variety
echo "3️⃣  Another Scan (Different Brand)"
echo "   Endpoint: GET /api/?brand=Hulu"
curl -s "$BASE_URL/api/?brand=Hulu" > /dev/null
echo "   ✅ Sent: Scan event with different brand context"
echo ""
sleep 1

# 4. Test health check (low sampling in production)
echo "4️⃣  Health Check (Low Priority Transaction)"
echo "   Endpoint: GET /api/health"
curl -s "$BASE_URL/api/health" > /dev/null
echo "   ✅ Sent: Health check (sampled at 1% in production)"
echo ""

echo "════════════════════════════════════════════════════════════════"
echo "  ✅ TEST COMPLETED - Events Sent to Sentry"
echo "════════════════════════════════════════════════════════════════"
echo ""
echo "🔍 Verify in Sentry Dashboard:"
echo ""
echo "   📍 Issues: https://sentry.io → Issues"
echo "      Expected: 1 ZeroDivisionError with breadcrumbs"
echo ""
echo "   📊 Performance: https://sentry.io → Performance"
echo "      Expected transactions:"
echo "      - GET /sentry-debug (500 error)"
echo "      - GET /api/ (multiple, with tags: scan_strategy, scan_success)"
echo "      - GET /api/health (might not appear due to sampling)"
echo ""
echo "   🏷️  Tags to filter by:"
echo "      - scan_strategy: ai_first"
echo "      - scan_success: true"
echo "      - request_type: api"
echo "      - framework: fastapi"
echo "      - deployment_region: local"
echo ""
echo "   🍞 Breadcrumbs to look for:"
echo "      - 'Starting competitor scan for: Nike'"
echo "      - 'Scan completed: X competitors found'"
echo "      - 'Results saved to database' (if Supabase configured)"
echo ""
echo "════════════════════════════════════════════════════════════════"

