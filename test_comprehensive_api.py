#!/usr/bin/env python3
"""
Comprehensive Test Suite for the Unified Financial API
Tests all 100+ endpoints with their inputs and expected outputs
"""

import requests
import json
import time
from datetime import datetime, timedelta
from typing import Dict, Any, List
import unittest
from unittest.mock import patch, MagicMock

class ComprehensiveAPITester(unittest.TestCase):
    """Comprehensive test suite for all API endpoints"""
    
    @classmethod
    def setUpClass(cls):
        cls.base_url = "http://localhost:8000"
        cls.session = requests.Session()
        cls.test_symbol = "AAPL"
        cls.test_date = "2024-01-31"
        cls.test_from_date = "2024-01-01"
        cls.test_to_date = "2024-01-31"
        
    def setUp(self):
        """Set up each test"""
        self.maxDiff = None
        
    def make_request(self, endpoint: str, params: dict = None, method: str = "GET", data: dict = None):
        """Make API request with error handling"""
        url = f"{self.base_url}{endpoint}"
        try:
            if method.upper() == "GET":
                response = self.session.get(url, params=params, timeout=30)
            elif method.upper() == "POST":
                response = self.session.post(url, json=data, timeout=30)
            return response
        except requests.exceptions.RequestException as e:
            self.fail(f"Request failed for {endpoint}: {e}")
    
    def assert_response_format(self, response, expected_keys: list = None, check_metadata: bool = True):
        """Assert common response format requirements"""
        self.assertEqual(response.status_code, 200, f"Expected 200, got {response.status_code}")
        
        try:
            data = response.json()
        except json.JSONDecodeError:
            self.fail("Response is not valid JSON")
        
        # Check metadata if enabled
        if check_metadata and isinstance(data, dict) and '_metadata' in data:
            metadata = data['_metadata']
            self.assertIn('source', metadata)
            self.assertIn('provider', metadata)
            self.assertIn('timestamp', metadata)
            self.assertIn(metadata['source'], ['live', 'cache'])
            self.assertIn(metadata['provider'], ['polygon', 'fmp'])
        
        # Check expected keys if provided
        if expected_keys and isinstance(data, (dict, list)):
            if isinstance(data, list) and data:
                for key in expected_keys:
                    self.assertIn(key, data[0], f"Missing key {key} in response")
            elif isinstance(data, dict):
                for key in expected_keys:
                    self.assertIn(key, data, f"Missing key {key} in response")
        
        return data

    # =============================================================================
    # REFERENCE DATA TESTS (10 endpoints)
    # =============================================================================
    
    def test_reference_tickers(self):
        """Test GET /api/v1/reference/tickers"""
        response = self.make_request("/api/v1/reference/tickers", {
            "limit": 50,
            "exchange": "NASDAQ"
        })
        data = self.assert_response_format(response, ["symbol", "name", "currency"])
        self.assertIsInstance(data, list)
        self.assertLessEqual(len(data), 50)
        
    def test_reference_ticker_profile(self):
        """Test GET /api/v1/reference/ticker/{symbol}"""
        response = self.make_request(f"/api/v1/reference/ticker/{self.test_symbol}")
        data = self.assert_response_format(response, ["symbol", "companyName", "sector"])
        
    def test_reference_ticker_executives(self):
        """Test GET /api/v1/reference/ticker/{symbol}/executives"""
        response = self.make_request(f"/api/v1/reference/ticker/{self.test_symbol}/executives")
        data = self.assert_response_format(response, ["name", "title"])
        
    def test_reference_ticker_outlook(self):
        """Test GET /api/v1/reference/ticker/{symbol}/outlook"""
        response = self.make_request(f"/api/v1/reference/ticker/{self.test_symbol}/outlook")
        data = self.assert_response_format(response, ["symbol", "profile"])
        
    def test_reference_exchanges(self):
        """Test GET /api/v1/reference/exchanges"""
        response = self.make_request("/api/v1/reference/exchanges")
        data = self.assert_response_format(response, ["name", "acronym", "country"])
        
    def test_reference_market_cap(self):
        """Test GET /api/v1/reference/market-cap/{symbol}"""
        response = self.make_request(f"/api/v1/reference/market-cap/{self.test_symbol}")
        data = self.assert_response_format(response, ["symbol", "marketCap"])
        
    def test_reference_market_status(self):
        """Test GET /api/v1/reference/market-status"""
        response = self.make_request("/api/v1/reference/market-status")
        data = self.assert_response_format(response, ["market", "exchanges"])
        
    def test_reference_market_holidays(self):
        """Test GET /api/v1/reference/market-holidays"""
        response = self.make_request("/api/v1/reference/market-holidays")
        data = self.assert_response_format(response, ["exchange", "name", "date"])

    # =============================================================================
    # MARKET DATA TESTS (15 endpoints)
    # =============================================================================
    
    def test_quotes_single(self):
        """Test GET /api/v1/quotes/{symbol}"""
        response = self.make_request(f"/api/v1/quotes/{self.test_symbol}")
        data = self.assert_response_format(response, ["symbol", "price", "change"])
        
    def test_quotes_batch(self):
        """Test GET /api/v1/quotes/batch"""
        response = self.make_request("/api/v1/quotes/batch", {
            "symbols": "AAPL,GOOGL,MSFT"
        })
        data = self.assert_response_format(response, ["symbol", "price"])
        self.assertLessEqual(len(data), 3)
        
    def test_quotes_gainers(self):
        """Test GET /api/v1/quotes/gainers"""
        response = self.make_request("/api/v1/quotes/gainers")
        data = self.assert_response_format(response, ["symbol", "changesPercentage"])
        
    def test_quotes_losers(self):
        """Test GET /api/v1/quotes/losers"""
        response = self.make_request("/api/v1/quotes/losers")
        data = self.assert_response_format(response, ["symbol", "changesPercentage"])
        
    def test_quotes_most_active(self):
        """Test GET /api/v1/quotes/most-active"""
        response = self.make_request("/api/v1/quotes/most-active")
        data = self.assert_response_format(response, ["symbol", "volume"])
        
    def test_quotes_last_trade(self):
        """Test GET /api/v1/quotes/{symbol}/last-trade"""
        response = self.make_request(f"/api/v1/quotes/{self.test_symbol}/last-trade")
        data = self.assert_response_format(response, ["results"])
        
    def test_quotes_last_quote(self):
        """Test GET /api/v1/quotes/{symbol}/last-quote"""
        response = self.make_request(f"/api/v1/quotes/{self.test_symbol}/last-quote")
        data = self.assert_response_format(response, ["results"])
        
    def test_quotes_previous_close(self):
        """Test GET /api/v1/quotes/{symbol}/previous-close"""
        response = self.make_request(f"/api/v1/quotes/{self.test_symbol}/previous-close")
        data = self.assert_response_format(response, ["results"])
        
    def test_historical_data(self):
        """Test GET /api/v1/historical/{symbol}"""
        response = self.make_request(f"/api/v1/historical/{self.test_symbol}", {
            "from": self.test_from_date,
            "to": self.test_to_date
        })
        data = self.assert_response_format(response, ["symbol", "historical"])
        
    def test_historical_intraday(self):
        """Test GET /api/v1/historical/{symbol}/intraday"""
        response = self.make_request(f"/api/v1/historical/{self.test_symbol}/intraday", {
            "interval": "5min",
            "from": self.test_date,
            "to": self.test_date
        })
        data = self.assert_response_format(response, ["date", "close"])
        
    def test_historical_dividends(self):
        """Test GET /api/v1/historical/{symbol}/dividends"""
        response = self.make_request(f"/api/v1/historical/{self.test_symbol}/dividends")
        data = self.assert_response_format(response, ["symbol", "historical"])
        
    def test_historical_splits(self):
        """Test GET /api/v1/historical/{symbol}/splits"""
        response = self.make_request(f"/api/v1/historical/{self.test_symbol}/splits")
        data = self.assert_response_format(response, ["symbol", "historical"])
        
    def test_historical_grouped(self):
        """Test GET /api/v1/historical/grouped/{date}"""
        response = self.make_request(f"/api/v1/historical/grouped/{self.test_date}")
        data = self.assert_response_format(response, ["results"])

    # =============================================================================
    # OPTIONS DATA TESTS (5 endpoints)
    # =============================================================================
    
    def test_options_contracts(self):
        """Test GET /api/v1/options/contracts"""
        response = self.make_request("/api/v1/options/contracts", {
            "underlying_ticker": self.test_symbol,
            "limit": 50
        })
        data = self.assert_response_format(response, ["results"])
        
    def test_options_chain(self):
        """Test GET /api/v1/options/chain/{symbol}"""
        response = self.make_request(f"/api/v1/options/chain/{self.test_symbol}")
        data = self.assert_response_format(response, ["results"])
        
    def test_options_greeks(self):
        """Test GET /api/v1/options/{symbol}/greeks"""
        response = self.make_request(f"/api/v1/options/{self.test_symbol}/greeks")
        data = self.assert_response_format(response, ["results"])
        
    def test_options_open_interest(self):
        """Test GET /api/v1/options/{symbol}/open-interest"""
        response = self.make_request(f"/api/v1/options/{self.test_symbol}/open-interest")
        data = self.assert_response_format(response, ["results"])
        
    def test_options_historical(self):
        """Test GET /api/v1/options/{contract}/historical"""
        contract = "O:AAPL240315C00150000"
        response = self.make_request(f"/api/v1/options/{contract}/historical", {
            "multiplier": 1,
            "timespan": "day",
            "from": self.test_from_date,
            "to": self.test_to_date
        })
        data = self.assert_response_format(response, ["results"])

    # =============================================================================
    # FUTURES DATA TESTS (3 endpoints)
    # =============================================================================
    
    def test_futures_contracts(self):
        """Test GET /api/v1/futures/contracts"""
        response = self.make_request("/api/v1/futures/contracts", {
            "underlying_ticker": "ES",
            "limit": 50
        })
        data = self.assert_response_format(response, ["results"])
        
    def test_futures_snapshot(self):
        """Test GET /api/v1/futures/{symbol}/snapshot"""
        response = self.make_request("/api/v1/futures/ES/snapshot")
        data = self.assert_response_format(response, ["results"])
        
    def test_futures_historical(self):
        """Test GET /api/v1/futures/{symbol}/historical"""
        response = self.make_request("/api/v1/futures/ES/historical", {
            "multiplier": 1,
            "timespan": "day",
            "from": self.test_from_date,
            "to": self.test_to_date
        })
        data = self.assert_response_format(response, ["results"])

    # =============================================================================
    # TICK-LEVEL DATA TESTS (3 endpoints)
    # =============================================================================
    
    def test_ticks_trades(self):
        """Test GET /api/v1/ticks/{symbol}/trades"""
        response = self.make_request(f"/api/v1/ticks/{self.test_symbol}/trades", {
            "limit": 100
        })
        data = self.assert_response_format(response, ["results"])
        
    def test_ticks_quotes(self):
        """Test GET /api/v1/ticks/{symbol}/quotes"""
        response = self.make_request(f"/api/v1/ticks/{self.test_symbol}/quotes", {
            "limit": 100
        })
        data = self.assert_response_format(response, ["results"])
        
    def test_ticks_aggs(self):
        """Test GET /api/v1/ticks/{symbol}/aggs"""
        response = self.make_request(f"/api/v1/ticks/{self.test_symbol}/aggs", {
            "multiplier": 1,
            "timespan": "minute",
            "from": self.test_date,
            "to": self.test_date,
            "limit": 100
        })
        data = self.assert_response_format(response, ["results"])

    # =============================================================================
    # FUNDAMENTAL DATA TESTS (8 endpoints)
    # =============================================================================
    
    def test_fundamentals_income_statement(self):
        """Test GET /api/v1/fundamentals/{symbol}/income-statement"""
        response = self.make_request(f"/api/v1/fundamentals/{self.test_symbol}/income-statement", {
            "period": "annual",
            "limit": 5
        })
        data = self.assert_response_format(response, ["revenue", "netIncome"])
        
    def test_fundamentals_balance_sheet(self):
        """Test GET /api/v1/fundamentals/{symbol}/balance-sheet"""
        response = self.make_request(f"/api/v1/fundamentals/{self.test_symbol}/balance-sheet", {
            "period": "annual",
            "limit": 5
        })
        data = self.assert_response_format(response, ["totalAssets", "totalLiabilities"])
        
    def test_fundamentals_cash_flow(self):
        """Test GET /api/v1/fundamentals/{symbol}/cash-flow"""
        response = self.make_request(f"/api/v1/fundamentals/{self.test_symbol}/cash-flow", {
            "period": "annual",
            "limit": 5
        })
        data = self.assert_response_format(response, ["operatingCashFlow", "freeCashFlow"])
        
    def test_fundamentals_ratios(self):
        """Test GET /api/v1/fundamentals/{symbol}/ratios"""
        response = self.make_request(f"/api/v1/fundamentals/{self.test_symbol}/ratios", {
            "period": "annual",
            "limit": 5
        })
        data = self.assert_response_format(response, ["currentRatio", "debtToEquity"])
        
    def test_fundamentals_metrics(self):
        """Test GET /api/v1/fundamentals/{symbol}/metrics"""
        response = self.make_request(f"/api/v1/fundamentals/{self.test_symbol}/metrics", {
            "period": "annual",
            "limit": 5
        })
        data = self.assert_response_format(response, ["marketCap", "peRatio"])
        
    def test_fundamentals_dcf(self):
        """Test GET /api/v1/fundamentals/{symbol}/dcf"""
        response = self.make_request(f"/api/v1/fundamentals/{self.test_symbol}/dcf")
        data = self.assert_response_format(response, ["dcf"])
        
    def test_fundamentals_enterprise_value(self):
        """Test GET /api/v1/fundamentals/{symbol}/enterprise-value"""
        response = self.make_request(f"/api/v1/fundamentals/{self.test_symbol}/enterprise-value", {
            "period": "annual",
            "limit": 5
        })
        data = self.assert_response_format(response, ["enterpriseValue"])
        
    def test_fundamentals_growth(self):
        """Test GET /api/v1/fundamentals/{symbol}/growth"""
        response = self.make_request(f"/api/v1/fundamentals/{self.test_symbol}/growth", {
            "period": "annual",
            "limit": 5
        })
        data = self.assert_response_format(response, ["revenueGrowth"])

    # =============================================================================
    # NEWS & SENTIMENT TESTS (5 endpoints)
    # =============================================================================
    
    def test_news_stock(self):
        """Test GET /api/v1/news/{symbol}"""
        response = self.make_request(f"/api/v1/news/{self.test_symbol}", {
            "limit": 10
        })
        data = self.assert_response_format(response, ["title", "publishedDate"])
        
    def test_news_general(self):
        """Test GET /api/v1/news/general"""
        response = self.make_request("/api/v1/news/general", {
            "limit": 20
        })
        data = self.assert_response_format(response, ["title", "publishedDate"])
        
    def test_news_press_releases(self):
        """Test GET /api/v1/news/{symbol}/press-releases"""
        response = self.make_request(f"/api/v1/news/{self.test_symbol}/press-releases", {
            "limit": 10
        })
        data = self.assert_response_format(response, ["title", "date"])
        
    def test_news_market(self):
        """Test GET /api/v1/news/market"""
        response = self.make_request("/api/v1/news/market", {
            "limit": 20
        })
        data = self.assert_response_format(response, ["title", "publishedDate"])
        
    def test_news_sentiment(self):
        """Test GET /api/v1/news/{symbol}/sentiment"""
        response = self.make_request(f"/api/v1/news/{self.test_symbol}/sentiment")
        data = self.assert_response_format(response, ["sentiment", "sentimentScore"])

    # =============================================================================
    # ANALYST DATA TESTS (4 endpoints)
    # =============================================================================
    
    def test_analysts_estimates(self):
        """Test GET /api/v1/analysts/{symbol}/estimates"""
        response = self.make_request(f"/api/v1/analysts/{self.test_symbol}/estimates", {
            "period": "quarter",
            "limit": 8
        })
        data = self.assert_response_format(response, ["estimatedEpsAvg"])
        
    def test_analysts_recommendations(self):
        """Test GET /api/v1/analysts/{symbol}/recommendations"""
        response = self.make_request(f"/api/v1/analysts/{self.test_symbol}/recommendations")
        data = self.assert_response_format(response, ["analystRatingsbuy"])
        
    def test_analysts_price_targets(self):
        """Test GET /api/v1/analysts/{symbol}/price-targets"""
        response = self.make_request(f"/api/v1/analysts/{self.test_symbol}/price-targets")
        data = self.assert_response_format(response, ["priceTarget"])
        
    def test_analysts_upgrades_downgrades(self):
        """Test GET /api/v1/analysts/{symbol}/upgrades-downgrades"""
        response = self.make_request(f"/api/v1/analysts/{self.test_symbol}/upgrades-downgrades")
        data = self.assert_response_format(response, ["newGrade"])

    # =============================================================================
    # EARNINGS DATA TESTS (4 endpoints)
    # =============================================================================
    
    def test_earnings_calendar(self):
        """Test GET /api/v1/earnings/calendar"""
        response = self.make_request("/api/v1/earnings/calendar", {
            "from": "2024-02-01",
            "to": "2024-02-07"
        })
        data = self.assert_response_format(response, ["symbol", "eps"])
        
    def test_earnings_transcripts(self):
        """Test GET /api/v1/earnings/{symbol}/transcripts"""
        response = self.make_request(f"/api/v1/earnings/{self.test_symbol}/transcripts", {
            "year": 2024,
            "quarter": 1
        })
        data = self.assert_response_format(response, ["content"])
        
    def test_earnings_history(self):
        """Test GET /api/v1/earnings/{symbol}/history"""
        response = self.make_request(f"/api/v1/earnings/{self.test_symbol}/history", {
            "limit": 20
        })
        data = self.assert_response_format(response, ["reportedEPS"])
        
    def test_earnings_surprises(self):
        """Test GET /api/v1/earnings/{symbol}/surprises"""
        response = self.make_request(f"/api/v1/earnings/{self.test_symbol}/surprises")
        data = self.assert_response_format(response, ["earningsSurprise"])

    # =============================================================================
    # CORPORATE EVENTS TESTS (3 endpoints)
    # =============================================================================
    
    def test_events_ipo_calendar(self):
        """Test GET /api/v1/events/ipo-calendar"""
        response = self.make_request("/api/v1/events/ipo-calendar", {
            "from": "2024-02-01",
            "to": "2024-02-29"
        })
        data = self.assert_response_format(response, ["company", "symbol"])
        
    def test_events_stock_split_calendar(self):
        """Test GET /api/v1/events/stock-split-calendar"""
        response = self.make_request("/api/v1/events/stock-split-calendar", {
            "from": "2024-02-01",
            "to": "2024-02-29"
        })
        data = self.assert_response_format(response, ["symbol", "numerator"])
        
    def test_events_dividend_calendar(self):
        """Test GET /api/v1/events/dividend-calendar"""
        response = self.make_request("/api/v1/events/dividend-calendar", {
            "from": "2024-02-01",
            "to": "2024-02-29"
        })
        data = self.assert_response_format(response, ["symbol", "dividend"])

    # =============================================================================
    # INSTITUTIONAL & INSIDER DATA TESTS (3 endpoints)
    # =============================================================================
    
    def test_institutional_13f(self):
        """Test GET /api/v1/institutional/{symbol}/13f"""
        response = self.make_request(f"/api/v1/institutional/{self.test_symbol}/13f", {
            "date": "2023-12-31"
        })
        data = self.assert_response_format(response, ["investorName", "shares"])
        
    def test_institutional_holders(self):
        """Test GET /api/v1/institutional/{symbol}/holders"""
        response = self.make_request(f"/api/v1/institutional/{self.test_symbol}/holders")
        data = self.assert_response_format(response, ["holder", "shares"])
        
    def test_institutional_insider_trading(self):
        """Test GET /api/v1/institutional/{symbol}/insider-trading"""
        response = self.make_request(f"/api/v1/institutional/{self.test_symbol}/insider-trading", {
            "limit": 20
        })
        data = self.assert_response_format(response, ["reportingName", "transactionType"])

    # =============================================================================
    # ECONOMIC DATA TESTS (5 endpoints)
    # =============================================================================
    
    def test_economy_gdp(self):
        """Test GET /api/v1/economy/gdp"""
        response = self.make_request("/api/v1/economy/gdp", {
            "from": "2020-01-01",
            "to": self.test_date
        })
        data = self.assert_response_format(response, ["date", "value"])
        
    def test_economy_inflation(self):
        """Test GET /api/v1/economy/inflation"""
        response = self.make_request("/api/v1/economy/inflation", {
            "from": "2020-01-01",
            "to": self.test_date
        })
        data = self.assert_response_format(response, ["date", "value"])
        
    def test_economy_unemployment(self):
        """Test GET /api/v1/economy/unemployment"""
        response = self.make_request("/api/v1/economy/unemployment", {
            "from": "2020-01-01",
            "to": self.test_date
        })
        data = self.assert_response_format(response, ["date", "value"])
        
    def test_economy_treasury_rates(self):
        """Test GET /api/v1/economy/treasury-rates"""
        response = self.make_request("/api/v1/economy/treasury-rates", {
            "from": self.test_from_date,
            "to": self.test_to_date
        })
        data = self.assert_response_format(response, ["date", "year10"])
        
    def test_economy_federal_funds_rate(self):
        """Test GET /api/v1/economy/federal-funds-rate"""
        response = self.make_request("/api/v1/economy/federal-funds-rate", {
            "from": "2020-01-01",
            "to": self.test_date
        })
        data = self.assert_response_format(response, ["date", "value"])

    # =============================================================================
    # ETF & MUTUAL FUNDS TESTS (4 endpoints)
    # =============================================================================
    
    def test_etf_list(self):
        """Test GET /api/v1/etf/list"""
        response = self.make_request("/api/v1/etf/list", {
            "limit": 100
        })
        data = self.assert_response_format(response, ["symbol", "name"])
        
    def test_etf_holdings(self):
        """Test GET /api/v1/etf/{symbol}/holdings"""
        response = self.make_request("/api/v1/etf/SPY/holdings")
        data = self.assert_response_format(response, ["asset", "weightPercentage"])
        
    def test_etf_performance(self):
        """Test GET /api/v1/etf/{symbol}/performance"""
        response = self.make_request("/api/v1/etf/SPY/performance")
        data = self.assert_response_format(response, ["oneDay", "oneYear"])
        
    def test_mutual_funds_list(self):
        """Test GET /api/v1/mutual-funds/list"""
        response = self.make_request("/api/v1/mutual-funds/list", {
            "limit": 100
        })
        data = self.assert_response_format(response, ["symbol", "name"])

    # =============================================================================
    # COMMODITIES TESTS (4 endpoints)
    # =============================================================================
    
    def test_commodities_list(self):
        """Test GET /api/v1/commodities/list"""
        response = self.make_request("/api/v1/commodities/list")
        data = self.assert_response_format(response, ["symbol", "name", "price"])
        
    def test_commodities_metals(self):
        """Test GET /api/v1/commodities/metals"""
        response = self.make_request("/api/v1/commodities/metals")
        data = self.assert_response_format(response, ["symbol", "name", "price"])
        
    def test_commodities_energy(self):
        """Test GET /api/v1/commodities/energy"""
        response = self.make_request("/api/v1/commodities/energy")
        data = self.assert_response_format(response, ["symbol", "name", "price"])
        
    def test_commodities_historical(self):
        """Test GET /api/v1/commodities/{symbol}/historical"""
        response = self.make_request("/api/v1/commodities/GCUSD/historical", {
            "from": self.test_from_date,
            "to": self.test_to_date
        })
        data = self.assert_response_format(response, ["symbol", "historical"])

    # =============================================================================
    # CRYPTOCURRENCIES TESTS (3 endpoints)
    # =============================================================================
    
    def test_crypto_list(self):
        """Test GET /api/v1/crypto/list"""
        response = self.make_request("/api/v1/crypto/list", {
            "limit": 50
        })
        data = self.assert_response_format(response, ["symbol", "name", "price"])
        
    def test_crypto_quote(self):
        """Test GET /api/v1/crypto/{symbol}"""
        response = self.make_request("/api/v1/crypto/BTCUSD")
        data = self.assert_response_format(response, ["symbol", "price"])
        
    def test_crypto_historical(self):
        """Test GET /api/v1/crypto/{symbol}/historical"""
        response = self.make_request("/api/v1/crypto/BTCUSD/historical", {
            "from": self.test_from_date,
            "to": self.test_to_date
        })
        data = self.assert_response_format(response, ["symbol", "historical"])

    # =============================================================================
    # INTERNATIONAL MARKETS TESTS (4 endpoints)
    # =============================================================================
    
    def test_international_exchanges(self):
        """Test GET /api/v1/international/exchanges"""
        response = self.make_request("/api/v1/international/exchanges")
        data = self.assert_response_format(response, ["name", "country"])
        
    def test_forex_rates(self):
        """Test GET /api/v1/forex/rates"""
        response = self.make_request("/api/v1/forex/rates", {
            "base": "USD"
        })
        data = self.assert_response_format(response, ["ticker", "bid", "ask"])
        
    def test_forex_historical(self):
        """Test GET /api/v1/forex/{pair}/historical"""
        response = self.make_request("/api/v1/forex/EURUSD/historical", {
            "from": self.test_from_date,
            "to": self.test_to_date
        })
        data = self.assert_response_format(response, ["symbol", "historical"])
        
    def test_international_stocks(self):
        """Test GET /api/v1/international/stocks/{exchange}"""
        response = self.make_request("/api/v1/international/stocks/LSE", {
            "limit": 50
        })
        data = self.assert_response_format(response, ["symbol", "name"])

    # =============================================================================
    # SEC FILINGS TESTS (5 endpoints)
    # =============================================================================
    
    def test_sec_filings(self):
        """Test GET /api/v1/sec/{symbol}/filings"""
        response = self.make_request(f"/api/v1/sec/{self.test_symbol}/filings", {
            "type": "10-K",
            "limit": 10
        })
        data = self.assert_response_format(response, ["type", "link"])
        
    def test_sec_10k(self):
        """Test GET /api/v1/sec/{symbol}/10k"""
        response = self.make_request(f"/api/v1/sec/{self.test_symbol}/10k", {
            "limit": 5
        })
        data = self.assert_response_format(response, ["type", "link"])
        
    def test_sec_10q(self):
        """Test GET /api/v1/sec/{symbol}/10q"""
        response = self.make_request(f"/api/v1/sec/{self.test_symbol}/10q", {
            "limit": 5
        })
        data = self.assert_response_format(response, ["type", "link"])
        
    def test_sec_8k(self):
        """Test GET /api/v1/sec/{symbol}/8k"""
        response = self.make_request(f"/api/v1/sec/{self.test_symbol}/8k", {
            "limit": 5
        })
        data = self.assert_response_format(response, ["type", "link"])
        
    def test_sec_rss_feed(self):
        """Test GET /api/v1/sec/rss-feed"""
        response = self.make_request("/api/v1/sec/rss-feed", {
            "limit": 20
        })
        data = self.assert_response_format(response, ["title", "formType"])

    # =============================================================================
    # TECHNICAL INDICATORS TESTS (8 endpoints)
    # =============================================================================
    
    def test_technical_sma(self):
        """Test GET /api/v1/technical/{symbol}/sma"""
        response = self.make_request(f"/api/v1/technical/{self.test_symbol}/sma", {
            "period": 20,
            "type": "close"
        })
        data = self.assert_response_format(response, ["date", "sma"])
        
    def test_technical_ema(self):
        """Test GET /api/v1/technical/{symbol}/ema"""
        response = self.make_request(f"/api/v1/technical/{self.test_symbol}/ema", {
            "period": 12,
            "type": "close"
        })
        data = self.assert_response_format(response, ["date", "ema"])
        
    def test_technical_rsi(self):
        """Test GET /api/v1/technical/{symbol}/rsi"""
        response = self.make_request(f"/api/v1/technical/{self.test_symbol}/rsi", {
            "period": 14,
            "type": "close"
        })
        data = self.assert_response_format(response, ["date", "rsi"])
        
    def test_technical_macd(self):
        """Test GET /api/v1/technical/{symbol}/macd"""
        response = self.make_request(f"/api/v1/technical/{self.test_symbol}/macd", {
            "short_period": 12,
            "long_period": 26,
            "signal_period": 9
        })
        data = self.assert_response_format(response, ["date", "macd", "signal"])
        
    def test_technical_bollinger_bands(self):
        """Test GET /api/v1/technical/{symbol}/bollinger-bands"""
        response = self.make_request(f"/api/v1/technical/{self.test_symbol}/bollinger-bands", {
            "period": 20,
            "std_dev": 2
        })
        data = self.assert_response_format(response, ["date", "upperBand", "lowerBand"])
        
    def test_technical_stochastic(self):
        """Test GET /api/v1/technical/{symbol}/stochastic"""
        response = self.make_request(f"/api/v1/technical/{self.test_symbol}/stochastic", {
            "k_period": 14,
            "d_period": 3
        })
        data = self.assert_response_format(response, ["date", "k_percent", "d_percent"])
        
    def test_technical_adx(self):
        """Test GET /api/v1/technical/{symbol}/adx"""
        response = self.make_request(f"/api/v1/technical/{self.test_symbol}/adx", {
            "period": 14
        })
        data = self.assert_response_format(response, ["date", "adx"])
        
    def test_technical_williams_r(self):
        """Test GET /api/v1/technical/{symbol}/williams-r"""
        response = self.make_request(f"/api/v1/technical/{self.test_symbol}/williams-r", {
            "period": 14
        })
        data = self.assert_response_format(response, ["date", "williams_r"])

    # =============================================================================
    # BULK DATA TESTS (3 endpoints)
    # =============================================================================
    
    def test_bulk_eod_prices(self):
        """Test GET /api/v1/bulk/eod-prices"""
        response = self.make_request("/api/v1/bulk/eod-prices", {
            "date": self.test_date,
            "exchange": "NASDAQ"
        })
        data = self.assert_response_format(response, ["symbol", "close"])
        
    def test_bulk_fundamentals(self):
        """Test GET /api/v1/bulk/fundamentals"""
        response = self.make_request("/api/v1/bulk/fundamentals", {
            "year": 2023,
            "period": "annual"
        })
        data = self.assert_response_format(response, ["symbol", "revenue"])
        
    def test_bulk_insider_trading(self):
        """Test GET /api/v1/bulk/insider-trading"""
        response = self.make_request("/api/v1/bulk/insider-trading", {
            "date": self.test_date
        })
        data = self.assert_response_format(response, ["symbol", "transactionType"])

    # =============================================================================
    # SYSTEM ENDPOINTS TESTS (3 endpoints)
    # =============================================================================
    
    def test_health_check(self):
        """Test GET /health"""
        response = self.make_request("/health", check_metadata=False)
        data = self.assert_response_format(response, ["status", "providers"], check_metadata=False)
        self.assertEqual(data["status"], "healthy")
        
    def test_endpoints_list(self):
        """Test GET /api/v1/endpoints"""
        response = self.make_request("/api/v1/endpoints", check_metadata=False)
        data = self.assert_response_format(response, ["total_endpoints", "endpoints"], check_metadata=False)
        self.assertGreater(data["total_endpoints"], 90)
        
    def test_batch_request(self):
        """Test POST /api/v1/batch"""
        batch_data = {
            "requests": [
                {"path": f"quotes/{self.test_symbol}"},
                {"path": "quotes/GOOGL"},
                {"path": f"fundamentals/{self.test_symbol}/ratios"}
            ]
        }
        response = self.make_request("/api/v1/batch", method="POST", data=batch_data, check_metadata=False)
        data = self.assert_response_format(response, ["results", "total"], check_metadata=False)
        self.assertEqual(data["total"], 3)
        self.assertEqual(len(data["results"]), 3)

    # =============================================================================
    # ERROR HANDLING TESTS
    # =============================================================================
    
    def test_invalid_symbol_404(self):
        """Test 404 error for invalid symbol"""
        response = self.make_request("/api/v1/quotes/INVALID_SYMBOL_123")
        self.assertEqual(response.status_code, 404)
        
    def test_invalid_endpoint_404(self):
        """Test 404 error for invalid endpoint"""
        response = self.make_request("/api/v1/invalid/endpoint")
        self.assertEqual(response.status_code, 404)
        
    def test_missing_required_params_400(self):
        """Test 400 error for missing required parameters"""
        response = self.make_request("/api/v1/options/O:AAPL240315C00150000/historical")
        self.assertEqual(response.status_code, 400)

    # =============================================================================
    # CACHING TESTS
    # =============================================================================
    
    def test_cache_behavior(self):
        """Test caching behavior"""
        # First request should be from live source
        response1 = self.make_request(f"/api/v1/quotes/{self.test_symbol}")
        data1 = self.assert_response_format(response1)
        
        # Second request should potentially be from cache
        response2 = self.make_request(f"/api/v1/quotes/{self.test_symbol}")
        data2 = self.assert_response_format(response2)
        
        # Both should return valid data
        self.assertIsNotNone(data1)
        self.assertIsNotNone(data2)

    # =============================================================================
    # PROVIDER ROUTING TESTS
    # =============================================================================
    
    def test_polygon_provider_routing(self):
        """Test that Polygon.io endpoints route correctly"""
        polygon_endpoints = [
            "/api/v1/options/contracts",
            "/api/v1/futures/contracts",
            "/api/v1/reference/market-status",
            f"/api/v1/ticks/{self.test_symbol}/trades"
        ]
        
        for endpoint in polygon_endpoints:
            with self.subTest(endpoint=endpoint):
                response = self.make_request(endpoint)
                if response.status_code == 200:
                    data = response.json()
                    if isinstance(data, dict) and '_metadata' in data:
                        self.assertEqual(data['_metadata']['provider'], 'polygon')
    
    def test_fmp_provider_routing(self):
        """Test that FMP endpoints route correctly"""
        fmp_endpoints = [
            f"/api/v1/quotes/{self.test_symbol}",
            f"/api/v1/fundamentals/{self.test_symbol}/income-statement",
            f"/api/v1/news/{self.test_symbol}",
            "/api/v1/reference/exchanges"
        ]
        
        for endpoint in fmp_endpoints:
            with self.subTest(endpoint=endpoint):
                response = self.make_request(endpoint)
                if response.status_code == 200:
                    data = response.json()
                    if isinstance(data, dict) and '_metadata' in data:
                        self.assertEqual(data['_metadata']['provider'], 'fmp')


if __name__ == "__main__":
    # Set up test configuration
    import sys
    
    # Configure unittest for verbose output
    unittest.main(verbosity=2, argv=sys.argv[:1]) 