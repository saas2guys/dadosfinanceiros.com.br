from __future__ import annotations

from enum import Enum


class EndpointFrom(Enum):
    # Examples (keep)
    EXAMPLE_POLYGON_TRADES = "/api/v1/examples/polygon/{symbol}/trades/"

    # Polygon stock API endpoints (app routes)
    STOCKS_AGG_CUSTOM_RANGE = "/api/v1/stocks/aggs/{stocksTicker}/range/{multiplier}/{timespan}/{from}/{to}/"
    STOCKS_AGG_GROUPED_DAILY = "/api/v1/stocks/aggs/grouped/{date}/"
    STOCKS_AGG_PREVIOUS_DAY = "/api/v1/stocks/aggs/{stocksTicker}/prev/"
    STOCKS_INDICATOR_EMA = "/api/v1/stocks/indicators/ema/{stockTicker}/"
    STOCKS_INDICATOR_MACD = "/api/v1/stocks/indicators/macd/{stockTicker}/"
    STOCKS_INDICATOR_RSI = "/api/v1/stocks/indicators/rsi/{stockTicker}/"
    STOCKS_INDICATOR_SMA = "/api/v1/stocks/indicators/sma/{stockTicker}/"
    STOCKS_LAST_NBBO = "/api/v1/stocks/last-quote/{stocksTicker}/"
    STOCKS_LAST_TRADE = "/api/v1/stocks/last-trade/{stocksTicker}/"
    STOCKS_OPEN_CLOSE = "/api/v1/stocks/open-close/{stocksTicker}/{date}/"
    STOCKS_QUOTES = "/api/v1/stocks/quotes/{stockTicker}/"
    STOCKS_REFERENCE_CONDITIONS = "/api/v1/stocks/reference/conditions/"
    STOCKS_REFERENCE_DIVIDENDS = "/api/v1/stocks/reference/dividends/"
    STOCKS_REFERENCE_EXCHANGES = "/api/v1/stocks/reference/exchanges/"
    STOCKS_REFERENCE_FINANCIALS = "/api/v1/stocks/reference/financials/"
    STOCKS_REFERENCE_IPOS = "/api/v1/stocks/reference/ipos/"
    STOCKS_REFERENCE_MARKET_HOLIDAYS = "/api/v1/stocks/reference/market-holidays/"
    STOCKS_REFERENCE_MARKET_STATUS = "/api/v1/stocks/reference/market-status/"
    STOCKS_REFERENCE_NEWS = "/api/v1/stocks/reference/news/"
    STOCKS_REFERENCE_SPLITS = "/api/v1/stocks/reference/splits/"
    STOCKS_REFERENCE_TICKER = "/api/v1/stocks/reference/tickers/{ticker}/"
    STOCKS_REFERENCE_TICKER_EVENTS = "/api/v1/stocks/reference/tickers/{id}/events/"
    STOCKS_REFERENCE_TICKER_TYPES = "/api/v1/stocks/reference/tickers/types/"
    STOCKS_REFERENCE_TICKERS = "/api/v1/stocks/reference/tickers/"
    STOCKS_RELATED_COMPANIES = "/api/v1/stocks/related-companies/{ticker}/"
    STOCKS_SNAPSHOT_MARKET = "/api/v1/stocks/snapshot/tickers/"
    STOCKS_SNAPSHOT_MOVERS = "/api/v1/stocks/snapshot/movers/{direction}/"
    STOCKS_SNAPSHOT_TICKER = "/api/v1/stocks/snapshot/tickers/{stocksTicker}/"
    STOCKS_SNAPSHOT_UNIFIED = "/api/v1/snapshot/"
    STOCKS_SHORT_INTEREST = "/api/v1/stocks/short-interest/"
    STOCKS_SHORT_VOLUME = "/api/v1/stocks/short-volume/"
    STOCKS_TRADES = "/api/v1/stocks/trades/{stockTicker}/"


class EndpointFromFMP(Enum):
    pass


class EndpointToFMP(Enum):
    pass


