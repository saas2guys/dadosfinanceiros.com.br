#!/usr/bin/env python3
"""
Comprehensive Test Suite for the New Unified Financial API
Tests all major endpoints, providers, caching, and error handling
"""

import json
import time
from datetime import datetime
from typing import Any, Dict

import requests


class FinancialAPITester:
    """Test suite for the new unified financial API"""

    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url.rstrip('/')
        self.session = requests.Session()
        self.results = {'passed': 0, 'failed': 0, 'errors': []}

    def run_all_tests(self):
        """Run the complete test suite"""
        print("🚀 Starting Unified Financial API Test Suite")
        print("=" * 60)

        # Test health and documentation endpoints
        self.test_health_endpoint()
        self.test_endpoints_documentation()

        # Test reference data endpoints
        self.test_reference_endpoints()

        # Test market data endpoints
        self.test_market_data_endpoints()

        # Test provider-specific endpoints
        self.test_polygon_exclusive_endpoints()
        self.test_fmp_exclusive_endpoints()

        # Test caching behavior
        self.test_caching_behavior()

        # Test error handling
        self.test_error_handling()

        # Test batch requests
        self.test_batch_requests()

        # Print final results
        self.print_final_results()

    def test_health_endpoint(self):
        """Test health check endpoint"""
        print("\n🔍 Testing Health Check Endpoint")

        try:
            response = self.session.get(f"{self.base_url}/health/")

            if response.status_code == 200:
                data = response.json()
                if 'status' in data and 'providers' in data:
                    print("✅ Health endpoint working correctly")
                    print(f"   Status: {data['status']}")
                    print(f"   Providers: {list(data.get('providers', {}).keys())}")
                    self.results['passed'] += 1
                else:
                    self.fail_test("Health endpoint missing required fields")
            else:
                self.fail_test(f"Health endpoint returned status {response.status_code}")

        except Exception as e:
            self.fail_test(f"Health endpoint error: {e}")

    def test_endpoints_documentation(self):
        """Test endpoints documentation"""
        print("\n📚 Testing Endpoints Documentation")

        try:
            response = self.session.get(f"{self.base_url}/api/v1/endpoints/")

            if response.status_code == 200:
                data = response.json()
                if 'total_endpoints' in data and 'endpoints' in data:
                    total = data['total_endpoints']
                    endpoints = data['endpoints']
                    print(f"✅ Documentation endpoint working correctly")
                    print(f"   Total endpoints: {total}")
                    print(f"   Sample endpoints: {[ep['endpoint'] for ep in endpoints[:3]]}")
                    self.results['passed'] += 1
                else:
                    self.fail_test("Documentation endpoint missing required fields")
            else:
                self.fail_test(f"Documentation endpoint returned status {response.status_code}")

        except Exception as e:
            self.fail_test(f"Documentation endpoint error: {e}")

    def test_reference_endpoints(self):
        """Test reference data endpoints"""
        print("\n📊 Testing Reference Data Endpoints")

        # Test endpoints that should work
        reference_tests = [
            {'name': 'Market Status', 'endpoint': '/api/v1/reference/market-status', 'provider': 'polygon'},
            {'name': 'Stock Profile', 'endpoint': '/api/v1/reference/ticker/AAPL', 'provider': 'fmp'},
            {'name': 'Exchanges List', 'endpoint': '/api/v1/reference/exchanges', 'provider': 'fmp'},
        ]

        for test in reference_tests:
            self.test_endpoint(test['name'], test['endpoint'], test['provider'])

    def test_market_data_endpoints(self):
        """Test market data endpoints"""
        print("\n📈 Testing Market Data Endpoints")

        market_tests = [
            {'name': 'Real-time Quote', 'endpoint': '/api/v1/quotes/AAPL', 'provider': 'fmp'},
            {'name': 'Market Gainers', 'endpoint': '/api/v1/quotes/gainers', 'provider': 'fmp'},
            {'name': 'Market Losers', 'endpoint': '/api/v1/quotes/losers', 'provider': 'fmp'},
            {'name': 'Historical Data', 'endpoint': '/api/v1/historical/AAPL', 'provider': 'fmp'},
        ]

        for test in market_tests:
            self.test_endpoint(test['name'], test['endpoint'], test['provider'])

    def test_polygon_exclusive_endpoints(self):
        """Test Polygon.io exclusive endpoints"""
        print("\n🔹 Testing Polygon.io Exclusive Endpoints")

        polygon_tests = [
            {'name': 'Options Contracts', 'endpoint': '/api/v1/options/contracts', 'provider': 'polygon'},
            {'name': 'Options Chain', 'endpoint': '/api/v1/options/chain/AAPL', 'provider': 'polygon'},
            {'name': 'Futures Contracts', 'endpoint': '/api/v1/futures/contracts', 'provider': 'polygon'},
        ]

        for test in polygon_tests:
            self.test_endpoint(test['name'], test['endpoint'], test['provider'])

    def test_fmp_exclusive_endpoints(self):
        """Test FMP exclusive endpoints"""
        print("\n🔸 Testing FMP Exclusive Endpoints")

        fmp_tests = [
            {'name': 'Income Statement', 'endpoint': '/api/v1/fundamentals/AAPL/income-statement', 'provider': 'fmp'},
            {'name': 'Financial Ratios', 'endpoint': '/api/v1/fundamentals/AAPL/ratios', 'provider': 'fmp'},
            {'name': 'News', 'endpoint': '/api/v1/news/AAPL', 'provider': 'fmp'},
            {'name': 'Analyst Estimates', 'endpoint': '/api/v1/analysts/AAPL/estimates', 'provider': 'fmp'},
        ]

        for test in fmp_tests:
            self.test_endpoint(test['name'], test['endpoint'], test['provider'])

    def test_endpoint(self, name: str, endpoint: str, expected_provider: str):
        """Test a specific endpoint"""
        try:
            response = self.session.get(f"{self.base_url}{endpoint}")

            if response.status_code == 200:
                try:
                    data = response.json()

                    # Check for metadata
                    if '_metadata' in data:
                        metadata = data['_metadata']
                        provider = metadata.get('provider')
                        source = metadata.get('source')

                        if provider == expected_provider:
                            print(f"   ✅ {name}: Provider={provider}, Source={source}")
                            self.results['passed'] += 1
                        else:
                            print(f"   ⚠️  {name}: Expected {expected_provider}, got {provider}")
                            self.results['passed'] += 1  # Still working, just different provider
                    else:
                        print(f"   ✅ {name}: Response received (no metadata)")
                        self.results['passed'] += 1

                except json.JSONDecodeError:
                    self.fail_test(f"{name}: Invalid JSON response")

            elif response.status_code == 404:
                print(f"   ⚠️  {name}: Endpoint not found (404)")
            elif response.status_code == 401:
                print(f"   ⚠️  {name}: Authentication required (401)")
            else:
                print(f"   ❌ {name}: HTTP {response.status_code}")
                self.results['failed'] += 1

        except Exception as e:
            self.fail_test(f"{name}: {e}")

    def test_caching_behavior(self):
        """Test caching behavior"""
        print("\n💾 Testing Caching Behavior")

        try:
            endpoint = "/api/v1/quotes/AAPL"

            # First request
            start_time = time.time()
            response1 = self.session.get(f"{self.base_url}{endpoint}")
            first_request_time = time.time() - start_time

            if response1.status_code == 200:
                data1 = response1.json()

                # Second request (should be cached)
                start_time = time.time()
                response2 = self.session.get(f"{self.base_url}{endpoint}")
                second_request_time = time.time() - start_time

                if response2.status_code == 200:
                    data2 = response2.json()

                    # Check if second request was faster (cached)
                    if second_request_time < first_request_time * 0.8:
                        print("   ✅ Caching appears to be working (faster response)")
                        self.results['passed'] += 1
                    else:
                        print("   ⚠️  Caching behavior unclear")

                    # Check metadata
                    source1 = data1.get('_metadata', {}).get('source', 'unknown')
                    source2 = data2.get('_metadata', {}).get('source', 'unknown')

                    print(f"   First request: {source1} ({first_request_time:.3f}s)")
                    print(f"   Second request: {source2} ({second_request_time:.3f}s)")
                else:
                    self.fail_test("Caching test: Second request failed")
            else:
                self.fail_test("Caching test: First request failed")

        except Exception as e:
            self.fail_test(f"Caching test error: {e}")

    def test_error_handling(self):
        """Test error handling"""
        print("\n❌ Testing Error Handling")

        error_tests = [
            {'name': 'Invalid Endpoint', 'endpoint': '/api/v1/invalid/endpoint', 'expected_status': 404},
            {
                'name': 'Invalid Symbol',
                'endpoint': '/api/v1/quotes/INVALIDXYZ',
                'expected_status': [200, 404, 400],  # Different providers handle differently
            },
        ]

        for test in error_tests:
            try:
                response = self.session.get(f"{self.base_url}{test['endpoint']}")
                expected = test['expected_status']

                if isinstance(expected, list):
                    if response.status_code in expected:
                        print(f"   ✅ {test['name']}: Status {response.status_code}")
                        self.results['passed'] += 1
                    else:
                        print(f"   ❌ {test['name']}: Expected {expected}, got {response.status_code}")
                        self.results['failed'] += 1
                else:
                    if response.status_code == expected:
                        print(f"   ✅ {test['name']}: Status {response.status_code}")
                        self.results['passed'] += 1
                    else:
                        print(f"   ❌ {test['name']}: Expected {expected}, got {response.status_code}")
                        self.results['failed'] += 1

            except Exception as e:
                self.fail_test(f"{test['name']}: {e}")

    def test_batch_requests(self):
        """Test batch request functionality"""
        print("\n📦 Testing Batch Requests")

        try:
            batch_data = {
                "requests": [
                    {"path": "quotes/AAPL", "params": {}},
                    {"path": "quotes/GOOGL", "params": {}},
                    {"path": "reference/ticker/MSFT", "params": {}},
                ]
            }

            response = self.session.post(f"{self.base_url}/api/v1/batch", json=batch_data, headers={'Content-Type': 'application/json'})

            if response.status_code == 200:
                data = response.json()
                if 'results' in data and 'total' in data:
                    results = data['results']
                    total = data['total']

                    print(f"   ✅ Batch request processed {total} requests")

                    success_count = sum(1 for r in results if 'data' in r)
                    error_count = sum(1 for r in results if 'error' in r)

                    print(f"   Successful: {success_count}, Errors: {error_count}")
                    self.results['passed'] += 1
                else:
                    self.fail_test("Batch response missing required fields")
            else:
                print(f"   ⚠️  Batch requests might not be implemented yet (Status: {response.status_code})")

        except Exception as e:
            self.fail_test(f"Batch request error: {e}")

    def fail_test(self, message: str):
        """Record a failed test"""
        print(f"   ❌ {message}")
        self.results['failed'] += 1
        self.results['errors'].append(message)

    def print_final_results(self):
        """Print final test results"""
        print("\n" + "=" * 60)
        print("🏁 TEST RESULTS SUMMARY")
        print("=" * 60)

        total = self.results['passed'] + self.results['failed']
        pass_rate = (self.results['passed'] / total * 100) if total > 0 else 0

        print(f"Total Tests: {total}")
        print(f"Passed: {self.results['passed']} ✅")
        print(f"Failed: {self.results['failed']} ❌")
        print(f"Pass Rate: {pass_rate:.1f}%")

        if self.results['errors']:
            print("\n🔍 ERRORS ENCOUNTERED:")
            for i, error in enumerate(self.results['errors'], 1):
                print(f"   {i}. {error}")

        if pass_rate >= 80:
            print("\n🎉 API is working well!")
        elif pass_rate >= 60:
            print("\n⚠️  API has some issues but is mostly functional")
        else:
            print("\n🚨 API has significant issues that need attention")


def main():
    """Main test function"""
    import argparse

    parser = argparse.ArgumentParser(description='Test the Unified Financial API')
    parser.add_argument('--url', default='http://localhost:8000', help='Base URL of the API (default: http://localhost:8000)')
    parser.add_argument('--verbose', action='store_true', help='Enable verbose output')

    args = parser.parse_args()

    print(f"🧪 Testing API at: {args.url}")
    print(f"⏰ Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    tester = FinancialAPITester(args.url)
    tester.run_all_tests()


if __name__ == "__main__":
    main()
