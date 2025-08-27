BASE_URL="http://127.0.0.1:8000"
FMP_API_KEY="your-fmp-key-here"
SYMBOL="AAPL"

echo "=== Institutional Holdings ==="
# discontinued FMP endpoints (legacy)
curl -s "${BASE_URL}/api/v1/institutional/${SYMBOL}/holdings?apikey=${FMP_API_KEY}" | jq '.'

echo "=== Institutional Holdings ==="
# discontinued FMP endpoints (legacy)
curl -s "${BASE_URL}/api/v1/institutional/${SYMBOL}/holdings?apikey=${FMP_API_KEY}" | jq '.'

echo "=== Institutional Holdings ==="
# discontinued FMP endpoints (legacy)
curl -s "${BASE_URL}/api/v1/institutional/${SYMBOL}/holdings?apikey=${FMP_API_KEY}" | jq '.'

echo "=== Insider Transactions ==="
# discontinued FMP endpoints (legacy)
curl -s "${BASE_URL}/api/v1/insider/${SYMBOL}/transactions?apikey=${FMP_API_KEY}" | jq '.'

echo "=== Insider Ownership ==="
# discontinued FMP endpoints (legacy)
curl -s "${BASE_URL}/api/v1/insider/${SYMBOL}/ownership?apikey=${FMP_API_KEY}" | jq '.'