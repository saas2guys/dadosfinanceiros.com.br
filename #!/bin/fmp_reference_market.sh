BASE_URL="http://127.0.0.1:8000"
FMP_API_KEY="your-fmp-key-here"

echo "=== Reference Data Exchanges ==="
curl -s "${BASE_URL}/api/v1/reference/exchanges?apikey=${FMP_API_KEY}" | jq '.'

echo "=== Reference Data Sectors ==="
# endpoint not implemented
curl -s "${BASE_URL}/api/v1/reference/sectors?apikey=${FMP_API_KEY}" | jq '.'

echo "=== Reference Data Industries ==="
# endpoint not implemented
curl -s "${BASE_URL}/api/v1/reference/industries?apikey=${FMP_API_KEY}" | jq '.'

echo "=== Reference Data Countries ==="
# endpoint not implemented
curl -s "${BASE_URL}/api/v1/reference/countries?apikey=${FMP_API_KEY}" | jq '.'

echo "=== Reference Data Market Status ==="
# discontinued FMP endpoint (legacy)
curl -s "${BASE_URL}/api/v1/reference/market-status?apikey=${FMP_API_KEY}" | jq '.'

echo "=== Reference Data Market Holidays ==="
# endpoint not implemented
curl -s "${BASE_URL}/api/v1/reference/market-holidays?apikey=${FMP_API_KEY}" | jq '.'

echo "=== Reference Data Trading Hours ==="
# endpoint not implemented
curl -s "${BASE_URL}/api/v1/reference/trading-hours?apikey=${FMP_API_KEY}" | jq '.'
