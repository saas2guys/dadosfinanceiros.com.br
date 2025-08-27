BASE_URL="http://127.0.0.1:8000"
FMP_API_KEY="your-fmp-key-here"

echo "=== Forex Rates ==="
curl -s "${BASE_URL}/api/v1/forex/rates?apikey=${FMP_API_KEY}" | jq '.'

echo "=== Forex Historical ==="
# discontinued FMP endpoint (legacy)
curl -s "${BASE_URL}/api/v1/forex/${PAIR}/historical?apikey=${FMP_API_KEY}" | jq '.'

echo "=== Forex Intraday ==="
# discontinued FMP endpoint (legacy)
curl -s "${BASE_URL}/api/v1/forex/${PAIR}/intraday?apikey=${FMP_API_KEY}" | jq '.'