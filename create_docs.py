#!/usr/bin/env python3
"""Generate unified API documentation"""

doc_content = """# Unified Financial Data API - Complete Guide

## 🚀 Overview

This comprehensive financial data API unifies **150+ endpoints** from both Polygon.io and Financial Modeling Prep (FMP) Ultimate under a single `/api/v1/` structure. The system intelligently routes requests to the optimal provider based on data type, coverage, and cost efficiency.

## 📊 Provider Strengths & Routing Strategy

### Polygon.io Strengths
- **🎯 US Options with Greeks** (Delta, Gamma, Theta, Vega, IV)
- **📈 US Futures** (4 CME Group exchanges)
- **⚡ Tick-level US Data** (Highest resolution)
- **🔴 Real-time US WebSockets**
- **🔧 Advanced US Market Operations**

### FMP Ultimate Strengths  
- **🌍 Global Stock Coverage** (70+ exchanges)
- **📋 Comprehensive Fundamentals** (30+ years history)
- **📰 News & Sentiment Analysis**
- **💰 Economic Indicators**
- **📞 Earnings Transcripts**
- **🏛️ Institutional Holdings**
- **👨‍💼 Analyst Estimates & Recommendations**
- **📄 SEC Filings**

## 🗺️ Complete API Endpoint Map

### 1. 📊 Market Data Endpoints

#### Real-time Quotes & Market Data
```bash
# Real-time quote data
GET /api/v1/quotes/{symbol}
GET /api/v1/quotes/batch?symbols=AAPL,MSFT,GOOGL

# Market snapshots
GET /api/v1/quotes/gainers
GET /api/v1/quotes/losers
GET /api/v1/quotes/active
```

#### Historical Price Data
```bash
# Historical pricing
GET /api/v1/historical/{symbol}
GET /api/v1/historical/{symbol}/intraday

# Corporate actions
GET /api/v1/historical/{symbol}/splits
GET /api/v1/historical/{symbol}/dividends
```

### 2. 🎯 Options Data (Polygon.io Exclusive)

```bash
# Options contracts and chains
GET /api/v1/options/contracts
GET /api/v1/options/chain/{symbol}
GET /api/v1/options/{symbol}/snapshot

# Contract details and history
GET /api/v1/options/{contract}/details
GET /api/v1/options/{contract}/historical
```

### 3. 📈 Futures Data (Polygon.io Exclusive)

```bash
# Futures contracts
GET /api/v1/futures/contracts
GET /api/v1/futures/{symbol}/snapshot
GET /api/v1/futures/{symbol}/historical
```

### 4. 🏢 Fundamental Data (FMP Exclusive)

#### Financial Statements
```bash
# Core financial statements
GET /api/v1/fundamentals/{symbol}/income-statement
GET /api/v1/fundamentals/{symbol}/balance-sheet
GET /api/v1/fundamentals/{symbol}/cash-flow

# Financial metrics
GET /api/v1/fundamentals/{symbol}/ratios
GET /api/v1/fundamentals/{symbol}/metrics
GET /api/v1/fundamentals/{symbol}/growth
```

#### Valuation & Analysis
```bash
# Valuation models
GET /api/v1/valuation/{symbol}/dcf
GET /api/v1/valuation/{symbol}/ratios
GET /api/v1/valuation/{symbol}/enterprise-value

# Stock screening
GET /api/v1/valuation/screener?marketCapMoreThan=1000000000
```

### 5. 📰 News & Sentiment (FMP Exclusive)

```bash
# Financial news
GET /api/v1/news
GET /api/v1/news/{symbol}
GET /api/v1/news/press-releases/{symbol}

# Sentiment analysis
GET /api/v1/news/sentiment/{symbol}
```

### 6. 👨‍💼 Analyst Data (FMP Exclusive)

```bash
# Analyst coverage
GET /api/v1/analysts/{symbol}/estimates
GET /api/v1/analysts/{symbol}/recommendations
GET /api/v1/analysts/{symbol}/price-targets
GET /api/v1/analysts/{symbol}/upgrades-downgrades
```

### 7. 📅 Earnings Data (FMP Exclusive)

```bash
# Earnings information
GET /api/v1/earnings/{symbol}/calendar
GET /api/v1/earnings/{symbol}/history
GET /api/v1/earnings/{symbol}/surprises
GET /api/v1/earnings/{symbol}/transcripts
GET /api/v1/earnings/calendar
```

### 8. 🏛️ Institutional Data (FMP Exclusive)

```bash
# Institutional holdings
GET /api/v1/institutional/{symbol}/holdings
GET /api/v1/institutional/{symbol}/13f
GET /api/v1/institutional/funds/{cik}

# Insider trading
GET /api/v1/insider/{symbol}/transactions
GET /api/v1/insider/{symbol}/ownership
```

### 9. 💰 Economic Data (FMP Exclusive)

```bash
# Economic indicators
GET /api/v1/economy/gdp
GET /api/v1/economy/inflation
GET /api/v1/economy/unemployment
GET /api/v1/economy/interest-rates
GET /api/v1/economy/treasury-rates
```

### 10. 📊 Technical Analysis

```bash
# Technical indicators
GET /api/v1/technical/{symbol}/sma?period=20
GET /api/v1/technical/{symbol}/ema?period=12
GET /api/v1/technical/{symbol}/rsi?period=14
GET /api/v1/technical/{symbol}/macd
GET /api/v1/technical/{symbol}/bollinger-bands
GET /api/v1/technical/{symbol}/stochastic
GET /api/v1/technical/{symbol}/adx
GET /api/v1/technical/{symbol}/williams-r
```

### 11. 📄 SEC Filings (FMP Exclusive)

```bash
# SEC documents
GET /api/v1/sec/{symbol}/filings
GET /api/v1/sec/{symbol}/10k
GET /api/v1/sec/{symbol}/10q
GET /api/v1/sec/{symbol}/8k
GET /api/v1/sec/rss-feed
```

### 12. 🏦 ETF & Mutual Fund Data (FMP Exclusive)

```bash
# ETF data
GET /api/v1/etf/list
GET /api/v1/etf/{symbol}/holdings
GET /api/v1/etf/{symbol}/performance

# Mutual funds
GET /api/v1/funds/list
GET /api/v1/funds/{symbol}/holdings
```

### 13. 🌍 Global Markets

#### Forex
```bash
# Currency exchange rates
GET /api/v1/forex/rates
GET /api/v1/forex/{pair}/historical
GET /api/v1/forex/{pair}/intraday
```

#### Cryptocurrency
```bash
# Crypto market data
GET /api/v1/crypto/prices
GET /api/v1/crypto/{symbol}/historical
GET /api/v1/crypto/{symbol}/intraday
GET /api/v1/crypto/market-cap
```

#### Commodities
```bash
# Commodity prices
GET /api/v1/commodities/metals
GET /api/v1/commodities/energy
GET /api/v1/commodities/agriculture
GET /api/v1/commodities/{symbol}/historical
```

#### Market Indices
```bash
# Global indices
GET /api/v1/indices/list
GET /api/v1/indices/{symbol}/historical
GET /api/v1/indices/{symbol}/components
```

### 14. 📋 Reference Data

```bash
# Company information
GET /api/v1/reference/tickers
GET /api/v1/reference/ticker/{symbol}
GET /api/v1/reference/ticker/{symbol}/profile
GET /api/v1/reference/ticker/{symbol}/executives
GET /api/v1/reference/ticker/{symbol}/peers

# Market metadata
GET /api/v1/reference/exchanges
GET /api/v1/reference/sectors
GET /api/v1/reference/industries
GET /api/v1/reference/countries
GET /api/v1/reference/market-status
GET /api/v1/reference/market-holidays
GET /api/v1/reference/trading-hours
```

### 15. ⚡ Tick-level Data (Polygon.io Exclusive)

```bash
# Individual trades and quotes
GET /api/v1/ticks/{symbol}/trades
GET /api/v1/ticks/{symbol}/quotes
GET /api/v1/ticks/{symbol}/aggregates
```

### 16. 📦 Bulk Data (FMP Exclusive)

```bash
# Bulk downloads
GET /api/v1/bulk/eod/{date}
GET /api/v1/bulk/fundamentals/{date}
GET /api/v1/bulk/insider-trading/{date}
```

## 🔧 Setup & Configuration

### Environment Variables

Add these to your `.env` file:

```bash
# FMP Ultimate API (NEW - for global markets & fundamentals)
FMP_API_KEY=your_fmp_ultimate_api_key_here
FMP_BASE_URL=https://financialmodelingprep.com/api

# Polygon.io API (existing - for US options, futures, tick data)
POLYGON_API_KEY=your_polygon_api_key_here
POLYGON_BASE_URL=https://api.polygon.io

# General configuration
PROXY_TIMEOUT=30
PROXY_DOMAIN=api.financialdata.online
ENV=local
```

### API Key Setup

#### FMP Ultimate API Key (Required for most endpoints)
1. Visit: https://financialmodelingprep.com/developer/docs
2. Sign up for FMP Ultimate plan
3. Provides: Global stocks, fundamentals, news, analyst data, economic indicators

#### Polygon.io API Key (For US options, futures, tick data)
1. Visit: https://polygon.io/
2. Sign up for appropriate plan
3. Provides: US options with Greeks, futures, tick-level data

## 📝 Response Format

### Unified Response Structure

All new `/api/v1/` endpoints return a consistent format:

```json
{
  "status": "success",
  "data": {
    // Actual financial data from provider
  },
  "metadata": {
    "provider": "fmp" | "polygon",
    "timestamp": "2024-01-15T10:30:00Z",
    "endpoint": "quotes/AAPL",
    "cache_type": "real_time"
  },
  "request_info": {
    "unified_path": "quotes/AAPL",
    "provider_endpoint": "/v3/quote/AAPL",
    "routed_to": "fmp"
  }
}
```

### Cache Types & TTL

- **real_time**: 30 seconds (live quotes, options)
- **intraday**: 5 minutes (intraday charts, technical indicators)
- **daily**: 1 hour (daily data, market status)
- **fundamental**: 24 hours (financial statements, company data)
- **news**: 30 minutes (news articles, sentiment)
- **static**: 7 days (reference data, company profiles)

## 🧪 Testing the API

### Run the Test Script

```bash
# Make sure the server is running
python manage.py runserver

# Run comprehensive tests
python test_unified_api.py
```

### Manual Testing Examples

```bash
# Test FMP endpoints
curl "http://localhost:8000/api/v1/quotes/AAPL"
curl "http://localhost:8000/api/v1/fundamentals/AAPL/income-statement"
curl "http://localhost:8000/api/v1/news/AAPL"

# Test Polygon endpoints  
curl "http://localhost:8000/api/v1/options/chain/AAPL"
curl "http://localhost:8000/api/v1/ticks/AAPL/trades"

# Test legacy endpoints (backward compatibility)
curl "http://localhost:8000/v1/snapshot"
curl "http://localhost:8000/v1/aggs/ticker/AAPL/range/1/day/2023-01-01/2023-12-31"
```

## 🔄 Backward Compatibility

All existing `/v1/` endpoints continue to work unchanged:

- ✅ Legacy Polygon.io proxy endpoints remain functional
- ✅ Authentication and permissions unchanged
- ✅ Response format for legacy endpoints unchanged
- ✅ URL cleaning and transformation preserved

## 🛡️ Security & Rate Limiting

### Rate Limits
- **FMP**: 3,000 calls per minute
- **Polygon**: 1,000 calls per minute

### Authentication (Production)
- JWT token authentication
- Daily request limits per user
- Request token authentication

### Development Mode
- No authentication required when `ENV=local`
- Full access to all endpoints

## 🎯 Provider Selection Logic

The system automatically routes requests to the optimal provider:

1. **Options & Futures**: Always routed to Polygon.io (exclusive)
2. **Fundamentals**: Always routed to FMP Ultimate (exclusive)
3. **News & Sentiment**: Always routed to FMP Ultimate (exclusive)
4. **Analyst Data**: Always routed to FMP Ultimate (exclusive)
5. **Economic Data**: Always routed to FMP Ultimate (exclusive)
6. **SEC Filings**: Always routed to FMP Ultimate (exclusive)
7. **Market Data**: Primary FMP, fallback to Polygon for US markets
8. **Technical Analysis**: Primary FMP, fallback to Polygon for US markets

## 📈 Performance Features

- **Multi-level caching** with Redis
- **Parallel provider calls** for maximum efficiency
- **Intelligent rate limiting** per provider
- **Error handling** with automatic fallbacks
- **Response transformation** to unified format

## 🆕 Migration from Legacy API

### For New Projects
Use the new `/api/v1/` endpoints exclusively for access to all providers and data types.

### For Existing Projects
- Keep using `/v1/` endpoints for backward compatibility
- Gradually migrate to `/api/v1/` endpoints for new features
- Both endpoints work with the same authentication

## 🔍 Troubleshooting

### Common Issues

1. **404 Endpoint Not Found**
   - Check endpoint spelling and structure
   - Verify the endpoint exists in the mapping

2. **Rate Limit Exceeded**
   - Wait for rate limit reset
   - Consider caching responses
   - Upgrade API plan if needed

3. **Provider API Key Missing**
   - Add API keys to environment variables
   - Restart the Django server
   - Check API key validity

4. **Authentication Errors**
   - Verify JWT token is valid
   - Check environment configuration
   - Ensure user has sufficient permissions

### Debug Mode

Set `DEBUG=True` in settings for detailed error information.

## 📞 Support

For issues and questions:
1. Check the test script output for endpoint routing
2. Verify API keys are correctly configured
3. Review Django logs for detailed error information
4. Test individual provider APIs directly to isolate issues

---

**🎉 Congratulations!** You now have access to a comprehensive financial data API with 150+ endpoints covering global markets, fundamentals, options, news, and much more through intelligent provider routing.
"""

# Write the documentation file
with open('UNIFIED_API_GUIDE.md', 'w') as f:
    f.write(doc_content)

print("✅ Unified API documentation created successfully!")
print("📄 File: UNIFIED_API_GUIDE.md")
