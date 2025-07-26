#!/usr/bin/env python3
"""
Unified Financial API Test Script
Tests the new comprehensive financial data proxy service.
"""

import json
import time
from datetime import datetime, timedelta

import requests

# Test configuration
BASE_URL = "http://localhost:8000"
TIMEOUT = 10


def test_endpoint(endpoint, description, expected_provider=None):
    """Test a single API endpoint"""
    url = f"{BASE_URL}{endpoint}"
    print(f"\n🧪 Testing: {description}")
    print(f"📍 URL: {url}")

    try:
        start_time = time.time()
        response = requests.get(url, timeout=TIMEOUT)
        response_time = time.time() - start_time

        print(f"⏱️  Response time: {response_time:.2f}s")
        print(f"📊 Status code: {response.status_code}")

        if response.status_code == 200:
            try:
                data = response.json()

                # Check if it's unified API response format
                if isinstance(data, dict) and 'metadata' in data:
                    provider = data.get('metadata', {}).get('provider')
                    print(f"🎯 Provider used: {provider}")

                    if expected_provider and provider != expected_provider:
                        print(f"⚠️  Expected {expected_provider}, got {provider}")

                    # Show sample data
                    if 'data' in data:
                        sample_data = str(data['data'])[:200] + "..." if len(str(data['data'])) > 200 else str(data['data'])
                        print(f"📄 Sample data: {sample_data}")
                else:
                    # Legacy format
                    sample_data = str(data)[:200] + "..." if len(str(data)) > 200 else str(data)
                    print(f"📄 Data: {sample_data}")

                print("✅ SUCCESS")
                return True

            except json.JSONDecodeError:
                print(f"❌ Invalid JSON response")
                print(f"📄 Raw response: {response.text[:200]}...")
                return False
        else:
            print(f"❌ HTTP Error: {response.status_code}")
            try:
                error_data = response.json()
                print(f"📄 Error: {error_data}")
            except:
                print(f"📄 Raw error: {response.text}")
            return False

    except requests.exceptions.RequestException as e:
        print(f"❌ Request failed: {e}")
        return False


