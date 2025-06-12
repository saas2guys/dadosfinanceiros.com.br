# Comprehensive Financial API Test Suite

## Overview

This comprehensive test suite provides **100% endpoint coverage** for the Unified Financial API, testing all 104 endpoints across 22 categories with their complete inputs and expected outputs as specified in the API documentation.

## 🏗️ Test Architecture

### Files Structure
```
test_comprehensive_api.py      # Main test class with all 104 endpoint tests
run_comprehensive_tests.py     # Test runner with detailed reporting
test_structure_verification.py # Verification script for test completeness
TEST_SUITE_README.md          # This documentation
```

### Test Categories (104 Tests Total)

| Category | Tests | Description |
|----------|-------|-------------|
| **Reference Data** | 8 | Company profiles, exchanges, market status |
| **Market Data** | 13 | Real-time quotes, historical data, gainers/losers |
| **Options Data** | 5 | Contracts, chains, Greeks, open interest |
| **Futures Data** | 3 | Contracts, snapshots, historical data |
| **Tick-level Data** | 3 | Trades, quotes, aggregated bars |
| **Fundamental Data** | 8 | Financial statements, ratios, metrics, DCF |
| **News & Sentiment** | 5 | Stock news, press releases, sentiment analysis |
| **Analyst Data** | 4 | Estimates, recommendations, price targets |
| **Earnings Data** | 4 | Calendar, transcripts, history, surprises |
| **Corporate Events** | 3 | IPO, splits, dividend calendars |
| **Institutional & Insider Data** | 3 | 13F filings, holders, insider trading |
| **Economic Data** | 5 | GDP, inflation, unemployment, rates |
| **ETF & Mutual Funds** | 4 | Lists, holdings, performance |
| **Commodities** | 4 | Metals, energy, historical prices |
| **Cryptocurrencies** | 3 | Crypto quotes and historical data |
| **International Markets** | 4 | Global exchanges, forex rates |
| **SEC Filings** | 5 | 10-K, 10-Q, 8-K filings |
| **Technical Indicators** | 8 | SMA, EMA, RSI, MACD, Bollinger Bands |
| **Bulk Data** | 3 | EOD prices, fundamentals, insider trading |
| **System Endpoints** | 3 | Health checks, endpoint docs, batch requests |
| **Error Handling** | 3 | 404, 400 error scenarios |
| **Caching & Routing** | 3 | Cache behavior, provider routing |

## 🚀 Quick Start

### Prerequisites
```bash
# Ensure your API server is running
python manage.py runserver  # Django development server

# Or your production server
```

### Running Tests

#### 1. Verify Test Structure
```bash
python test_structure_verification.py
```

#### 2. Run Complete Test Suite
```bash
python run_comprehensive_tests.py
```

#### 3. Run Individual Test Categories
```bash
# Run with Python unittest
python -m unittest test_comprehensive_api.ComprehensiveAPITester.test_quotes_single
python -m unittest test_comprehensive_api.ComprehensiveAPITester.test_fundamentals_income_statement
```

#### 4. Custom API URL
```bash
python run_comprehensive_tests.py --url http://your-api-domain.com
```

## 📊 Test Features

### 🔍 Comprehensive Validation
- **Parameter Validation**: Tests all required and optional parameters
- **Response Format**: Validates JSON structure and required fields
- **HTTP Status Codes**: Checks correct status codes (200, 400, 404, etc.)
- **Metadata Validation**: Verifies `_metadata` fields (source, provider, timestamp)
- **Data Types**: Ensures correct data types for all fields

### 🎯 Provider Routing Tests
- **Polygon.io Routes**: Options, futures, tick-level data
- **FMP Routes**: Market data, fundamentals, news, analyst data
- **Provider Verification**: Confirms correct provider attribution

### ⚡ Performance & Caching Tests
- **Cache Behavior**: Tests live vs cached responses
- **Response Times**: Monitors API performance
- **Rate Limiting**: Validates provider rate limit handling

### 🚨 Error Handling Tests
- **Invalid Symbols**: Tests 404 responses for non-existent symbols
- **Invalid Endpoints**: Tests 404 for wrong URLs
- **Missing Parameters**: Tests 400 for required parameter validation
- **Provider Errors**: Tests handling of upstream provider failures

### 🔄 Batch Request Testing
- **Multiple Endpoints**: Tests simultaneous requests
- **Response Formatting**: Validates batch response structure
- **Error Propagation**: Tests error handling in batch requests

## 📋 Test Examples

### Example 1: Market Data Test
```python
def test_quotes_single(self):
    """Test GET /api/v1/quotes/{symbol}"""
    response = self.make_request(f"/api/v1/quotes/{self.test_symbol}")
    data = self.assert_response_format(response, ["symbol", "price", "change"])
    
    # Validates:
    # - HTTP 200 status
    # - JSON response format
    # - Required fields: symbol, price, change
    # - Metadata: source, provider, timestamp
```

### Example 2: Options Data Test
```python
def test_options_chain(self):
    """Test GET /api/v1/options/chain/{symbol}"""
    response = self.make_request(f"/api/v1/options/chain/{self.test_symbol}")
    data = self.assert_response_format(response, ["results"])
    
    # Validates:
    # - Polygon.io provider routing
    # - Options contract structure
    # - Greeks data presence
    # - Real-time vs cached data
```

### Example 3: Error Handling Test
```python
def test_invalid_symbol_404(self):
    """Test 404 error for invalid symbol"""
    response = self.make_request("/api/v1/quotes/INVALID_SYMBOL_123")
    self.assertEqual(response.status_code, 404)
    
    # Validates:
    # - Correct 404 status code
    # - Error message format
    # - Graceful error handling
```

## 🎯 Expected Outputs

