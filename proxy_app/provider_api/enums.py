from __future__ import annotations

from enum import Enum


class EndpointFrom(Enum):
    # Reference
    REFERENCE_TICKERS = "/api/v1/reference/tickers/"
    REFERENCE_TICKER = "/api/v1/reference/ticker/{symbol}/"
    REFERENCE_TICKER_PROFILE = "/api/v1/reference/ticker/{symbol}/profile/"
    REFERENCE_TICKER_EXECUTIVES = "/api/v1/reference/ticker/{symbol}/executives/"
    REFERENCE_TICKER_OUTLOOK = "/api/v1/reference/ticker/{symbol}/outlook/"
    REFERENCE_EXCHANGES = "/api/v1/reference/exchanges/"
    REFERENCE_MARKET_CAP = "/api/v1/reference/market-cap/{symbol}/"
    REFERENCE_MARKET_STATUS = "/api/v1/reference/market-status/"
    REFERENCE_MARKET_HOLIDAYS = "/api/v1/reference/market-holidays/"

    # Market Data
    QUOTES_SINGLE = "/api/v1/quotes/{symbol}/"
    QUOTES_BATCH = "/api/v1/quotes/batch/"
    QUOTES_GAINERS = "/api/v1/quotes/gainers/"
    QUOTES_LOSERS = "/api/v1/quotes/losers/"
    QUOTES_MOST_ACTIVE = "/api/v1/quotes/most-active/"
    QUOTES_LAST_TRADE = "/api/v1/quotes/{symbol}/last-trade/"
    QUOTES_LAST_QUOTE = "/api/v1/quotes/{symbol}/last-quote/"
    QUOTES_PREVIOUS_CLOSE = "/api/v1/quotes/{symbol}/previous-close/"

    # Historical
    HISTORICAL = "/api/v1/historical/{symbol}/"
    HISTORICAL_INTRADAY = "/api/v1/historical/{symbol}/intraday/"
    HISTORICAL_DIVIDENDS = "/api/v1/historical/{symbol}/dividends/"
    HISTORICAL_SPLITS = "/api/v1/historical/{symbol}/splits/"
    HISTORICAL_GROUPED = "/api/v1/historical/grouped/{date}/"

    # Options (Polygon)
    OPTIONS_CONTRACTS = "/api/v1/options/contracts/"
    OPTIONS_CHAIN = "/api/v1/options/chain/{symbol}/"
    OPTIONS_GREEKS = "/api/v1/options/{symbol}/greeks/"
    OPTIONS_OPEN_INTEREST = "/api/v1/options/{symbol}/open-interest/"
    OPTIONS_CONTRACT_HIST = "/api/v1/options/{contract}/historical/"

    # Futures (Polygon)
    FUTURES_CONTRACTS = "/api/v1/futures/contracts/"
    FUTURES_SNAPSHOT = "/api/v1/futures/{symbol}/snapshot/"
    FUTURES_HISTORICAL = "/api/v1/futures/{symbol}/historical/"

    # Ticks (Polygon)
    TICKS_TRADES = "/api/v1/ticks/{symbol}/trades/"
    TICKS_QUOTES = "/api/v1/ticks/{symbol}/quotes/"
    TICKS_AGGREGATES = "/api/v1/ticks/{symbol}/aggregates/"

    # Fundamentals (FMP)
    FUND_IS = "/api/v1/fundamentals/{symbol}/income-statement/"
    FUND_BS = "/api/v1/fundamentals/{symbol}/balance-sheet/"
    FUND_CF = "/api/v1/fundamentals/{symbol}/cash-flow/"
    FUND_RATIOS = "/api/v1/fundamentals/{symbol}/ratios/"
    FUND_DCF = "/api/v1/fundamentals/{symbol}/dcf/"
    FUND_METRICS = "/api/v1/fundamentals/{symbol}/metrics/"
    FUND_EV = "/api/v1/fundamentals/{symbol}/enterprise-value/"
    FUND_SCREENER = "/api/v1/fundamentals/screener/"

    # News (FMP)
    NEWS = "/api/v1/news/"
    NEWS_SYMBOL = "/api/v1/news/{symbol}/"
    NEWS_PR = "/api/v1/news/press-releases/"
    NEWS_SYMBOL_PR = "/api/v1/news/{symbol}/press-releases/"
    NEWS_SENTIMENT = "/api/v1/news/sentiment/"

    # Analysts (FMP)
    ANALYST_EST = "/api/v1/analysts/{symbol}/estimates/"
    ANALYST_RECO = "/api/v1/analysts/{symbol}/recommendations/"
    ANALYST_PRICE_TARGETS = "/api/v1/analysts/{symbol}/price-targets/"
    ANALYST_UPGRADES = "/api/v1/analysts/{symbol}/upgrades-downgrades/"

    # Earnings (FMP)
    EARNINGS_CAL = "/api/v1/earnings/{symbol}/calendar/"
    EARNINGS_TRANSCRIPTS = "/api/v1/earnings/{symbol}/transcripts/"
    EARNINGS_HISTORY = "/api/v1/earnings/{symbol}/history/"
    EARNINGS_SURPRISES = "/api/v1/earnings/{symbol}/surprises/"

    # Corporate events (FMP)
    EVENTS_IPO = "/api/v1/events/ipo-calendar/"
    EVENTS_SPLIT = "/api/v1/events/stock-split-calendar/"
    EVENTS_DIVIDEND = "/api/v1/events/dividend-calendar/"

    # Institutional (FMP)
    INST_13F = "/api/v1/institutional/{symbol}/13f/"
    INST_HOLDERS = "/api/v1/institutional/{symbol}/holders/"
    INST_INSIDER = "/api/v1/institutional/{symbol}/insider-trading/"

    # Economic (FMP)
    ECO_GDP = "/api/v1/economy/gdp/"
    ECO_CPI = "/api/v1/economy/inflation/"
    ECO_UNEMP = "/api/v1/economy/unemployment/"
    ECO_RATES = "/api/v1/economy/interest-rates/"
    ECO_TREASURY = "/api/v1/economy/treasury-rates/"

    # ETF & Mutual funds (FMP)
    ETF_LIST = "/api/v1/etf/list/"
    ETF_HOLDINGS = "/api/v1/etf/{symbol}/holdings/"
    ETF_PERF = "/api/v1/etf/{symbol}/performance/"
    MF_LIST = "/api/v1/mutual-funds/list/"

    # Commodities (FMP)
    COM_METALS = "/api/v1/commodities/metals/"
    COM_ENERGY = "/api/v1/commodities/energy/"
    COM_AGRI = "/api/v1/commodities/agricultural/"
    COM_HIST = "/api/v1/commodities/{symbol}/historical/"

    # Crypto (FMP)
    CRYPTO_LIST = "/api/v1/crypto/list/"
    CRYPTO_QUOTE = "/api/v1/crypto/{symbol}/"
    CRYPTO_HIST = "/api/v1/crypto/{symbol}/historical/"

    # International (FMP)
    INT_EXCHANGES = "/api/v1/international/exchanges/"
    INT_STOCKS = "/api/v1/international/{exchange}/stocks/"
    FOREX_RATES = "/api/v1/forex/rates/"
    FOREX_PAIR = "/api/v1/forex/{pair}/"

    # SEC (FMP)
    SEC_FILINGS = "/api/v1/sec/{symbol}/filings/"
    SEC_10K = "/api/v1/sec/{symbol}/10k/"
    SEC_10Q = "/api/v1/sec/{symbol}/10q/"
    SEC_8K = "/api/v1/sec/{symbol}/8k/"
    SEC_RSS = "/api/v1/sec/rss-feed/"

    # Examples
    EXAMPLE_FMP_GAINERS = "/api/v1/examples/fmp/gainers/"
    EXAMPLE_POLYGON_TRADES = "/api/v1/examples/polygon/{symbol}/trades/"


