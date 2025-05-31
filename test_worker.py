#!/usr/bin/env python3
"""
Test script for the Cloudflare Worker Cache Proxy

This script tests the functionality of the Cloudflare worker that acts as a 
caching proxy for the Django Polygon.io API service.
"""

import requests
import time
import json
from typing import Dict, Any

WORKER_URL = "http://localhost:8787"
DJANGO_URL = "http://localhost:8000"

def test_health_endpoint():
    """Test the worker health endpoint"""
    print("🔍 Testing health endpoint...")
    response = requests.get(f"{WORKER_URL}/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}
    print("✅ Health endpoint working")

def test_proxy_functionality():
    """Test that the worker correctly proxies requests to Django"""
    print("\n🔍 Testing proxy functionality...")
    
    # Test through worker
    worker_response = requests.get(f"{WORKER_URL}/v1/reference/tickers/types")
    
    # Test direct Django
    django_response = requests.get(f"{DJANGO_URL}/v1/reference/tickers/types")
    
    assert worker_response.status_code == 200
    assert django_response.status_code == 200
    
    # Both should return the same data (minus cache headers)
    worker_data = worker_response.json()
    django_data = django_response.json()
    
    assert worker_data == django_data
    print("✅ Proxy functionality working - data matches Django backend")

def test_caching_functionality():
    """Test that caching works correctly"""
    print("\n🔍 Testing caching functionality...")
    
    # Clear any existing cache by using a unique parameter
    test_url = f"{WORKER_URL}/v1/reference/tickers/types?test={int(time.time())}"
    
    # First request should be a cache MISS
    response1 = requests.get(test_url)
    cache_status1 = response1.headers.get('cache-status', 'UNKNOWN')
    
    # Second request should be a cache HIT
    time.sleep(1)  # Small delay
    response2 = requests.get(test_url)
    cache_status2 = response2.headers.get('cache-status', 'UNKNOWN')
    cache_age2 = response2.headers.get('cache-age', '0')
    
    print(f"   First request cache status: {cache_status1}")
    print(f"   Second request cache status: {cache_status2}")
    print(f"   Cache age on second request: {cache_age2}s")
    
    assert response1.status_code == 200
    assert response2.status_code == 200
    assert cache_status2 == 'HIT'
    assert int(cache_age2) > 0
    print("✅ Caching functionality working")

def test_nocache_parameter():
    """Test that nocache parameter bypasses cache"""
    print("\n🔍 Testing nocache parameter...")
    
    response = requests.get(f"{WORKER_URL}/v1/reference/tickers/types?nocache=1")
    cache_status = response.headers.get('cache-status')
    
    assert response.status_code == 200
    assert cache_status is None  # No cache headers when bypassing cache
    print("✅ Nocache parameter working - cache bypassed")

def test_cors_functionality():
    """Test CORS headers"""
    print("\n🔍 Testing CORS functionality...")
    
    # Test OPTIONS request
    response = requests.options(
        f"{WORKER_URL}/v1/reference/tickers/types",
        headers={"Origin": "https://example.com"}
    )
    
    assert response.status_code == 200
    assert response.headers.get('access-control-allow-origin') == '*'
    assert response.headers.get('access-control-allow-methods') == '*'
    assert response.headers.get('access-control-allow-headers') == '*'
    
    # Test GET request CORS headers
    response = requests.get(f"{WORKER_URL}/v1/reference/tickers/types")
    assert response.headers.get('access-control-allow-origin') == '*'
    
    print("✅ CORS functionality working")

def test_cache_ttl_logic():
    """Test different cache TTL for different endpoints"""
    print("\n🔍 Testing cache TTL logic...")
    
    endpoints_and_expected_ttl = [
        ("/v1/reference/tickers/types", 604800),  # WEEK
        ("/v1/reference/tickers", 14400),         # HOUR_4
    ]
    
    for endpoint, expected_ttl in endpoints_and_expected_ttl:
        response = requests.get(f"{WORKER_URL}{endpoint}")
        cache_control = response.headers.get('cache-control', '')
        
        if 'max-age=' in cache_control:
            actual_ttl = int(cache_control.split('max-age=')[1].split(',')[0])
            print(f"   {endpoint}: TTL = {actual_ttl}s (expected: {expected_ttl}s)")
            assert actual_ttl == expected_ttl
        
    print("✅ Cache TTL logic working")

def test_error_handling():
    """Test error handling for invalid endpoints"""
    print("\n🔍 Testing error handling...")
    
    # Test invalid endpoint
    response = requests.get(f"{WORKER_URL}/v1/invalid/endpoint")
    
    # Should still proxy to Django and get Django's error response
    assert response.status_code in [404, 400, 500]  # Django will handle the error
    print("✅ Error handling working - invalid requests properly proxied")

def run_all_tests():
    """Run all tests"""
    print("🚀 Starting Cloudflare Worker Tests")
    print("=" * 50)
    
    try:
        test_health_endpoint()
        test_proxy_functionality()
        test_caching_functionality()
        test_nocache_parameter()
        test_cors_functionality()
        test_cache_ttl_logic()
        test_error_handling()
        
        print("\n" + "=" * 50)
        print("🎉 All tests passed! The Cloudflare worker is working correctly.")
        print("\n📊 Summary:")
        print("   ✅ Health endpoint responding")
        print("   ✅ Proxy functionality working")
        print("   ✅ Caching system operational")
        print("   ✅ Cache bypass (nocache) working")
        print("   ✅ CORS headers properly set")
        print("   ✅ Cache TTL logic implemented")
        print("   ✅ Error handling functional")
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        raise

if __name__ == "__main__":
    run_all_tests() 