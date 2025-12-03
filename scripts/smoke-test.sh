#!/bin/bash

# Smoke Test Script for Backend API
# Validates that deployed backend is functioning correctly

set -e

# Configuration
BACKEND_URL="${BACKEND_URL:-https://shopsmart-backend-staging.azurewebsites.net}"
MAX_RETRIES=3
RETRY_DELAY=5

echo "🧪 Running Smoke Tests for Backend API"
echo "Backend URL: $BACKEND_URL"
echo ""

# Function to test endpoint
test_endpoint() {
    local endpoint=$1
    local expected_status=$2
    local description=$3

    echo "Testing: $description"
    echo "  Endpoint: $endpoint"

    for i in $(seq 1 $MAX_RETRIES); do
        response=$(curl -s -o /dev/null -w "%{http_code}" "$BACKEND_URL$endpoint" || echo "000")

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

# Function to test endpoint with JSON response
test_json_endpoint() {
    local endpoint=$1
    local expected_key=$2
    local description=$3

    echo "Testing: $description"
    echo "  Endpoint: $endpoint"

    response=$(curl -s "$BACKEND_URL$endpoint" || echo "")

    if [ -z "$response" ]; then
        echo "  ❌ FAIL: Empty response"
        return 1
    fi

    if echo "$response" | grep -q "$expected_key"; then
        echo "  ✅ PASS: Response contains '$expected_key'"
        echo "  Response preview: $(echo "$response" | head -c 100)..."
        return 0
    else
        echo "  ❌ FAIL: Response missing '$expected_key'"
        echo "  Response: $response"
        return 1
    fi
}

# Run tests
FAILED=0

echo "=== Test 1: Health Check ==="
test_endpoint "/health" "200" "Health check endpoint" || FAILED=$((FAILED + 1))
echo ""

echo "=== Test 2: Root Endpoint ==="
test_json_endpoint "/" "message" "Root endpoint returns JSON" || FAILED=$((FAILED + 1))
echo ""

echo "=== Test 3: API Documentation ==="
test_endpoint "/docs" "200" "API documentation accessible" || FAILED=$((FAILED + 1))
echo ""

echo "=== Test 4: Supermarkets Endpoint ==="
test_json_endpoint "/api/v1/supermarkets/" "id" "Supermarkets endpoint returns data" || FAILED=$((FAILED + 1))
echo ""

echo "=== Test 5: Products Endpoint ==="
test_json_endpoint "/api/v1/products/" "id" "Products endpoint returns data" || FAILED=$((FAILED + 1))
echo ""

# Summary
echo "=== Test Summary ==="
if [ $FAILED -eq 0 ]; then
    echo "✅ All smoke tests passed!"
    exit 0
else
    echo "❌ $FAILED test(s) failed"
    exit 1
fi