class EndpointToFMP(Enum):
    # Reference
    REFERENCE_TICKERS = "/v3/stock/list"
    REFERENCE_TICKER = "/v3/profile/{symbol}"
    REFERENCE_TICKER_PROFILE = "/v3/profile/{symbol}"
    REFERENCE_TICKER_EXECUTIVES = "/v3/key-executives/{symbol}"
    REFERENCE_TICKER_OUTLOOK = "/v4/company-outlook"
    REFERENCE_EXCHANGES = "/v3/exchanges-list"
    REFERENCE_MARKET_CAP = "/v3/market-capitalization/{symbol}"

    # Market Data
    QUOTES_SINGLE = "/v3/quote/{symbol}"
    QUOTES_BATCH = "/v3/quote/{symbols}"
    QUOTES_GAINERS = "/v3/gainers"
    QUOTES_LOSERS = "/v3/losers"
    QUOTES_MOST_ACTIVE = "/v3/actives"

    # Historical
    HISTORICAL = "/v3/historical-price-full/{symbol}"
    HISTORICAL_INTRADAY = "/v3/historical-chart/{interval}/{symbol}"
    HISTORICAL_DIVIDENDS = "/v3/historical-price-full/stock_dividend/{symbol}"
    HISTORICAL_SPLITS = "/v3/historical-price-full/stock_split/{symbol}"

    # Fundamentals
    FUND_IS = "/v3/income-statement/{symbol}"
    FUND_BS = "/v3/balance-sheet-statement/{symbol}"
    FUND_CF = "/v3/cash-flow-statement/{symbol}"
    FUND_RATIOS = "/v3/ratios/{symbol}"
    FUND_DCF = "/v3/discounted-cash-flow/{symbol}"
    FUND_METRICS = "/v3/key-metrics/{symbol}"
    FUND_EV = "/v3/enterprise-values/{symbol}"
    FUND_SCREENER = "/v3/stock-screener"

    # News
    NEWS = "/v3/stock_news"
    NEWS_SYMBOL = "/v3/stock_news"
    NEWS_PR = "/v3/press-releases"
    NEWS_SYMBOL_PR = "/v3/press-releases/{symbol}"
    NEWS_SENTIMENT = "/v4/historical/social-sentiment"

    # Analysts
    ANALYST_EST = "/v3/analyst-estimates/{symbol}"
    ANALYST_RECO = "/v3/analyst-stock-recommendations/{symbol}"
    ANALYST_PRICE_TARGETS = "/v4/price-target"
    ANALYST_UPGRADES = "/v4/upgrades-downgrades"

    # Earnings
    EARNINGS_CAL = "/v3/earning_calendar"
    EARNINGS_TRANSCRIPTS = "/v4/batch_earning_call_transcript/{symbol}"
    EARNINGS_HISTORY = "/v3/historical/earning_calendar/{symbol}"
    EARNINGS_SURPRISES = "/v3/earnings-surprises/{symbol}"

    # Corporate events
    EVENTS_IPO = "/v3/ipo_calendar"
    EVENTS_SPLIT = "/v3/stock_split_calendar"
    EVENTS_DIVIDEND = "/v3/stock_dividend_calendar"

    # Institutional
    INST_13F = "/v3/form-thirteen/{symbol}"
    INST_HOLDERS = "/v3/institutional-holder/{symbol}"
    INST_INSIDER = "/v4/insider-trading"

    # Economic
    ECO_GDP = "/v4/economic"
    ECO_CPI = "/v4/economic"
    ECO_UNEMP = "/v4/economic"
    ECO_RATES = "/v4/economic"
    ECO_TREASURY = "/v4/treasury"

    # ETF & Mutual funds
    ETF_LIST = "/v3/etf/list"
    ETF_HOLDINGS = "/v3/etf-holder/{symbol}"
    ETF_PERF = "/v4/etf-info"
    MF_LIST = "/v3/mutual-fund/list"

    # Commodities
    COM_QUOTES = "/v3/quotes/commodity"
    COM_HIST = "/v3/historical-price-full/{symbol}"

    # Crypto
    CRYPTO_LIST = "/v3/quotes/crypto"
    CRYPTO_QUOTE = "/v3/quote/{symbol}"
    CRYPTO_HIST = "/v3/historical-price-full/{symbol}"

    # International
    INT_EXCHANGES = "/v3/exchanges-list"
    INT_STOCKS = "/v3/available-traded/list"
    FOREX_RATES = "/v3/fx"
    FOREX_PAIR = "/v3/historical-price-full/{pair}"

    # SEC
    SEC_FILINGS = "/v3/sec_filings/{symbol}"
    SEC_10K = "/v3/sec_filings/{symbol}"
    SEC_10Q = "/v3/sec_filings/{symbol}"
    SEC_8K = "/v3/sec_filings/{symbol}"
    SEC_RSS = "/v4/rss_feed"


