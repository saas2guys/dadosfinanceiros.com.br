#!/usr/bin/env python3
"""
Test script for the Polygon.io proxy.

This script tests real US market endpoints via Polygon.io API.
Requires POLYGON_API_KEY to be configured for real data.
"""

import json
import logging
import sys
from datetime import datetime, timedelta

import requests

BASE_URL = "http://localhost:8000/v1"

# Configure logging to be quiet by default
logging.basicConfig(level=logging.WARNING)
logger = logging.getLogger(__name__)


def test_endpoint(url, description, verbose=False):
    """Test a single endpoint and return result"""
    if verbose:
        logger.info(f"Testing: {description}")
        logger.info(f"URL: {url}")

    try:
        response = requests.get(url, timeout=10)
        if verbose:
            logger.info(f"Status: {response.status_code}")

        if response.status_code == 200:
            data = response.json()
            if verbose:
                logger.info(f"Response keys: {list(data.keys())}")

                # Show sample data structure
                if "results" in data:
                    results = data["results"]
                    if isinstance(results, list) and len(results) > 0:
                        logger.info(f"Sample result keys: {list(results[0].keys())}")
                    elif isinstance(results, dict):
                        logger.info(f"Result keys: {list(results.keys())}")

            return True
        else:
            if verbose:
                logger.error(f"Error: {response.text}")
            return False

    except requests.exceptions.Timeout:
        if verbose:
            logger.error("Request timed out")
        return False
    except requests.exceptions.RequestException as e:
        if verbose:
            logger.error(f"Request failed: {e}")
        return False
    except Exception as e:
        if verbose:
            logger.error(f"Unexpected error: {e}")
        return False


def main():
    """Run all tests"""
    # Check if verbose mode is requested
    verbose = "--verbose" in sys.argv or "-v" in sys.argv

    if verbose:
        logging.getLogger().setLevel(logging.INFO)
        logger.info("Testing Polygon.io Proxy - Real Endpoints")
        logger.info("=" * 50)

    # Calculate date range for testing
    end_date = datetime.now().strftime("%Y-%m-%d")
    start_date = (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d")

    test_cases = [
        # Real Polygon.io endpoints mapped to clean /v1/ URLs
        {
            "url": f"{BASE_URL}/last/trade/AAPL",
            "description": "Last Trade - AAPL",
        },
        {
            "url": f"{BASE_URL}/last/nbbo/MSFT",
            "description": "Last Quote (NBBO) - MSFT",
        },
        {
            "url": f"{BASE_URL}/aggs/ticker/AAPL/range/1/day/{start_date}/{end_date}",
            "description": "Aggregates - AAPL (7 days)",
        },
        {
            "url": f"{BASE_URL}/aggs/ticker/GOOGL/prev",
            "description": "Previous Day Bar - GOOGL",
        },
        {
            "url": f"{BASE_URL}/reference/tickers?market=stocks&limit=5",
            "description": "Reference Tickers - Stocks",
        },
        {
            "url": f"{BASE_URL}/reference/tickers/TSLA",
            "description": "Ticker Overview - TSLA",
        },
        {
            "url": f"{BASE_URL}/snapshot/locale/us/markets/stocks/tickers/AAPL",
            "description": "Single Ticker Snapshot - AAPL",
        },
        {
            "url": f"{BASE_URL}/conversion/USD/EUR?amount=100",
            "description": "Currency Conversion - USD to EUR",
        },
    ]

    # Run tests
    passed = 0
    total = len(test_cases)

    for test_case in test_cases:
        if test_endpoint(test_case["url"], test_case["description"], verbose=verbose):
            passed += 1

    # Summary
    if verbose:
        logger.info("=" * 50)
        logger.info(f"Test Results: {passed}/{total} passed")

        if passed == total:
            logger.info("All tests passed!")
        elif passed == 0:
            logger.warning("All tests failed - check POLYGON_API_KEY configuration")
        else:
            logger.warning(f"{total - passed} tests failed")

    # Exit with appropriate code
    sys.exit(0 if passed >= total * 0.75 else 1)  # Allow 25% failure rate


if __name__ == "__main__":
    main()
