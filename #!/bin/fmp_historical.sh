BASE_URL="http://127.0.0.1:8000"
FMP_API_KEY="your-fmp-key-here"
SYMBOL="AAPL"

echo "=== Historical Daily Prices ==="
curl -s "${BASE_URL}/api/v1/historical/${SYMBOL}?apikey=${FMP_API_KEY}" | jq '.'

echo "=== Intraday Prices ==="
# discontinued FMP endpoint (legacy)
curl -s "${BASE_URL}/api/v1/historical/${SYMBOL}/intraday?apikey=${FMP_API_KEY}" | jq '.'

echo "=== Splits ==="
# discontinued FMP endpoint (legacy)
curl -s "${BASE_URL}/api/v1/historical/${SYMBOL}/splits?apikey=${FMP_API_KEY}" | jq '.'

echo "=== Dividends ==="
curl -s "${BASE_URL}/api/v1/historical/${SYMBOL}/dividends?apikey=${FMP_API_KEY}" | jq '.'
