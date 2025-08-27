BASE_URL="http://127.0.0.1:8000"
FMP_API_KEY="your-fmp-key-here"
SYMBOL="AAPL"

echo "=== SEC Filings ==="
curl -s "${BASE_URL}/api/v1/sec/${SYMBOL}/filings?apikey=${FMP_API_KEY}" | jq '.'

echo "=== SEC 10k ==="
# discontinued FMP endpoint (legacy)
curl -s "${BASE_URL}/api/v1/sec/${SYMBOL}/10k?apikey=${FMP_API_KEY}" | jq '.'

echo "=== SEC 10q ==="
# discontinued FMP endpoint (legacy)
curl -s "${BASE_URL}/api/v1/sec/${SYMBOL}/10q?apikey=${FMP_API_KEY}" | jq '.'

echo "=== SEC 8k ==="
# discontinued FMP endpoint (legacy)
curl -s "${BASE_URL}/api/v1/sec/${SYMBOL}/8k?apikey=${FMP_API_KEY}" | jq '.'

echo "=== SEC RSS Feed ==="
# discontinued FMP endpoint (legacy)
curl -s "${BASE_URL}/api/v1/sec/rss-feed?apikey=${FMP_API_KEY}" | jq '.'
