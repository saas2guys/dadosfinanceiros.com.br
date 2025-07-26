#!/usr/bin/env python3
"""
Comprehensive API Test Runner
Organizes and runs all API tests with detailed reporting and metrics
"""

import json
import sys
import time
import unittest
from datetime import datetime

import requests
from test_comprehensive_api import ComprehensiveAPITester


class APITestRunner:
    """Test runner with enhanced reporting and organization"""

    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.test_categories = {
            'Reference Data': [
                'test_reference_tickers',
                'test_reference_ticker_profile',
                'test_reference_ticker_executives',
                'test_reference_ticker_outlook',
                'test_reference_exchanges',
                'test_reference_market_cap',
                'test_reference_market_status',
                'test_reference_market_holidays',
            ],
            'Market Data': [
                'test_quotes_single',
                'test_quotes_batch',
                'test_quotes_gainers',
                'test_quotes_losers',
                'test_quotes_most_active',
                'test_quotes_last_trade',
                'test_quotes_last_quote',
                'test_quotes_previous_close',
                'test_historical_data',
                'test_historical_intraday',
                'test_historical_dividends',
                'test_historical_splits',
                'test_historical_grouped',
            ],
            'Options Data': [
                'test_options_contracts',
                'test_options_chain',
                'test_options_greeks',
                'test_options_open_interest',
                'test_options_historical',
            ],
            'Futures Data': ['test_futures_contracts', 'test_futures_snapshot', 'test_futures_historical'],
            'Tick-level Data': ['test_ticks_trades', 'test_ticks_quotes', 'test_ticks_aggs'],
            'Fundamental Data': [
                'test_fundamentals_income_statement',
                'test_fundamentals_balance_sheet',
                'test_fundamentals_cash_flow',
                'test_fundamentals_ratios',
                'test_fundamentals_metrics',
                'test_fundamentals_dcf',
                'test_fundamentals_enterprise_value',
                'test_fundamentals_growth',
            ],
            'News & Sentiment': [
                'test_news_stock',
                'test_news_general',
                'test_news_press_releases',
                'test_news_market',
                'test_news_sentiment',
            ],
            'Analyst Data': [
                'test_analysts_estimates',
                'test_analysts_recommendations',
                'test_analysts_price_targets',
                'test_analysts_upgrades_downgrades',
            ],
            'Earnings Data': ['test_earnings_calendar', 'test_earnings_transcripts', 'test_earnings_history', 'test_earnings_surprises'],
            'Corporate Events': ['test_events_ipo_calendar', 'test_events_stock_split_calendar', 'test_events_dividend_calendar'],
            'Institutional & Insider Data': ['test_institutional_13f', 'test_institutional_holders', 'test_institutional_insider_trading'],
            'Economic Data': [
                'test_economy_gdp',
                'test_economy_inflation',
                'test_economy_unemployment',
                'test_economy_treasury_rates',
                'test_economy_federal_funds_rate',
            ],
            'ETF & Mutual Funds': ['test_etf_list', 'test_etf_holdings', 'test_etf_performance', 'test_mutual_funds_list'],
            'Commodities': ['test_commodities_list', 'test_commodities_metals', 'test_commodities_energy', 'test_commodities_historical'],
            'Cryptocurrencies': ['test_crypto_list', 'test_crypto_quote', 'test_crypto_historical'],
            'International Markets': [
                'test_international_exchanges',
                'test_forex_rates',
                'test_forex_historical',
                'test_international_stocks',
            ],
            'SEC Filings': ['test_sec_filings', 'test_sec_10k', 'test_sec_10q', 'test_sec_8k', 'test_sec_rss_feed'],
            'Technical Indicators': [
                'test_technical_sma',
                'test_technical_ema',
                'test_technical_rsi',
                'test_technical_macd',
                'test_technical_bollinger_bands',
                'test_technical_stochastic',
                'test_technical_adx',
                'test_technical_williams_r',
            ],
            'Bulk Data': ['test_bulk_eod_prices', 'test_bulk_fundamentals', 'test_bulk_insider_trading'],
            'System Endpoints': ['test_health_check', 'test_endpoints_list', 'test_batch_request'],
            'Error Handling': ['test_invalid_symbol_404', 'test_invalid_endpoint_404', 'test_missing_required_params_400'],
            'Caching & Routing': ['test_cache_behavior', 'test_polygon_provider_routing', 'test_fmp_provider_routing'],
        }

        self.results = {}
        self.overall_stats = {
            'total_tests': 0,
            'passed': 0,
            'failed': 0,
            'errors': 0,
            'skipped': 0,
            'start_time': None,
            'end_time': None,
            'duration': 0,
        }

    def check_api_availability(self):
        """Check if API is available before running tests"""
        print("🔍 Checking API availability...")
        try:
            response = requests.get(f"{self.base_url}/health/", timeout=10)
            if response.status_code == 200:
                data = response.json()
                print(f"✅ API is available - Status: {data.get('status', 'unknown')}")
                return True
            else:
                print(f"❌ API returned status code: {response.status_code}")
                return False
        except requests.exceptions.RequestException as e:
            print(f"❌ API is not available: {e}")
            return False

    def run_category_tests(self, category: str, test_methods: list):
        """Run tests for a specific category"""
        print(f"\n{'='*60}")
        print(f"🧪 Testing Category: {category}")
        print(f"{'='*60}")

        category_results = {'total': len(test_methods), 'passed': 0, 'failed': 0, 'errors': 0, 'skipped': 0, 'tests': {}, 'duration': 0}

        category_start = time.time()

        # Create test suite for this category
        suite = unittest.TestSuite()
        for test_method in test_methods:
            suite.addTest(ComprehensiveAPITester(test_method))

        # Custom test result to capture detailed info
        result = unittest.TestResult()

        # Run the tests
        suite.run(result)

        category_duration = time.time() - category_start
        category_results['duration'] = category_duration

        # Process results
        for test, error in result.failures:
            test_name = test._testMethodName
            category_results['failed'] += 1
            category_results['tests'][test_name] = {'status': 'FAILED', 'error': str(error) if error else None}
            print(f"❌ {test_name}: FAILED")

        for test, error in result.errors:
            test_name = test._testMethodName
            category_results['errors'] += 1
            category_results['tests'][test_name] = {'status': 'ERROR', 'error': str(error) if error else None}
            print(f"🔥 {test_name}: ERROR")

        # Count passed tests
        total_run = result.testsRun
        total_problems = len(result.failures) + len(result.errors)
        category_results['passed'] = total_run - total_problems

        # Mark successful tests
        for test_method in test_methods:
            if test_method not in category_results['tests']:
                category_results['tests'][test_method] = {'status': 'PASSED', 'error': None}
                print(f"✅ {test_method}: PASSED")

        # Update overall stats
        self.overall_stats['total_tests'] += category_results['total']
        self.overall_stats['passed'] += category_results['passed']
        self.overall_stats['failed'] += category_results['failed']
        self.overall_stats['errors'] += category_results['errors']

        # Print category summary
        print(f"\n📊 {category} Summary:")
        print(f"   Total: {category_results['total']}")
        print(f"   Passed: {category_results['passed']}")
        print(f"   Failed: {category_results['failed']}")
        print(f"   Errors: {category_results['errors']}")
        print(f"   Duration: {category_duration:.2f}s")

        self.results[category] = category_results
        return category_results

    def run_all_tests(self):
        """Run all test categories"""
        print("🚀 Starting Comprehensive Financial API Test Suite")
        print(f"🎯 Target API: {self.base_url}")
        print(f"📅 Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

        # Check API availability first
        if not self.check_api_availability():
            print("❌ Cannot proceed with tests - API is not available")
            return False

        self.overall_stats['start_time'] = time.time()

        # Run tests by category
        for category, test_methods in self.test_categories.items():
            try:
                self.run_category_tests(category, test_methods)
            except KeyboardInterrupt:
                print("\n⚠️ Tests interrupted by user")
                break
            except Exception as e:
                print(f"❌ Error running category {category}: {e}")
                continue

        self.overall_stats['end_time'] = time.time()
        self.overall_stats['duration'] = self.overall_stats['end_time'] - self.overall_stats['start_time']

        self.print_final_report()
        return True

    def print_final_report(self):
        """Print comprehensive final report"""
        print(f"\n{'='*80}")
        print("📋 COMPREHENSIVE TEST REPORT")
        print(f"{'='*80}")

        # Overall statistics
        stats = self.overall_stats
        success_rate = (stats['passed'] / stats['total_tests'] * 100) if stats['total_tests'] > 0 else 0

        print(f"\n📊 Overall Statistics:")
        print(f"   Total Tests Run: {stats['total_tests']}")
        print(f"   ✅ Passed: {stats['passed']}")
        print(f"   ❌ Failed: {stats['failed']}")
        print(f"   🔥 Errors: {stats['errors']}")
        print(f"   📈 Success Rate: {success_rate:.1f}%")
        print(f"   ⏱️ Total Duration: {stats['duration']:.2f}s")

        # Category breakdown
        print(f"\n📂 Category Breakdown:")
        for category, results in self.results.items():
            success_rate = (results['passed'] / results['total'] * 100) if results['total'] > 0 else 0
            status_icon = "✅" if results['failed'] == 0 and results['errors'] == 0 else "❌"
            print(f"   {status_icon} {category}: {results['passed']}/{results['total']} ({success_rate:.1f}%)")

        print(f"\n🏁 Final Assessment:")
        overall_success = (stats['passed'] / stats['total_tests'] * 100) if stats['total_tests'] > 0 else 0
        if overall_success >= 90:
            print("   🎉 EXCELLENT - API is performing very well!")
        elif overall_success >= 75:
            print("   👍 GOOD - API is mostly functional with minor issues")
        elif overall_success >= 50:
            print("   ⚠️ FAIR - API has significant issues that need attention")
        else:
            print("   🚨 POOR - API has major problems and needs immediate attention")

        print(f"\n📅 Completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"{'='*80}")

        # Save results to file
        self.save_results_to_file()

    def save_results_to_file(self):
        """Save test results to JSON file"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"api_test_results_{timestamp}.json"

        report_data = {
            'metadata': {
                'timestamp': datetime.now().isoformat(),
                'api_url': self.base_url,
                'total_categories': len(self.test_categories),
                'total_expected_endpoints': 100,
            },
            'overall_stats': self.overall_stats,
            'category_results': self.results,
            'test_categories': self.test_categories,
        }

        try:
            with open(filename, 'w') as f:
                json.dump(report_data, f, indent=2, default=str)
            print(f"📄 Test results saved to: {filename}")
        except Exception as e:
            print(f"⚠️ Could not save results to file: {e}")

    def list_categories(self):
        """List all available test categories"""
        print("📂 Available Test Categories:")
        for i, (category, tests) in enumerate(self.test_categories.items(), 1):
            print(f"   {i:2d}. {category} ({len(tests)} tests)")


def main():
    """Main entry point"""
    import argparse

    parser = argparse.ArgumentParser(description='Comprehensive API Test Runner')
    parser.add_argument('--url', default='http://localhost:8000', help='Base URL of the API (default: http://localhost:8000)')

    args = parser.parse_args()

    runner = APITestRunner(args.url)
    runner.run_all_tests()


if __name__ == "__main__":
    main()
