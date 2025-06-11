"""
Complete Configuration for Financial Data API - 100% Feature Coverage
All endpoints from both Polygon.io and FMP Ultimate included
"""
import os

# API Keys (from environment variables)
FMP_API_KEY = os.getenv('FMP_API_KEY', 'your_fmp_ultimate_api_key')
POLYGON_API_KEY = os.getenv('POLYGON_API_KEY', 'your_polygon_api_key')

# Provider URLs
PROVIDER_URLS = {
    'polygon': 'https://api.polygon.io',
    'fmp': 'https://financialmodelingprep.com/api'
}

# Cache TTL (Time To Live) in seconds
CACHE_TTL = {
    'real_time': 30,        # Real-time quotes, trades
    'intraday': 300,        # 5 minutes for intraday
    'daily': 3600,          # 1 hour for daily data
    'fundamental': 86400,   # 24 hours for fundamentals
    'news': 1800,           # 30 minutes for news
    'static': 604800        # 1 week for static data
}

# Rate limits (calls per minute)
RATE_LIMITS = {
    'polygon': 1000,
    'fmp': 3000
}

# COMPLETE Endpoint routing configuration - 100% Coverage
ENDPOINT_ROUTES = {
    
    # ==================== REFERENCE DATA ====================
    
    # Basic Reference
    "reference/tickers": {
        "provider": "fmp", 
        "endpoint": "/v3/stock/list", 
        "cache": "static"
    },
    "reference/ticker/{symbol}": {
        "provider": "fmp", 
        "endpoint": "/v3/profile/{symbol}", 
        "cache": "daily"
    },
    "reference/ticker/{symbol}/profile": {
        "provider": "fmp", 
        "endpoint": "/v3/profile/{symbol}", 
        "cache": "daily"
    },
    "reference/ticker/{symbol}/executives": {
        "provider": "fmp", 
        "endpoint": "/v3/key-executives/{symbol}", 
        "cache": "static"
    },
    "reference/ticker/{symbol}/outlook": {
        "provider": "fmp", 
        "endpoint": "/v4/company-outlook", 
        "cache": "daily",
        "params": {"symbol": "{symbol}"}
    },
    "reference/exchanges": {
        "provider": "fmp", 
        "endpoint": "/v3/exchanges-list", 
        "cache": "static"
    },
    "reference/market-cap/{symbol}": {
        "provider": "fmp", 
        "endpoint": "/v3/market-capitalization/{symbol}", 
        "cache": "daily"
    },
    
    # Market Status (Polygon.io)
    "reference/market-status": {
        "provider": "polygon", 
        "endpoint": "/v1/marketstatus/now", 
        "cache": "real_time"
    },
    "reference/market-holidays": {
        "provider": "polygon", 
        "endpoint": "/v1/marketstatus/upcoming", 
        "cache": "static"
    },
    
    # ==================== MARKET DATA ====================
    
    # Real-time Quotes
    "quotes/{symbol}": {
        "provider": "fmp", 
        "endpoint": "/v3/quote/{symbol}", 
        "cache": "real_time"
    },
    "quotes/batch": {
        "provider": "fmp", 
        "endpoint": "/v3/quote/{symbols}", 
        "cache": "real_time"
    },
    "quotes/gainers": {
        "provider": "fmp", 
        "endpoint": "/v3/gainers", 
        "cache": "real_time"
    },
    "quotes/losers": {
        "provider": "fmp", 
        "endpoint": "/v3/losers", 
        "cache": "real_time"
    },
    "quotes/most-active": {
        "provider": "fmp", 
        "endpoint": "/v3/actives", 
        "cache": "real_time"
    },
    
    # Last Trade/Quote (Polygon.io)
    "quotes/{symbol}/last-trade": {
        "provider": "polygon", 
        "endpoint": "/v2/last/trade/{symbol}", 
        "cache": "real_time"
    },
    "quotes/{symbol}/last-quote": {
        "provider": "polygon", 
        "endpoint": "/v2/last/nbbo/{symbol}", 
        "cache": "real_time"
    },
    "quotes/{symbol}/previous-close": {
        "provider": "polygon", 
        "endpoint": "/v2/aggs/ticker/{symbol}/prev", 
        "cache": "daily"
    },
    
    # Historical Data
    "historical/{symbol}": {
        "provider": "fmp", 
        "endpoint": "/v3/historical-price-full/{symbol}", 
        "cache": "daily"
    },
    "historical/{symbol}/intraday": {
        "provider": "fmp", 
        "endpoint": "/v3/historical-chart/{interval}/{symbol}", 
        "cache": "intraday"
    },
    "historical/{symbol}/dividends": {
        "provider": "fmp", 
        "endpoint": "/v3/historical-price-full/stock_dividend/{symbol}", 
        "cache": "daily"
    },
    "historical/{symbol}/splits": {
        "provider": "fmp", 
        "endpoint": "/v3/historical-price-full/stock_split/{symbol}", 
        "cache": "daily"
    },
    
    # Grouped Daily (Polygon.io)
    "historical/grouped/{date}": {
        "provider": "polygon", 
        "endpoint": "/v2/aggs/grouped/locale/us/market/stocks/{date}", 
        "cache": "daily"
    },
    
    # ==================== OPTIONS DATA (Polygon.io Exclusive) ====================
    
    "options/contracts": {
        "provider": "polygon", 
        "endpoint": "/v3/reference/options/contracts", 
        "cache": "daily"
    },
    "options/chain/{symbol}": {
        "provider": "polygon", 
        "endpoint": "/v3/snapshot/options/{symbol}", 
        "cache": "real_time"
    },
    "options/{symbol}/greeks": {
        "provider": "polygon", 
        "endpoint": "/v3/snapshot/options/{symbol}", 
        "cache": "real_time"
    },
    "options/{symbol}/open-interest": {
        "provider": "polygon", 
        "endpoint": "/v3/snapshot/options/{symbol}", 
        "cache": "real_time"
    },
    "options/{contract}/historical": {
        "provider": "polygon", 
        "endpoint": "/v2/aggs/ticker/{contract}/range/{multiplier}/{timespan}/{from}/{to}", 
        "cache": "daily"
    },
    
    # ==================== FUTURES DATA (Polygon.io Exclusive) ====================
    
    "futures/contracts": {
        "provider": "polygon", 
        "endpoint": "/v3/reference/futures/contracts", 
        "cache": "daily"
    },
    "futures/{symbol}/snapshot": {
        "provider": "polygon", 
        "endpoint": "/v2/snapshot/locale/global/markets/futures/tickers/{symbol}", 
        "cache": "real_time"
    },
    "futures/{symbol}/historical": {
        "provider": "polygon", 
        "endpoint": "/v2/aggs/ticker/{symbol}/range/{multiplier}/{timespan}/{from}/{to}", 
        "cache": "daily"
    },
    
    # ==================== TICK-LEVEL DATA (Polygon.io Exclusive) ====================
    
    "ticks/{symbol}/trades": {
        "provider": "polygon", 
        "endpoint": "/v3/trades/{symbol}", 
        "cache": "real_time"
    },
    "ticks/{symbol}/quotes": {
        "provider": "polygon", 
        "endpoint": "/v3/quotes/{symbol}", 
        "cache": "real_time"
    },
    "ticks/{symbol}/aggregates": {
        "provider": "polygon", 
        "endpoint": "/v2/aggs/ticker/{symbol}/range/{multiplier}/{timespan}/{from}/{to}", 
        "cache": "intraday"
    },
    
    # ==================== FUNDAMENTAL DATA (FMP Exclusive) ====================
    
    # Financial Statements
    "fundamentals/{symbol}/income-statement": {
        "provider": "fmp", 
        "endpoint": "/v3/income-statement/{symbol}", 
        "cache": "fundamental"
    },
    "fundamentals/{symbol}/balance-sheet": {
        "provider": "fmp", 
        "endpoint": "/v3/balance-sheet-statement/{symbol}", 
        "cache": "fundamental"
    },
    "fundamentals/{symbol}/cash-flow": {
        "provider": "fmp", 
        "endpoint": "/v3/cash-flow-statement/{symbol}", 
        "cache": "fundamental"
    },
    "fundamentals/{symbol}/ratios": {
        "provider": "fmp", 
        "endpoint": "/v3/ratios/{symbol}", 
        "cache": "fundamental"
    },
    
    # Valuation & Metrics
    "fundamentals/{symbol}/dcf": {
        "provider": "fmp", 
        "endpoint": "/v3/discounted-cash-flow/{symbol}", 
        "cache": "fundamental"
    },
    "fundamentals/{symbol}/metrics": {
        "provider": "fmp", 
        "endpoint": "/v3/key-metrics/{symbol}", 
        "cache": "fundamental"
    },
    "fundamentals/{symbol}/enterprise-value": {
        "provider": "fmp", 
        "endpoint": "/v3/enterprise-values/{symbol}", 
        "cache": "fundamental"
    },
    "fundamentals/screener": {
        "provider": "fmp", 
        "endpoint": "/v3/stock-screener", 
        "cache": "daily"
    },
    
    # ==================== NEWS & SENTIMENT (FMP Exclusive) ====================
    
    "news": {
        "provider": "fmp", 
        "endpoint": "/v3/stock_news", 
        "cache": "news"
    },
    "news/{symbol}": {
        "provider": "fmp", 
        "endpoint": "/v3/stock_news", 
        "cache": "news",
        "params": {"tickers": "{symbol}"}
    },
    "news/press-releases": {
        "provider": "fmp", 
        "endpoint": "/v3/press-releases", 
        "cache": "news"
    },
    "news/{symbol}/press-releases": {
        "provider": "fmp", 
        "endpoint": "/v3/press-releases/{symbol}", 
        "cache": "news"
    },
    "news/sentiment": {
        "provider": "fmp", 
        "endpoint": "/v4/historical/social-sentiment", 
        "cache": "news"
    },
    
    # ==================== ANALYST DATA (FMP Exclusive) ====================
    
    "analysts/{symbol}/estimates": {
        "provider": "fmp", 
        "endpoint": "/v3/analyst-estimates/{symbol}", 
        "cache": "daily"
    },
    "analysts/{symbol}/recommendations": {
        "provider": "fmp", 
        "endpoint": "/v3/analyst-stock-recommendations/{symbol}", 
        "cache": "daily"
    },
    "analysts/{symbol}/price-targets": {
        "provider": "fmp", 
        "endpoint": "/v4/price-target", 
        "cache": "daily",
        "params": {"symbol": "{symbol}"}
    },
    "analysts/{symbol}/upgrades-downgrades": {
        "provider": "fmp", 
        "endpoint": "/v4/upgrades-downgrades", 
        "cache": "daily",
        "params": {"symbol": "{symbol}"}
    },
    
    # ==================== EARNINGS DATA (FMP Exclusive) ====================
    
    "earnings/{symbol}/calendar": {
        "provider": "fmp", 
        "endpoint": "/v3/earning_calendar", 
        "cache": "daily",
        "params": {"symbol": "{symbol}"}
    },
    "earnings/{symbol}/transcripts": {
        "provider": "fmp", 
        "endpoint": "/v4/batch_earning_call_transcript/{symbol}", 
        "cache": "fundamental"
    },
    "earnings/{symbol}/history": {
        "provider": "fmp", 
        "endpoint": "/v3/historical/earning_calendar/{symbol}", 
        "cache": "fundamental"
    },
    "earnings/{symbol}/surprises": {
        "provider": "fmp", 
        "endpoint": "/v3/earnings-surprises/{symbol}", 
        "cache": "fundamental"
    },
    
    # ==================== CORPORATE EVENTS (FMP Exclusive) ====================
    
    "events/ipo-calendar": {
        "provider": "fmp", 
        "endpoint": "/v3/ipo_calendar", 
        "cache": "daily"
    },
    "events/stock-split-calendar": {
        "provider": "fmp", 
        "endpoint": "/v3/stock_split_calendar", 
        "cache": "daily"
    },
    "events/dividend-calendar": {
        "provider": "fmp", 
        "endpoint": "/v3/stock_dividend_calendar", 
        "cache": "daily"
    },
    
    # ==================== INSTITUTIONAL & INSIDER DATA (FMP Exclusive) ====================
    
    "institutional/{symbol}/13f": {
        "provider": "fmp", 
        "endpoint": "/v3/form-thirteen/{symbol}", 
        "cache": "fundamental"
    },
    "institutional/{symbol}/holders": {
        "provider": "fmp", 
        "endpoint": "/v3/institutional-holder/{symbol}", 
        "cache": "fundamental"
    },
    "institutional/{symbol}/insider-trading": {
        "provider": "fmp", 
        "endpoint": "/v4/insider-trading", 
        "cache": "daily",
        "params": {"symbol": "{symbol}"}
    },
    
    # ==================== ECONOMIC DATA (FMP Exclusive) ====================
    
    "economy/gdp": {
        "provider": "fmp", 
        "endpoint": "/v4/economic", 
        "cache": "fundamental",
        "params": {"name": "GDP"}
    },
    "economy/inflation": {
        "provider": "fmp", 
        "endpoint": "/v4/economic", 
        "cache": "fundamental",
        "params": {"name": "CPI"}
    },
    "economy/unemployment": {
        "provider": "fmp", 
        "endpoint": "/v4/economic", 
        "cache": "fundamental",
        "params": {"name": "unemploymentRate"}
    },
    "economy/interest-rates": {
        "provider": "fmp", 
        "endpoint": "/v4/economic", 
        "cache": "fundamental",
        "params": {"name": "federalFunds"}
    },
    "economy/treasury-rates": {
        "provider": "fmp", 
        "endpoint": "/v4/treasury", 
        "cache": "daily"
    },
    
    # ==================== ETF & MUTUAL FUNDS (FMP Exclusive) ====================
    
    "etf/list": {
        "provider": "fmp", 
        "endpoint": "/v3/etf/list", 
        "cache": "static"
    },
    "etf/{symbol}/holdings": {
        "provider": "fmp", 
        "endpoint": "/v3/etf-holder/{symbol}", 
        "cache": "daily"
    },
    "etf/{symbol}/performance": {
        "provider": "fmp", 
        "endpoint": "/v4/etf-info", 
        "cache": "daily",
        "params": {"symbol": "{symbol}"}
    },
    "mutual-funds/list": {
        "provider": "fmp", 
        "endpoint": "/v3/mutual-fund/list", 
        "cache": "static"
    },
    
    # ==================== COMMODITIES (FMP Exclusive) ====================
    
    "commodities/metals": {
        "provider": "fmp", 
        "endpoint": "/v3/quotes/commodity", 
        "cache": "real_time"
    },
    "commodities/energy": {
        "provider": "fmp", 
        "endpoint": "/v3/quotes/commodity", 
        "cache": "real_time"
    },
    "commodities/agricultural": {
        "provider": "fmp", 
        "endpoint": "/v3/quotes/commodity", 
        "cache": "real_time"
    },
    "commodities/{symbol}/historical": {
        "provider": "fmp", 
        "endpoint": "/v3/historical-price-full/{symbol}", 
        "cache": "daily"
    },
    
    # ==================== CRYPTOCURRENCIES (FMP Exclusive) ====================
    
    "crypto/list": {
        "provider": "fmp", 
        "endpoint": "/v3/quotes/crypto", 
        "cache": "real_time"
    },
    "crypto/{symbol}": {
        "provider": "fmp", 
        "endpoint": "/v3/quote/{symbol}", 
        "cache": "real_time"
    },
    "crypto/{symbol}/historical": {
        "provider": "fmp", 
        "endpoint": "/v3/historical-price-full/{symbol}", 
        "cache": "daily"
    },
    
    # ==================== INTERNATIONAL MARKETS (FMP Exclusive) ====================
    
    "international/exchanges": {
        "provider": "fmp", 
        "endpoint": "/v3/exchanges-list", 
        "cache": "static"
    },
    "international/{exchange}/stocks": {
        "provider": "fmp", 
        "endpoint": "/v3/available-traded/list", 
        "cache": "static",
        "params": {"exchange": "{exchange}"}
    },
    "forex/rates": {
        "provider": "fmp", 
        "endpoint": "/v3/fx", 
        "cache": "real_time"
    },
    "forex/{pair}": {
        "provider": "fmp", 
        "endpoint": "/v3/historical-price-full/{pair}", 
        "cache": "daily"
    },
    
    # ==================== SEC FILINGS (FMP Exclusive) ====================
    
    "sec/{symbol}/filings": {
        "provider": "fmp", 
        "endpoint": "/v3/sec_filings/{symbol}", 
        "cache": "daily"
    },
    "sec/{symbol}/10k": {
        "provider": "fmp", 
        "endpoint": "/v3/sec_filings/{symbol}", 
        "cache": "fundamental",
        "params": {"type": "10-K"}
    },
    "sec/{symbol}/10q": {
        "provider": "fmp", 
        "endpoint": "/v3/sec_filings/{symbol}", 
        "cache": "fundamental",
        "params": {"type": "10-Q"}
    },
    "sec/{symbol}/8k": {
        "provider": "fmp", 
        "endpoint": "/v3/sec_filings/{symbol}", 
        "cache": "daily",
        "params": {"type": "8-K"}
    },
    "sec/rss-feed": {
        "provider": "fmp", 
        "endpoint": "/v4/rss_feed", 
        "cache": "news"
    },
    
    # ==================== TECHNICAL INDICATORS ====================
    
    # Basic Technical Indicators
    "technical/{symbol}/sma": {
        "provider": "fmp", 
        "endpoint": "/v3/technical_indicator/{timespan}/{symbol}", 
        "cache": "intraday",
        "params": {"type": "SMA"}
    },
    "technical/{symbol}/ema": {
        "provider": "fmp", 
        "endpoint": "/v3/technical_indicator/{timespan}/{symbol}", 
        "cache": "intraday",
        "params": {"type": "EMA"}
    },
    "technical/{symbol}/rsi": {
        "provider": "fmp", 
        "endpoint": "/v3/technical_indicator/{timespan}/{symbol}", 
        "cache": "intraday",
        "params": {"type": "RSI"}
    },
    "technical/{symbol}/macd": {
        "provider": "fmp", 
        "endpoint": "/v3/technical_indicator/{timespan}/{symbol}", 
        "cache": "intraday",
        "params": {"type": "MACD"}
    },
    
    # Advanced Technical Indicators
    "technical/{symbol}/bollinger-bands": {
        "provider": "fmp", 
        "endpoint": "/v3/technical_indicator/{timespan}/{symbol}", 
        "cache": "intraday",
        "params": {"type": "BBANDS"}
    },
    "technical/{symbol}/stochastic": {
        "provider": "fmp", 
        "endpoint": "/v3/technical_indicator/{timespan}/{symbol}", 
        "cache": "intraday",
        "params": {"type": "STOCH"}
    },
    "technical/{symbol}/adx": {
        "provider": "fmp", 
        "endpoint": "/v3/technical_indicator/{timespan}/{symbol}", 
        "cache": "intraday",
        "params": {"type": "ADX"}
    },
    "technical/{symbol}/williams-r": {
        "provider": "fmp", 
        "endpoint": "/v3/technical_indicator/{timespan}/{symbol}", 
        "cache": "intraday",
        "params": {"type": "WILLR"}
    },
    
    # ==================== BULK DATA (FMP Exclusive) ====================
    
    "bulk/eod-prices": {
        "provider": "fmp", 
        "endpoint": "/v4/batch-request-end-of-day-prices", 
        "cache": "daily"
    },
    "bulk/fundamentals": {
        "provider": "fmp", 
        "endpoint": "/v4/batch-request-financial-statements", 
        "cache": "fundamental"
    },
    "bulk/insider-trading": {
        "provider": "fmp", 
        "endpoint": "/v4/insider-trading-rss-feed", 
        "cache": "daily"
    }
}

# Custom exceptions
class FinancialAPIError(Exception):
    """Base exception for Financial API"""
    pass

class ProviderError(FinancialAPIError):
    """Provider-specific error"""
    def __init__(self, provider, message, status_code=None):
        self.provider = provider
        self.status_code = status_code
        super().__init__(f"[{provider}] {message}")

class EndpointNotFoundError(FinancialAPIError):
    """Endpoint not found error"""
    pass

class RateLimitError(FinancialAPIError):
    """Rate limit exceeded error"""
    pass 