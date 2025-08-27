BASE_URL="http://127.0.0.1:8000"
FMP_API_KEY="your-fmp-key-here"
SYMBOL="AAPL"

echo "=== Income Statement ==="
curl -s "${BASE_URL}/api/v1/fundamentals/${SYMBOL}/income-statement?apikey=${FMP_API_KEY}" | jq '.'

echo "=== Balance Sheet ==="
curl -s "${BASE_URL}/api/v1/fundamentals/${SYMBOL}/balance-sheet?apikey=${FMP_API_KEY}" | jq '.'

echo "=== Cash Flow ==="
curl -s "${BASE_URL}/api/v1/fundamentals/${SYMBOL}/cash-flow?apikey=${FMP_API_KEY}" | jq '.'

echo "=== Ratios ==="
curl -s "${BASE_URL}/api/v1/fundamentals/${SYMBOL}/ratios?apikey=${FMP_API_KEY}" | jq '.'

echo "=== Metrics ==="
 # discontinued FMP endpoint (legacy)
curl -s "${BASE_URL}/api/v1/fundamentals/${SYMBOL}/metrics?apikey=${FMP_API_KEY}" | jq '.'

echo "=== Growth ==="
# discontinued FMP endpoint (legacy)
curl -s "${BASE_URL}/api/v1/fundamentals/${SYMBOL}/growth?apikey=${FMP_API_KEY}" | jq '.'
