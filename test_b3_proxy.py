#!/usr/bin/env python3
"""
Test script for the unified Polygon/B3 proxy with market selection.

This script tests both US (Polygon.io) and Brazilian (B3) market endpoints
to ensure the market selector parameter works correctly.
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
        logger.info("Testing Unified Polygon/B3 Proxy")
        logger.info("=" * 50)

    # Calculate date range for testing
    end_date = datetime.now().strftime("%Y-%m-%d")
    start_date = (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d")

    test_cases = [
        # US Market Tests (Polygon.io)
        {
            "url": f"{BASE_URL}/us/v2/last/trade/AAPL",
            "description": "US Last Trade - AAPL",
        },
        {
            "url": f"{BASE_URL}/us/v2/last/nbbo/MSFT",
            "description": "US Last Quote - MSFT",
        },
        {
            "url": f"{BASE_URL}/us/v2/aggs/ticker/AAPL/range/1/day/{start_date}/{end_date}",
            "description": "US Aggregates - AAPL (30 days)",
        },
        # Brazilian Market Tests (B3)
        {
            "url": f"{BASE_URL}/br/v2/last/trade/PETR4",
            "description": "BR Last Trade - PETR4",
        },
        {
            "url": f"{BASE_URL}/br/v2/last/nbbo/VALE3",
            "description": "BR Last Quote - VALE3",
        },
        {
            "url": f"{BASE_URL}/br/v2/aggs/ticker/PETR4/range/1/day/{start_date}/{end_date}",
            "description": "BR Aggregates - PETR4 (30 days)",
        },
        # Ticker Conversion Tests
        {
            "url": f"{BASE_URL}/br/v2/last/trade/AAPL",
            "description": "BR Ticker Conversion - AAPL→AAPL34",
        },
        {
            "url": f"{BASE_URL}/br/v2/last/trade/TSLA",
            "description": "BR Ticker Conversion - TSLA→TSLA34",
        },
        # Backward Compatibility Tests
        {
            "url": f"{BASE_URL}/v2/last/trade/AAPL",
            "description": "Legacy Format (should redirect to US)",
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
        else:
            logger.warning(f"{total - passed} tests failed")

    # Exit with appropriate code
    sys.exit(0 if passed == total else 1)


if __name__ == "__main__":
    main()
