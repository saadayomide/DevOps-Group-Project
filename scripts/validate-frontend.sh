#!/bin/bash

# Frontend Validation Script
# Validates that deployed frontend loads correctly

set -e

# Configuration
FRONTEND_URL="${FRONTEND_URL:-https://shopsmart-frontend-staging.azurewebsites.net}"
MAX_RETRIES=3
RETRY_DELAY=5

echo "🧪 Validating Frontend Deployment"
echo "Frontend URL: $FRONTEND_URL"
echo ""

# Function to test endpoint
test_endpoint() {
    local expected_status=$1
    local description=$2

    echo "Testing: $description"

    for i in $(seq 1 $MAX_RETRIES); do
        response=$(curl -s -o /dev/null -w "%{http_code}" "$FRONTEND_URL" || echo "000")

        if [ "$response" = "$expected_status" ]; then
            echo "  ✅ PASS: HTTP $response"
            return 0
        else
            echo "  ⚠️  Attempt $i/$MAX_RETRIES: HTTP $response (expected $expected_status)"
            if [ $i -lt $MAX_RETRIES ]; then
                sleep $RETRY_DELAY
            fi
        fi
    done

    echo "  ❌ FAIL: Expected HTTP $expected_status, got $response"
    return 1
}

# Function to validate HTML structure
validate_html() {
    echo "Validating HTML structure..."

    html=$(curl -s "$FRONTEND_URL" || echo "")

    if [ -z "$html" ]; then
        echo "  ❌ FAIL: Empty response"
        return 1
    fi

    # Check for React root div
    if echo "$html" | grep -q 'id="root"'; then
        echo "  ✅ PASS: React root element found"
    else
        echo "  ⚠️  WARNING: React root element not found"
    fi

    # Check for script tags
    if echo "$html" | grep -q '<script'; then
        echo "  ✅ PASS: JavaScript bundles found"
    else
        echo "  ⚠️  WARNING: No script tags found"
    fi

    # Check for title
    if echo "$html" | grep -q '<title'; then
        echo "  ✅ PASS: HTML title found"
    else
        echo "  ⚠️  WARNING: No title tag found"
    fi

    return 0
}

# Run tests
FAILED=0

echo "=== Test 1: Frontend Loads ==="
test_endpoint "200" "Frontend returns HTTP 200" || FAILED=$((FAILED + 1))
echo ""

echo "=== Test 2: HTML Structure ==="
validate_html || FAILED=$((FAILED + 1))
echo ""

echo "=== Test 3: No Mixed Content ==="
html=$(curl -s "$FRONTEND_URL" || echo "")
if echo "$html" | grep -q 'http://'; then
    echo "  ⚠️  WARNING: Found HTTP URLs (mixed content risk)"
else
    echo "  ✅ PASS: No HTTP URLs found"
fi
echo ""

# Summary
echo "=== Validation Summary ==="
if [ $FAILED -eq 0 ]; then
    echo "✅ Frontend validation passed!"
    exit 0
else
    echo "❌ $FAILED validation(s) failed"
    exit 1
fi
