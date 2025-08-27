BASE_URL="http://127.0.0.1:8000"
FMP_API_KEY="your-fmp-key-here"
SYMBOL="AAPL"

echo "=== Company News ==="
# discontinued FMP endpoint (legacy)
curl -s "${BASE_URL}/api/v1/news/${SYMBOL}?apikey=${FMP_API_KEY}" | jq '.'

echo "=== General News ==="
# discontinued FMP endpoint (legacy)
curl -s "${BASE_URL}/api/v1/news?apikey=${FMP_API_KEY}" | jq '.'

echo "=== Sentiment ==="
# discontinued FMP endpoint (legacy)
curl -s "${BASE_URL}/api/v1/news/sentiment/${SYMBOL}?apikey=${FMP_API_KEY}" | jq '.'

echo "=== Press Releases ==="
# discontinued FMP endpoint (legacy)
curl -s "${BASE_URL}/api/v1/news/press-releases/${SYMBOL}?apikey=${FMP_API_KEY}" | jq '.'