def main():
    """Run comprehensive API tests"""
    print("🚀 Starting Unified Financial API Tests")
    print("=" * 60)

    # Test results tracking
    tests = []

    # 1. Test new unified endpoints
    print("\n📈 TESTING NEW UNIFIED API ENDPOINTS")
    print("-" * 40)

    unified_tests = [
        # Market Data
        ("/api/v1/quotes/AAPL", "Real-time quote for AAPL", "fmp"),
        ("/api/v1/quotes/gainers", "Top gaining stocks", "fmp"),
        ("/api/v1/quotes/losers", "Top losing stocks", "fmp"),
        ("/api/v1/quotes/active", "Most active stocks", "fmp"),
        # Historical Data
        ("/api/v1/historical/AAPL", "Historical price data for AAPL", "fmp"),
        ("/api/v1/historical/AAPL/intraday", "Intraday data for AAPL", "fmp"),
        # Fundamental Data (FMP exclusive)
        ("/api/v1/fundamentals/AAPL/income-statement", "Income statement for AAPL", "fmp"),
        ("/api/v1/fundamentals/AAPL/balance-sheet", "Balance sheet for AAPL", "fmp"),
        ("/api/v1/fundamentals/AAPL/ratios", "Financial ratios for AAPL", "fmp"),
        # Reference Data
        ("/api/v1/reference/ticker/AAPL", "Company profile for AAPL", "fmp"),
        ("/api/v1/reference/market-status", "Market status", "fmp"),
        # Options Data (Polygon exclusive)
        ("/api/v1/options/contracts", "Options contracts", "polygon"),
        ("/api/v1/options/chain/AAPL", "Options chain for AAPL", "polygon"),
        # Technical Analysis
        ("/api/v1/technical/AAPL/sma", "SMA indicator for AAPL", "fmp"),
        ("/api/v1/technical/AAPL/rsi", "RSI indicator for AAPL", "fmp"),
        # News & Sentiment (FMP exclusive)
        ("/api/v1/news", "Latest financial news", "fmp"),
        ("/api/v1/news/AAPL", "News for AAPL", "fmp"),
        # Analyst Data (FMP exclusive)
        ("/api/v1/analysts/AAPL/estimates", "Analyst estimates for AAPL", "fmp"),
        ("/api/v1/analysts/AAPL/recommendations", "Analyst recommendations for AAPL", "fmp"),
        # Economic Data (FMP exclusive)
        ("/api/v1/economy/gdp", "GDP data", "fmp"),
        ("/api/v1/economy/treasury-rates", "Treasury rates", "fmp"),
        # Forex & Crypto
        ("/api/v1/forex/rates", "Forex rates", "fmp"),
        ("/api/v1/crypto/prices", "Cryptocurrency prices", "fmp"),
        # ETF Data (FMP exclusive)
        ("/api/v1/etf/list", "ETF list", "fmp"),
        # Commodities (FMP exclusive)
        ("/api/v1/commodities/metals", "Precious metals prices", "fmp"),
    ]

    for endpoint, description, expected_provider in unified_tests:
        success = test_endpoint(endpoint, description, expected_provider)
        tests.append((endpoint, success))

    # 2. Test legacy endpoints (backward compatibility)
    print("\n🔄 TESTING LEGACY ENDPOINTS (Backward Compatibility)")
    print("-" * 50)

    legacy_tests = [
        ("/v1/snapshot", "Legacy snapshot endpoint", "polygon"),
        ("/v1/reference/tickers/AAPL", "Legacy ticker reference", "polygon"),
        ("/v1/aggs/ticker/AAPL/range/1/day/2023-01-01/2023-12-31", "Legacy aggregates", "polygon"),
    ]

    for endpoint, description, expected_provider in legacy_tests:
        success = test_endpoint(endpoint, description, expected_provider)
        tests.append((endpoint, success))

    # 3. Test error handling
    print("\n❌ TESTING ERROR HANDLING")
    print("-" * 30)

    error_tests = [
        ("/api/v1/nonexistent/endpoint", "Non-existent endpoint", None),
        ("/api/v1/quotes/INVALIDTICKER12345", "Invalid ticker", "fmp"),
    ]

    for endpoint, description, expected_provider in error_tests:
        # For error tests, we expect failure
        print(f"\n🧪 Testing: {description}")
        url = f"{BASE_URL}{endpoint}"
        print(f"📍 URL: {url}")

        try:
            response = requests.get(url, timeout=TIMEOUT)
            print(f"📊 Status code: {response.status_code}")

            if response.status_code >= 400:
                print("✅ ERROR HANDLED CORRECTLY")
                tests.append((endpoint, True))
            else:
                print("⚠️  Expected error but got success")
                tests.append((endpoint, False))

        except Exception as e:
            print(f"❌ Request failed: {e}")
            tests.append((endpoint, False))

    # Print summary
    print("\n" + "=" * 60)
    print("📊 TEST SUMMARY")
    print("=" * 60)

    successful = sum(1 for _, success in tests if success)
    total = len(tests)
    success_rate = (successful / total) * 100 if total > 0 else 0

    print(f"✅ Successful tests: {successful}/{total} ({success_rate:.1f}%)")

    if successful == total:
        print("🎉 ALL TESTS PASSED!")
    else:
        print("\n❌ Failed tests:")
        for endpoint, success in tests:
            if not success:
                print(f"   - {endpoint}")

    print("\n📝 Notes:")
    print("   - If tests fail due to missing API keys, that's expected")
    print("   - The important thing is that endpoints are routed correctly")
    print("   - Check that providers are correctly identified in responses")
    print("   - Legacy endpoints should still work for backward compatibility")

    return success_rate == 100.0


if __name__ == "__main__":
    main()
