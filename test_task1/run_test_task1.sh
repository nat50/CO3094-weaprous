#!/bin/bash

SERVER="http://127.0.0.1:9000"
PASSED=0
FAILED=0

echo "==================================="
echo "WeApRous Authentication Test Suite"
echo "==================================="
echo ""

# Test 1: Valid Login
echo "[Test 1] Valid login credentials..."
RESPONSE=$(curl -s -o /dev/null -w "%{http_code}" -X POST $SERVER/login \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=admin&password=password")
if [ "$RESPONSE" = "302" ]; then
  echo "✓ PASSED - Got 302 Found"
  PASSED=$((PASSED + 1))
else
  echo "✗ FAILED - Expected 302, got $RESPONSE"
  FAILED=$((FAILED + 1))
fi
echo ""

# Test 2: Invalid Login
echo "[Test 2] Invalid login credentials..."
RESPONSE=$(curl -s -o /dev/null -w "%{http_code}" -X POST $SERVER/login \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=admin&password=wrong")
if [ "$RESPONSE" = "401" ]; then
  echo "✓ PASSED - Got 401 Unauthorized"
  PASSED=$((PASSED + 1))
else
  echo "✗ FAILED - Expected 401, got $RESPONSE"
  FAILED=$((FAILED + 1))
fi
echo ""

# Test 3: Access without cookie
echo "[Test 3] Access root without cookie..."
RESPONSE=$(curl -s -o /dev/null -w "%{http_code}" -X GET $SERVER/)
if [ "$RESPONSE" = "401" ]; then
  echo "✓ PASSED - Got 401 Unauthorized"
  PASSED=$((PASSED + 1))
else
  echo "✗ FAILED - Expected 401, got $RESPONSE"
  FAILED=$((FAILED + 1))
fi
echo ""

# Test 4: Access with valid cookie
echo "[Test 4] Access root with valid cookie..."
RESPONSE=$(curl -s -o /dev/null -w "%{http_code}" -X GET $SERVER/ \
  -H "Cookie: auth=true")
if [ "$RESPONSE" = "200" ]; then
  echo "✓ PASSED - Got 200 OK"
  PASSED=$((PASSED + 1))
else
  echo "✗ FAILED - Expected 200, got $RESPONSE"
  FAILED=$((FAILED + 1))
fi
echo ""

# Test 5: Access with invalid cookie
echo "[Test 5] Access root with invalid cookie..."
RESPONSE=$(curl -s -o /dev/null -w "%{http_code}" -X GET $SERVER/ \
  -H "Cookie: auth=false")
if [ "$RESPONSE" = "401" ]; then
  echo "✓ PASSED - Got 401 Unauthorized"
  PASSED=$((PASSED + 1))
else
  echo "✗ FAILED - Expected 401, got $RESPONSE"
  FAILED=$((FAILED + 1))
fi
echo ""

# Summary
echo "==================================="
echo "Test Results:"
echo "PASSED: $PASSED"
echo "FAILED: $FAILED"
echo "==================================="

# Cleanup
rm -f cookies.txt

exit $FAILED