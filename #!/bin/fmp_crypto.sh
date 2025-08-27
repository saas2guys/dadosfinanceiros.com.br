BASE_URL="http://127.0.0.1:8000"
FMP_API_KEY="your-fmp-key-here"
SYMBOL="AAPL"

echo "=== Crypto Prices ==="
# discontinued FMP endpoint (legacy)
curl -s "${BASE_URL}/api/v1/crypto/prices?apikey=${FMP_API_KEY}" | jq '.'

echo "=== Crypto Market Cap ==="
# not implemented
curl -s "${BASE_URL}/api/v1/crypto/market-cap?apikey=${FMP_API_KEY}" | jq '.'

echo "=== Crypto Historical ==="
curl -s "${BASE_URL}/api/v1/crypto/${SYMBOL}/historical?apikey=${FMP_API_KEY}" | jq '.'

echo "=== Crypto Intraday ==="
# discontinued FMP endpoint (legacy)
curl -s "${BASE_URL}/api/v1/crypto/${SYMBOL}/intraday?apikey=${FMP_API_KEY}" | jq '.'

