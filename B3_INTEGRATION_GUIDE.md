# B3 Brazilian Market Integration Guide

## Overview

This implementation extends the existing Polygon.io proxy to support Brazilian B3 market data through a unified API interface. The same endpoints now serve both US (Polygon.io) and Brazilian (B3) market data with identical response formats.

## Features

✅ **Unified API Interface** - Same endpoint structure for both markets  
✅ **Automatic Ticker Conversion** - US tickers automatically convert to Brazilian BDRs  
✅ **Multiple Data Sources** - Fallback system with B3 Official → Cedro → Free APIs  
✅ **Backward Compatibility** - Existing US endpoints continue to work  
✅ **Consistent Response Format** - All responses match Polygon.io structure  
✅ **Brazilian Market Hours** - Accurate B3 trading session detection  

## URL Structure

### New Unified Format
```
/v1/{market}/{polygon_path}
```

- **market**: `us` (Polygon.io) or `br` (B3)
- **polygon_path**: Standard Polygon.io API path

### Examples

```bash
# US Market (existing functionality)
GET /v1/us/v2/aggs/ticker/AAPL/range/1/day/2023-01-01/2023-12-31
GET /v1/us/v2/last/trade/MSFT
GET /v1/us/v2/last/nbbo/GOOGL

# Brazilian Market (new functionality)  
GET /v1/br/v2/aggs/ticker/PETR4/range/1/day/2023-01-01/2023-12-31
GET /v1/br/v2/last/trade/VALE3
GET /v1/br/v2/last/nbbo/ITUB4

# Automatic Ticker Conversion
GET /v1/br/v2/last/trade/AAPL    # Converts AAPL → AAPL34
GET /v1/br/v2/last/trade/TSLA    # Converts TSLA → TSLA34
```

### Backward Compatibility

Old format automatically redirects to US market:
```bash
# Legacy format (redirects to /v1/us/...)
GET /v1/v2/last/trade/AAPL
```

## Supported Endpoints

### Aggregates (Historical Data)
```bash
# US Market
GET /v1/us/v2/aggs/ticker/{ticker}/range/{multiplier}/{timespan}/{from}/{to}

# Brazilian Market  
GET /v1/br/v2/aggs/ticker/{ticker}/range/{multiplier}/{timespan}/{from}/{to}
```

**Response Format:**
```json
{
  "results": [
    {
      "c": 150.25,     // Close price
      "h": 152.00,     // High price
      "l": 149.50,     // Low price
      "o": 151.00,     // Open price
      "t": 1640995200000, // Timestamp (ms)
      "v": 1000000,    // Volume
      "vw": 150.75,    // Volume weighted average price
      "n": 15000       // Number of transactions
    }
  ],
  "resultsCount": 1,
  "adjusted": true
}
```

### Last Trade
```bash
# US Market
GET /v1/us/v2/last/trade/{ticker}

# Brazilian Market
GET /v1/br/v2/last/trade/{ticker}
```

**Response Format:**
```json
{
  "results": {
    "conditions": [1],
    "exchange": 147,   // B3 exchange ID for BR market
    "price": 150.25,
    "size": 100,
    "timestamp": 1640995200000000000,
    "timeframe": "REAL-TIME"
  }
}
```

### Last Quote (NBBO)
```bash
# US Market
GET /v1/us/v2/last/nbbo/{ticker}

# Brazilian Market
GET /v1/br/v2/last/nbbo/{ticker}
```

**Response Format:**
```json
{
  "results": {
    "ask": 150.30,
    "ask_exchange": 147,
    "ask_size": 100,
    "bid": 150.20,
    "bid_exchange": 147,
    "bid_size": 100,
    "exchange": 147,
    "timestamp": 1640995200000000000
  }
}
```

## Ticker Conversion

The system automatically converts US tickers to Brazilian BDRs when using the `br` market:

### US ADR/BDR Mappings
| US Ticker | Brazilian BDR | Company |
|-----------|---------------|---------|
| AAPL      | AAPL34       | Apple |
| MSFT      | MSFT34       | Microsoft |
| GOOGL     | GOGL34       | Google |
| TSLA      | TSLA34       | Tesla |
| AMZN      | AMZO34       | Amazon |
| META      | M1TA34       | Meta |
| NVDA      | NVDC34       | NVIDIA |
| NFLX      | NFLX34       | Netflix |

### Popular Brazilian Stocks
These pass through without conversion:
- **PETR4** (Petrobras)
- **VALE3** (Vale)
- **ITUB4** (Itaú)
- **BBDC4** (Bradesco)
- **ABEV3** (Ambev)
- **And many more...**

## Configuration

Add these environment variables to your `.env` file:

### Required for B3 Official API
```bash
# B3 Official Market Data API
B3_API_KEY=your_b3_api_key
B3_BASE_URL=https://api-marketdata.b3.com.br
```

### Optional Fallback APIs
```bash
# Cedro Technologies API (fallback)
CEDRO_API_KEY=your_cedro_api_key
CEDRO_BASE_URL=https://api.cedrotech.com

# Free B3 Historical Data (fallback)
B3_HISTORICAL_URL=https://cvscarlos.github.io/b3-api-dados-historicos/api/v1
```

