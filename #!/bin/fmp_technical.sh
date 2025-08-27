BASE_URL="http://127.0.0.1:8000"
FMP_API_KEY="your-fmp-key-here"
SYMBOL="AAPL"

# discontinued FMP endpoint (legacy)
echo "=== Technical ==="
curl -s "${BASE_URL}/api/v1/technical/${SYMBOL}/rsi?period=14&apikey=${FMP_API_KEY}" | jq '.'