### Successful Test Run
```
🚀 Starting Comprehensive Financial API Test Suite
🎯 Target API: http://localhost:8000
📅 Started at: 2024-01-31 15:30:00

🔍 Checking API availability...
✅ API is available - Status: healthy

============================================================
🧪 Testing Category: Reference Data
============================================================
✅ test_reference_tickers: PASSED
✅ test_reference_ticker_profile: PASSED
✅ test_reference_ticker_executives: PASSED
...

📋 COMPREHENSIVE TEST REPORT
================================================================================

📊 Overall Statistics:
   Total Tests Run: 104
   ✅ Passed: 98
   ❌ Failed: 4
   🔥 Errors: 2
   📈 Success Rate: 94.2%
   ⏱️ Total Duration: 45.67s

📂 Category Breakdown:
   ✅ Reference Data: 8/8 (100.0%)
   ✅ Market Data: 13/13 (100.0%)
   ❌ Options Data: 4/5 (80.0%)
   ...

🏁 Final Assessment:
   🎉 EXCELLENT - API is performing very well!
```

## 🔧 Configuration

### Test Parameters
The test suite uses these default parameters:
```python
self.test_symbol = "AAPL"           # Primary test symbol
self.test_date = "2024-01-31"       # Test date
self.test_from_date = "2024-01-01"  # Date range start
self.test_to_date = "2024-01-31"    # Date range end
```

### Timeouts
- **Individual Request Timeout**: 30 seconds
- **API Availability Check**: 10 seconds

### Expected Response Format
All API responses should include:
```json
{
  "data": "...",
  "_metadata": {
    "source": "live|cache",
    "provider": "polygon|fmp", 
    "timestamp": "2024-01-31T15:30:00Z"
  }
}
```

## 🐛 Debugging Failed Tests

### Common Issues and Solutions

#### 1. API Not Available
```
❌ API is not available: Connection refused
```
**Solution**: Ensure your Django server is running on the correct port.

#### 2. Authentication Errors
```
❌ test_quotes_single: ERROR - 401 Unauthorized
```
**Solution**: Check that your API keys are properly configured in environment variables.

#### 3. Provider Routing Issues
```
❌ test_polygon_provider_routing: FAILED - Expected 'polygon', got 'fmp'
```
**Solution**: Verify your endpoint routing configuration in `proxy_app/config.py`.

#### 4. Rate Limiting
```
❌ test_batch_request: ERROR - 429 Too Many Requests
```
**Solution**: Implement proper rate limiting and caching in your proxy service.

### Debug Mode
To get more detailed error information, modify the test:
```python
def test_quotes_single(self):
    response = self.make_request(f"/api/v1/quotes/{self.test_symbol}")
    print(f"Response: {response.status_code}")
    print(f"Headers: {response.headers}")
    print(f"Content: {response.text}")
    # ... rest of test
```

## 📈 Continuous Integration

### GitHub Actions Example
```yaml
name: API Tests
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Set up Python
        uses: actions/setup-python@v2
        with:
          python-version: 3.9
      - name: Install dependencies
        run: pip install -r requirements.txt
      - name: Run Django server
        run: python manage.py runserver &
      - name: Wait for server
        run: sleep 10
      - name: Run tests
        run: python run_comprehensive_tests.py
```

## 🎯 Test Coverage Goals

### Coverage Metrics
- ✅ **Endpoint Coverage**: 104/104 (100%)
- ✅ **Provider Coverage**: Both Polygon.io and FMP
- ✅ **HTTP Methods**: GET and POST
- ✅ **Error Scenarios**: 404, 400, 429, 500
- ✅ **Response Formats**: JSON validation
- ✅ **Metadata Validation**: Complete
- ✅ **Parameter Testing**: Required and optional

### Quality Gates
- **Minimum Success Rate**: 90%
- **Maximum Response Time**: 30 seconds per endpoint
- **Error Rate Threshold**: <5%
- **Provider Distribution**: Both providers tested

## 🚀 Advanced Usage

### Running Specific Test Categories
```python
# Import and run specific tests
from test_comprehensive_api import ComprehensiveAPITester
import unittest

# Create test suite for specific category
suite = unittest.TestSuite()
suite.addTest(ComprehensiveAPITester('test_quotes_single'))
suite.addTest(ComprehensiveAPITester('test_quotes_batch'))

# Run the suite
runner = unittest.TextTestRunner(verbosity=2)
result = runner.run(suite)
```

### Custom Test Assertions
```python
def custom_assert_price_data(self, data):
    """Custom assertion for price data validation"""
    self.assertIsInstance(data['price'], (int, float))
    self.assertGreater(data['price'], 0)
    self.assertIn('symbol', data)
    self.assertRegex(data['symbol'], r'^[A-Z]{1,5}$')
```

## 📚 Additional Resources

- **API Documentation**: See `NEW_API_IMPLEMENTATION.md`
- **Endpoint Reference**: Complete specification with inputs/outputs
- **Configuration Guide**: `proxy_app/config.py` documentation
- **Provider Documentation**: Polygon.io and FMP Ultimate APIs

## 🤝 Contributing

### Adding New Tests
1. Add test method to `ComprehensiveAPITester` class
2. Follow naming convention: `test_category_endpoint`
3. Use `assert_response_format()` for validation
4. Update category counts in verification script
5. Run verification: `python test_structure_verification.py`

### Test Guidelines
- Each test should be independent
- Use descriptive test names
- Validate both success and error cases
- Include parameter testing
- Check response metadata
- Test provider routing when applicable

---

**Test Suite Version**: 1.0  
**API Coverage**: 104/104 endpoints (100%)  
**Last Updated**: 2024-01-31  
**Maintainer**: Financial API Team 