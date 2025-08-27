BASE_URL="http://127.0.0.1:8000"
FMP_API_KEY="your-fmp-key-here"
SYMBOL="AAPL"

echo "=== Stock Quote ==="
curl -s "${BASE_URL}/api/v1/quotes/${SYMBOL}?apikey=${FMP_API_KEY}" | jq '.' || echo "Erro JSON"

echo "=== Batch Quotes ==="
# returned null
curl -s "${BASE_URL}/api/v1/quotes/batch?symbols=AAPL,MSFT,GOOGL&apikey=${FMP_API_KEY}" | jq '.'

echo "=== Market Gainers ==="
# discontinued FMP endpoint (legacy)
curl -s "${BASE_URL}/api/v1/quotes/gainers?apikey=${FMP_API_KEY}" | jq '.'

echo "=== Market Losers ==="
# discontinued FMP endpoint (legacy)
curl -s "${BASE_URL}/api/v1/quotes/losers?apikey=${FMP_API_KEY}" | jq '.'

echo "=== Most Active ==="
# discontinued FMP endpoint (legacy)
curl -s "${BASE_URL}/api/v1/quotes/active?apikey=${FMP_API_KEY}" | jq '.'
