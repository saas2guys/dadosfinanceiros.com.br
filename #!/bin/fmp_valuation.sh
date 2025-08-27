BASE_URL="http://127.0.0.1:8000"
FMP_API_KEY="your-fmp-key-here"
SYMBOL="AAPL"

echo "=== DCF Valuation ==="
curl -s "${BASE_URL}/api/v1/valuation/${SYMBOL}/dcf?apikey=${FMP_API_KEY}" | jq '.'

echo "=== Enterprise Value ==="
curl -s "${BASE_URL}/api/v1/valuation/${SYMBOL}/enterprise-value?apikey=${FMP_API_KEY}" | jq '.'