### Existing Polygon.io Configuration
```bash
# Keep existing Polygon.io settings
POLYGON_API_KEY=your_polygon_api_key
POLYGON_BASE_URL=https://api.polygon.io
```

## Data Sources & Fallback Logic

The Brazilian market implementation uses a sophisticated fallback system:

### 1. Primary: B3 Official API
- **URL**: `https://api-marketdata.b3.com.br`
- **Coverage**: Real-time and historical data
- **Requires**: B3_API_KEY

### 2. Fallback: Cedro Technologies
- **URL**: `https://api.cedrotech.com`
- **Coverage**: Real-time quotes and historical data
- **Requires**: CEDRO_API_KEY

### 3. Last Resort: Free B3 Historical
- **URL**: `https://cvscarlos.github.io/b3-api-dados-historicos/api/v1`
- **Coverage**: Historical data only
- **Requires**: No API key

## Market Hours

Brazilian market hours are automatically detected:

### B3 Trading Hours
- **Open**: 10:00 AM BRT (UTC-3)
- **Close**: 5:30 PM BRT (UTC-3)
- **Days**: Monday to Friday
- **Timezone**: America/Sao_Paulo

### Market Status Response
```json
{
  "results": {
    "afterHours": false,
    "market": "open",
    "preMarket": false,
    "serverTime": "2023-12-01T14:30:00-03:00"
  }
}
```

## Testing

Run the included test script to verify functionality:

```bash
# Make the test script executable
chmod +x test_b3_proxy.py

# Run tests
python test_b3_proxy.py
```

### Expected Test Results
```
🚀 Testing Unified Polygon/B3 Proxy
==================================================

🧪 Testing: US Last Trade - AAPL
📡 URL: http://localhost:8000/v1/us/v2/last/trade/AAPL
✅ Status: 200
📊 Response keys: ['results']
📈 Result keys: ['conditions', 'exchange', 'price', 'size', 'timestamp', 'timeframe']

[... more tests ...]

==================================================
📊 Test Results: 9/9 passed
🎉 All tests passed!
```

## Error Handling

### Invalid Market Parameter
```bash
GET /v1/invalid/v2/last/trade/AAPL
```
```json
{
  "status": "ERROR",
  "error": "Invalid market 'invalid'. Use 'us' or 'br'",
  "request_id": "proxy_1640995200.123"
}
```

### No B3 Data Available
```bash
GET /v1/br/v2/last/trade/UNKNOWN
```
```json
{
  "status": "ERROR",
  "error": "No data available from any B3 source",
  "request_id": "proxy_1640995200.456"
}
```

### Timeout Errors
```json
{
  "error": "Gateway Timeout",
  "message": "The request timed out"
}
```

## Implementation Notes

### Response Format Consistency
All Brazilian market responses are converted to match Polygon.io format exactly, ensuring:
- ✅ Same field names (`c`, `h`, `l`, `o`, `t`, `v`, `vw`, `n`)
- ✅ Same data types (numbers for prices, timestamps in milliseconds)
- ✅ Same structure (`results` array/object, `resultsCount`, etc.)
- ✅ Same HTTP status codes

### Authentication
- Uses existing JWT/Token authentication system
- Same rate limiting applies to both markets
- User request counts are incremented for both US and BR markets

### Logging
All requests are logged with market identifier:
```
INFO: Forwarding GET request for br market to: v2/last/trade/PETR4 by user: user@example.com
```

## Migration from Existing Implementation

### For Existing Users
No changes required - all existing endpoints continue to work:
```bash
# This still works (redirects to /v1/us/...)
GET /v1/v2/last/trade/AAPL
```

### For New Brazilian Market Users
Simply add the `br` market parameter:
```bash
# New Brazilian market endpoints
GET /v1/br/v2/last/trade/PETR4
GET /v1/br/v2/aggs/ticker/VALE3/range/1/day/2023-01-01/2023-12-31
```

## Performance Considerations

### Caching
- Consider implementing Redis caching for B3 responses
- Cache timeouts should respect market hours
- Historical data can be cached longer than real-time data

### Rate Limiting
- B3 APIs may have different rate limits than Polygon.io
- Consider separate rate limiting buckets per market
- Implement exponential backoff for fallback APIs

### Monitoring
- Monitor success rates for each B3 data source
- Track fallback API usage
- Set up alerts for API failures

## Future Enhancements

### Planned Features
- 🔄 **Real-time WebSocket support** for B3 market data
- 📊 **Extended market data** (options, futures)
- 🌍 **Additional Latin American markets** (Argentina, Mexico)
- 📈 **Advanced indicators** specific to Brazilian market
- 🔍 **Enhanced ticker search** and symbol lookup

### API Versioning
Future versions may include:
- `/v2/` endpoints with enhanced Brazilian market features
- Market-specific metadata endpoints
- Currency conversion utilities

---

## Support

For questions or issues:
1. Check the test script output for specific error messages
2. Verify environment variables are set correctly
3. Check API key validity for each data source
4. Review logs for detailed error information

**Happy trading with unified US and Brazilian market data! 🚀📈** 