BASE_URL="http://127.0.0.1:8000"
FMP_API_KEY="your-fmp-key-here"

echo "=== GDP ==="
# discontinued FMP endpoints (legacy)
curl -s "${BASE_URL}/api/v1/economy/gdp?apikey=${FMP_API_KEY}" | jq '.'

echo "=== Inflation ==="
# discontinued FMP endpoints (legacy)
curl -s "${BASE_URL}/api/v1/economy/inflation?apikey=${FMP_API_KEY}" | jq '.'
