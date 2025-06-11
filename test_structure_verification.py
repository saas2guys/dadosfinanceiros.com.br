#!/usr/bin/env python3
"""
Test Structure Verification
Verifies that all test methods are properly structured and accessible
"""

import unittest
import inspect
from test_comprehensive_api import ComprehensiveAPITester

def verify_test_structure():
    """Verify that all test methods are properly structured"""
    
    # Get all test methods from the test class
    test_methods = []
    for name, method in inspect.getmembers(ComprehensiveAPITester, predicate=inspect.isfunction):
        if name.startswith('test_'):
            test_methods.append(name)
    
    # Expected test categories and their counts
    expected_categories = {
        'Reference Data': 8,
        'Market Data': 13,
        'Options Data': 5,
        'Futures Data': 3,
        'Tick-level Data': 3,
        'Fundamental Data': 8,
        'News & Sentiment': 5,
        'Analyst Data': 4,
        'Earnings Data': 4,
        'Corporate Events': 3,
        'Institutional & Insider Data': 3,
        'Economic Data': 5,
        'ETF & Mutual Funds': 4,
        'Commodities': 4,
        'Cryptocurrencies': 3,
        'International Markets': 4,
        'SEC Filings': 5,
        'Technical Indicators': 8,
        'Bulk Data': 3,
        'System Endpoints': 3,
        'Error Handling': 3,
        'Caching & Routing': 3
    }
    
    total_expected = sum(expected_categories.values())
    
    print("🔍 Test Structure Verification")
    print("=" * 50)
    print(f"Expected total tests: {total_expected}")
    print(f"Found test methods: {len(test_methods)}")
    print(f"Coverage: {len(test_methods)/total_expected*100:.1f}%")
    
    # Verify each category
    print("\n📂 Category Analysis:")
    
    category_patterns = {
        'Reference Data': 'test_reference_',
        'Market Data': 'test_quotes_|test_historical_',
        'Options Data': 'test_options_',
        'Futures Data': 'test_futures_',
        'Tick-level Data': 'test_ticks_',
        'Fundamental Data': 'test_fundamentals_',
        'News & Sentiment': 'test_news_',
        'Analyst Data': 'test_analysts_',
        'Earnings Data': 'test_earnings_',
        'Corporate Events': 'test_events_',
        'Institutional & Insider Data': 'test_institutional_',
        'Economic Data': 'test_economy_',
        'ETF & Mutual Funds': 'test_etf_|test_mutual_',
        'Commodities': 'test_commodities_',
        'Cryptocurrencies': 'test_crypto_',
        'International Markets': 'test_international_|test_forex_',
        'SEC Filings': 'test_sec_',
        'Technical Indicators': 'test_technical_',
        'Bulk Data': 'test_bulk_',
        'System Endpoints': 'test_health_|test_endpoints_|test_batch_',
        'Error Handling': 'test_invalid_|test_missing_',
        'Caching & Routing': 'test_cache_|test_polygon_|test_fmp_'
    }
    
    import re
    
    for category, pattern in category_patterns.items():
        matching_tests = [m for m in test_methods if re.search(pattern, m)]
        expected_count = expected_categories[category]
        status = "✅" if len(matching_tests) >= expected_count else "❌"
        print(f"   {status} {category}: {len(matching_tests)}/{expected_count}")
        if len(matching_tests) < expected_count:
            print(f"      Missing tests in {category}")
    
    # List all found test methods
    print(f"\n📋 All Test Methods ({len(test_methods)}):")
    for i, method in enumerate(sorted(test_methods), 1):
        print(f"   {i:2d}. {method}")
    
    # Check for any obvious issues
    print(f"\n🔍 Validation Summary:")
    if len(test_methods) >= total_expected * 0.9:
        print("   ✅ Test coverage is excellent")
    elif len(test_methods) >= total_expected * 0.75:
        print("   ⚠️ Test coverage is good but could be improved")
    else:
        print("   ❌ Test coverage needs significant improvement")
    
    # Verify test class structure
    print(f"\n🏗️ Class Structure:")
    print(f"   Base class: {ComprehensiveAPITester.__bases__}")
    print(f"   Methods: {len([m for m in dir(ComprehensiveAPITester) if not m.startswith('_')])}")
    print(f"   Test methods: {len(test_methods)}")
    
    return len(test_methods) >= total_expected * 0.9

if __name__ == "__main__":
    success = verify_test_structure()
    exit(0 if success else 1) 