BASE_URL="http://127.0.0.1:8000"
FMP_API_KEY="your-fmp-key-here"
SYMBOL="AAPL"

echo "=== Reference Data Tickers ==="
curl -s "${BASE_URL}/api/v1/reference/tickers?apikey=${FMP_API_KEY}" | jq '.'

echo "=== Reference Data Ticker Symbol ==="
# discontinued FMP endpoint (legacy)
curl -s "${BASE_URL}/api/v1/reference/ticker/${SYMBOL}?apikey=${FMP_API_KEY}" | jq '.'

echo "=== Reference Data Ticker Symbol Profile==="
# discontinued FMP endpoint (legacy)
curl -s "${BASE_URL}/api/v1/reference/ticker/${SYMBOL}/profile?apikey=${FMP_API_KEY}" | jq '.'

echo "=== Reference Data Ticker Symbol Executives==="
# discontinued FMP endpoint (legacy)
curl -s "${BASE_URL}/api/v1/reference/ticker/${SYMBOL}/executives?apikey=${FMP_API_KEY}" | jq '.'

echo "=== Reference Data Ticker Symbol Peers==="
# discontinued FMP endpoint (legacy)
curl -s "${BASE_URL}/api/v1/reference/ticker/${SYMBOL}/peers?apikey=${FMP_API_KEY}" | jq '.'