class EndpointToPolygon(Enum):
    # Reference
    REFERENCE_MARKET_STATUS = "/v1/marketstatus/now"
    REFERENCE_MARKET_HOLIDAYS = "/v1/marketstatus/upcoming"

    # Market Data
    QUOTES_LAST_TRADE = "/v2/last/trade/{symbol}"
    QUOTES_LAST_QUOTE = "/v2/last/nbbo/{symbol}"
    QUOTES_PREVIOUS_CLOSE = "/v2/aggs/ticker/{symbol}/prev"

    # Historical aggregated/grouped
    HISTORICAL_GROUPED = "/v2/aggs/grouped/locale/us/market/stocks/{date}"

    # Options
    OPTIONS_CONTRACTS = "/v3/reference/options/contracts"
    OPTIONS_CHAIN = "/v3/snapshot/options/{symbol}"
    OPTIONS_GREEKS = "/v3/snapshot/options/{symbol}"
    OPTIONS_OPEN_INTEREST = "/v3/snapshot/options/{symbol}"
    OPTIONS_CONTRACT_HIST = "/v2/aggs/ticker/{contract}/range/{multiplier}/{timespan}/{from}/{to}"

    # Futures
    FUTURES_CONTRACTS = "/v3/reference/futures/contracts"
    FUTURES_SNAPSHOT = "/v2/snapshot/locale/global/markets/futures/tickers/{symbol}"
    FUTURES_HISTORICAL = "/v2/aggs/ticker/{symbol}/range/{multiplier}/{timespan}/{from}/{to}"

    # Ticks
    TICKS_TRADES = "/v3/trades/{symbol}"
    TICKS_QUOTES = "/v3/quotes/{symbol}"
    TICKS_AGGREGATES = "/v2/aggs/ticker/{symbol}/range/{multiplier}/{timespan}/{from}/{to}"


class CommonParams(Enum):
    LIMIT = "limit"
    PAGE = "page"
    FROM = "from"
    TO = "to"
    SYMBOL = "symbol"
    SYMBOLS = "symbols"
    EXCHANGE = "exchange"
    SECTOR = "sector"
    MARKET = "market"
    INDUSTRY = "industry"
    TICKER = "ticker"
    INTERVAL = "interval"
    MULTIPLIER = "multiplier"
    TIMESPAN = "timespan"


class NewsParams(Enum):
    TICKERS = "tickers"


class EconomicParams(Enum):
    NAME = "name"


class EndpointTo:
    FMP = EndpointToFMP
    Polygon = EndpointToPolygon

