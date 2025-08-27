BASE_URL="http://127.0.0.1:8000"
POLYGON_API_KEY="your-fmp-key-here"

echo "=== Futures Contracts ==="
# endpoint not implemented
curl -s "${BASE_URL}/api/v1/futures/contracts?apikey=${POLYGON_API_KEY}" | jq '.'

echo "=== Futures Snapshot ==="
# endpoint not implemented
curl -s "${BASE_URL}/api/v1/futures/${SYMBOL}/snapshot?apikey=${POLYGON_API_KEY}" | jq '.'

echo "=== Futures Historical ==="
# endpoint not implemented
curl -s "${BASE_URL}/api/v1/futures/${SYMBOL}/historical?apikey=${POLYGON_API_KEY}" | jq '.'
