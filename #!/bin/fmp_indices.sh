BASE_URL="http://127.0.0.1:8000"
FMP_API_KEY="your-fmp-key-here"
SYMBOL="AAPL"

echo "=== Global Indices List ==="
curl -s "${BASE_URL}/api/v1/indices/list?apikey=${FMP_API_KEY}" | jq '.'

echo "=== Global Indices Components ==="
# discontinued FMP endpoint (legacy)
curl -s "${BASE_URL}/api/v1/indices/${SYMBOL}/components?apikey=${FMP_API_KEY}" | jq '.'

echo "=== Global Indices Historical ==="
curl -s "${BASE_URL}/api/v1/indices/${SYMBOL}/historical?apikey=${FMP_API_KEY}" | jq '.'