class EndpointToPolygon(Enum):
    AGG_CUSTOM_RANGE = "/v2/aggs/ticker/{stocksTicker}/range/{multiplier}/{timespan}/{from}/{to}"
    AGG_GROUPED_DAILY = "/v2/aggs/grouped/locale/us/market/stocks/{date}"
    AGG_PREVIOUS_DAY = "/v2/aggs/ticker/{stocksTicker}/prev"
    INDICATOR_EMA = "/v1/indicators/ema/{stockTicker}"
    INDICATOR_MACD = "/v1/indicators/macd/{stockTicker}"
    INDICATOR_RSI = "/v1/indicators/rsi/{stockTicker}"
    INDICATOR_SMA = "/v1/indicators/sma/{stockTicker}"
    LAST_NBBO = "/v2/last/nbbo/stocks/{stocksTicker}"
    LAST_TRADE = "/v2/last/trade/stocks/{stocksTicker}"
    OPEN_CLOSE = "/v1/open-close/{stocksTicker}/{date}"
    QUOTES = "/v3/quotes/{stockTicker}"
    REFERENCE_CONDITIONS = "/v3/reference/conditions"
    REFERENCE_DIVIDENDS = "/v3/reference/dividends"
    REFERENCE_EXCHANGES = "/v3/reference/exchanges"
    REFERENCE_FINANCIALS = "/vX/reference/financials"
    REFERENCE_IPOS = "/v3/reference/ipos"
    REFERENCE_NEWS = "/v2/reference/news"
    REFERENCE_SPLITS = "/v3/reference/splits"
    REFERENCE_TICKER = "/v3/reference/tickers/{ticker}"
    REFERENCE_TICKER_EVENTS = "/vX/reference/tickers/{id}/events"
    REFERENCE_TICKER_TYPES = "/v3/reference/tickers/types"
    REFERENCE_TICKERS = "/v3/reference/tickers"
    REFERENCE_MARKET_HOLIDAYS = "/v1/marketstatus/upcoming"
    REFERENCE_MARKET_STATUS = "/v1/marketstatus/now"
    RELATED_COMPANIES = "/v1/related-companies/{ticker}"
    SNAPSHOT_MARKET = "/v2/snapshot/locale/us/markets/stocks/tickers"
    SNAPSHOT_MOVERS = "/v2/snapshot/locale/us/markets/stocks/{direction}"
    SNAPSHOT_TICKER = "/v2/snapshot/locale/us/markets/stocks/tickers/{stocksTicker}"
    SNAPSHOT_UNIFIED = "/v3/snapshot"
    STOCKS_SHORT_INTEREST = "/stocks/v1/short-interest"
    STOCKS_SHORT_VOLUME = "/stocks/v1/short-volume"
    TRADES = "/v3/trades/{stockTicker}"


class EndpointFromPolygon(Enum):
    pass


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


# Polygon endpoint-specific allowed query parameter groups
class PolygonParams:
    # Shared/common params across many Polygon endpoints
    class Common(Enum):
        limit = "limit"
        order = "order"
        sort = "sort"
    class ReferenceTickers(Enum):
        active = "active"
        cik = "cik"
        cusip = "cusip"
        date = "date"
        exchange = "exchange"
        market = "market"
        search = "search"
        ticker = "ticker"
        type = "type"

    class ReferenceTicker(Enum):
        date = "date"

    class ReferenceTickerTypes(Enum):
        asset_class = "asset_class"
        locale = "locale"

    class AggCustomRange(Enum):
        adjusted = "adjusted"

    class AggGroupedDaily(Enum):
        adjusted = "adjusted"
        include_otc = "include_otc"

    class OpenClose(Enum):
        adjusted = "adjusted"

    class SnapshotMarket(Enum):
        include_otc = "include_otc"
        tickers = "tickers"

    class SnapshotUnified(Enum):
        ticker = "ticker"
        type = "type"

    class SnapshotMovers(Enum):
        include_otc = "include_otc"

    class Trades(Enum):
        timestamp = "timestamp"

    class Quotes(Enum):
        timestamp = "timestamp"

    class IndicatorCommon(Enum):
        expand_underlying = "expand_underlying"
        series_type = "series_type"
        timestamp = "timestamp"
        window = "window"

    class IndicatorMACD(Enum):
        expand_underlying = "expand_underlying"
        long_window = "long_window"
        series_type = "series_type"
        short_window = "short_window"
        signal_window = "signal_window"
        timestamp = "timestamp"

    class ReferenceExchanges(Enum):
        asset_class = "asset_class"
        locale = "locale"

    class ReferenceConditions(Enum):
        asset_class = "asset_class"
        data_type = "data_type"
        id = "id"
        sip = "sip"

    class ReferenceIPOs(Enum):
        isin = "isin"
        ticker = "ticker"
        us_code = "us_code"
        listing_date = "listing_date"

    class ReferenceSplits(Enum):
        execution_date = "execution_date"
        reverse_split = "reverse_split"
        ticker = "ticker"

    class ReferenceDividends(Enum):
        cash_amount = "cash_amount"
        declaration_date = "declaration_date"
        dividend_type = "dividend_type"
        ex_dividend_date = "ex_dividend_date"
        frequency = "frequency"
        pay_date = "pay_date"
        record_date = "record_date"
        ticker = "ticker"

    class ReferenceTickerEvents(Enum):
        types = "types"

    class ReferenceFinancials(Enum):
        cik = "cik"
        company_name = "company_name"
        filing_date = "filing_date"
        include_sources = "include_sources"
        period_of_report_date = "period_of_report_date"
        sic = "sic"
        ticker = "ticker"
        timeframe = "timeframe"

    class StocksShortInterest(Enum):
        avg_daily_volume = "avg_daily_volume"
        days_to_cover = "days_to_cover"
        settlement_date = "settlement_date"
        ticker = "ticker"

    class StocksShortVolume(Enum):
        date = "date"
        short_volume_ratio = "short_volume_ratio"
        ticker = "ticker"
        total_volume = "total_volume"

    class ReferenceNews(Enum):
        published_utc = "published_utc"
        ticker = "ticker"


class EndpointTo:
    Polygon = EndpointToPolygon

