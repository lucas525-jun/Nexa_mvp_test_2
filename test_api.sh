#!/bin/bash

# Nexa Test #2 - Complete Workflow Test Script
# This script demonstrates the full order lifecycle

set -e

BASE_URL="http://localhost:8000/api/v1"
TIMESTAMP=$(date -u +"%Y-%m-%dT%H:%M:%SZ")

echo "========================================="
echo "Nexa Test #2 - API Workflow Test"
echo "========================================="
echo ""

# 1. Get all masters
echo "1. Getting all available masters..."
curl -s -X GET "${BASE_URL}/masters" | python3 -m json.tool
echo ""
echo ""

# 2. Create an order
echo "2. Creating a new order..."
ORDER_RESPONSE=$(curl -s -X POST "${BASE_URL}/orders" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Fix electrical wiring",
    "description": "Outlet not working in kitchen",
    "customer": {
      "name": "John Doe",
      "phone": "+1234567890"
    },
    "geo": {
      "lat": 40.7128,
      "lng": -74.0060
    }
  }')

echo "$ORDER_RESPONSE" | python3 -m json.tool
ORDER_ID=$(echo "$ORDER_RESPONSE" | python3 -c "import sys, json; print(json.load(sys.stdin)['id'])")
echo ""
echo "Order ID: $ORDER_ID"
echo ""

# 3. Assign master to order
echo "3. Assigning master to order $ORDER_ID..."
curl -s -X POST "${BASE_URL}/orders/${ORDER_ID}/assign" | python3 -m json.tool
echo ""
echo ""

# 4. Attach ADL media
echo "4. Attaching ADL media to order $ORDER_ID..."
curl -s -X POST "${BASE_URL}/orders/${ORDER_ID}/adl" \
  -H "Content-Type: application/json" \
  -d "{
    \"type\": \"photo\",
    \"url\": \"/uploads/order_${ORDER_ID}_photo.jpg\",
    \"gps\": {
      \"lat\": 40.7128,
      \"lng\": -74.0060
    },
    \"capturedAt\": \"${TIMESTAMP}\",
    \"meta\": {
      \"device\": \"iPhone 14\",
      \"fileSize\": \"2.5MB\"
    }
  }" | python3 -m json.tool
echo ""
echo ""

# 5. Try to complete without valid ADL (should fail - commented out to test with valid ADL)
# echo "5. Attempting to complete order without valid ADL (should fail)..."
# curl -s -X POST "${BASE_URL}/orders/${ORDER_ID}/complete" | python3 -m json.tool
# echo ""

# 6. Complete the order
echo "5. Completing order $ORDER_ID..."
curl -s -X POST "${BASE_URL}/orders/${ORDER_ID}/complete" | python3 -m json.tool
echo ""
echo ""

# 7. Get final order details
echo "6. Getting final order details..."
curl -s -X GET "${BASE_URL}/orders/${ORDER_ID}" | python3 -m json.tool
echo ""
echo ""

echo "========================================="
echo "Workflow completed successfully!"
echo "========================================="
