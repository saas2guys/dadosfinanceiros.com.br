BASE_URL="http://127.0.0.1:8000"
POLYGON_API_KEY="your-fmp-key-here"
SYMBOL="AAPL"
CONTRACT="AAPL250829C00190000"

echo "=== Options Chain ==="
curl -s "${BASE_URL}/api/v1/options/chain/${SYMBOL}?apikey=${POLYGON_API_KEY}" | jq '.'

echo "=== Options Snapshot ==="
curl -s "${BASE_URL}/api/v1/options/${SYMBOL}/snapshot?apikey=${POLYGON_API_KEY}" | jq '.'

echo "=== Options Contracts ==="
# endpoint not implemented
GET "${BASE_URL}/api/v1/options//api/v1/options/contracts?apikey=${POLYGON_API_KEY}" | jq '.'

echo "=== Options Contracts Details ==="
GET "${BASE_URL}/api/v1/options/${CONTRACT}/details?apikey=${POLYGON_API_KEY}" | jq '.'

echo "=== Options Contracts Historical ==="
GET "${BASE_URL}/api/v1/options/${CONTRACT}/historical?apikey=${POLYGON_API_KEY}" | jq '.'
