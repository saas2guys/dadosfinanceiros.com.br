from __future__ import annotations

from enum import Enum


class EndpointFrom(Enum):
    # Examples (keep)
    EXAMPLE_POLYGON_TRADES = "/api/v1/examples/polygon/{symbol}/trades/"
    EXAMPLE_FMP_GAINERS = "/api/v1/examples/fmp/gainers/"

    # Polygon stock API endpoints (app routes)
    STOCKS_AGGREGATE_CUSTOM_RANGE = "/api/v1/stocks/aggs/{stocksTicker}/range/{multiplier}/{timespan}/{from}/{to}/"
    STOCKS_AGGREGATE_GROUPED_DAILY = "/api/v1/stocks/aggs/grouped/{date}/"
    STOCKS_AGGREGATE_PREVIOUS_DAY = "/api/v1/stocks/aggs/{stocksTicker}/prev/"
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


    # FMP app endpoints
    ANALYST_ESTIMATES = "/api/v1/analysts/{symbol}/estimates/"
    ANALYST_PRICE_TARGETS = "/api/v1/analysts/{symbol}/price-targets/"
    ANALYST_RECOMMENDATIONS = "/api/v1/analysts/{symbol}/recommendations/"
    ANALYST_UPGRADES_DOWNGRADES = "/api/v1/analysts/{symbol}/upgrades-downgrades/"
    COMMODITIES_AGRICULTURAL = "/api/v1/commodities/agricultural/"
    COMMODITIES_ENERGY = "/api/v1/commodities/energy/"
    COMMODITIES_HISTORICAL = "/api/v1/commodities/{symbol}/historical/"
    COMMODITIES_METALS = "/api/v1/commodities/metals/"
    COMPANY_EXECUTIVES = "/api/v1/reference/ticker/{symbol}/company-executives/"
    COMPANY_SCREENER_STABLE = "/api/v1/fundamentals/screener/stable/"
    CRYPTO_HISTORICAL = "/api/v1/crypto/{symbol}/historical/"
    CRYPTO_LIST = "/api/v1/crypto/list/"
    CRYPTO_QUOTE = "/api/v1/crypto/{symbol}/"
    ECONOMY_INFLATION = "/api/v1/economy/inflation/"
    ECONOMY_GDP = "/api/v1/economy/gdp/"
    ECONOMY_TREASURY_RATES = "/api/v1/economy/treasury-rates/"
    ECONOMY_UNEMPLOYMENT = "/api/v1/economy/unemployment/"
    EARNINGS_CALENDAR = "/api/v1/earnings/{symbol}/calendar/"
    EARNINGS_HISTORY = "/api/v1/earnings/{symbol}/history/"
    EARNINGS_SURPRISES = "/api/v1/earnings/{symbol}/surprises/"
    EARNINGS_TRANSCRIPTS = "/api/v1/earnings/{symbol}/transcripts/"
    EMPLOYEE_COUNT = "/api/v1/reference/ticker/{symbol}/employee-count/"
    EMPLOYEE_COUNT_HISTORICAL = "/api/v1/reference/ticker/{symbol}/employee-count/historical/"
    # ENTERPRISE_VALUES = "/api/v1/fundamentals/{symbol}/enterprise-value/"  # INTERNAL DUPLICATE: Use FUNDAMENTALS_ENTERPRISE_VALUE
    EVENTS_DIVIDEND = "/api/v1/events/dividend-calendar/"
    # EVENTS_IPO = "/api/v1/events/ipo-calendar/"  # DUPLICATE: Use STOCKS_REFERENCE_IPOS from Polygon
    ETF_HOLDINGS = "/api/v1/etf/{symbol}/holdings/"
    ETF_LIST = "/api/v1/etf/list/"
    ETF_PERFORMANCE = "/api/v1/etf/{symbol}/performance/"
    EXEC_COMP = "/api/v1/corporate/executive-compensation/"
    EXEC_COMP_BENCHMARK = "/api/v1/corporate/executive-compensation/benchmark/"
    EXCHANGE_VARIANTS = "/api/v1/reference/exchange-variants/"
    FOREX_PAIR = "/api/v1/forex/{pair}/"
    FOREX_RATES = "/api/v1/forex/rates/"
    FUNDAMENTALS_BALANCE_SHEET = "/api/v1/fundamentals/{symbol}/balance-sheet/"
    FUNDAMENTALS_CASH_FLOW = "/api/v1/fundamentals/{symbol}/cash-flow/"
    FUNDAMENTALS_DCF = "/api/v1/fundamentals/{symbol}/dcf/"
    FUNDAMENTALS_ENTERPRISE_VALUE = "/api/v1/fundamentals/{symbol}/enterprise-value/"
    FUNDAMENTALS_INCOME_STATEMENT = "/api/v1/fundamentals/{symbol}/income-statement/"
    FUNDAMENTALS_METRICS = "/api/v1/fundamentals/{symbol}/metrics/"
    FUNDAMENTALS_SCREENER = "/api/v1/fundamentals/screener/"
    # HISTORICAL = "/api/v1/historical/{symbol}/"  # SIMILAR: Use STOCKS_AGGREGATE_CUSTOM_RANGE from Polygon
    # HISTORICAL_DIVIDENDS = "/api/v1/historical/{symbol}/dividends/"  # DUPLICATE: Use STOCKS_REFERENCE_DIVIDENDS from Polygon
    HISTORICAL_INTRADAY = "/api/v1/historical/{symbol}/intraday/"
    # HISTORICAL_SPLITS = "/api/v1/historical/{symbol}/splits/"  # DUPLICATE: Use STOCKS_REFERENCE_SPLITS from Polygon
    INSTITUTIONAL_13F = "/api/v1/institutional/{symbol}/13f/"
    INSTITUTIONAL_HOLDERS = "/api/v1/institutional/{symbol}/holders/"
    INSTITUTIONAL_INSIDER_TRADING = "/api/v1/institutional/{symbol}/insider-trading/"
    INTERNATIONAL_EXCHANGES = "/api/v1/international/exchanges/"
    INTERNATIONAL_STOCKS = "/api/v1/international/{exchange}/stocks/"
    MERGERS_ACQUISITIONS = "/api/v1/corporate/mergers-acquisitions/"
    MERGERS_ACQUISITIONS_SEARCH = "/api/v1/corporate/mergers-acquisitions/search/"
    # NEWS = "/api/v1/news/"  # DUPLICATE: Use STOCKS_REFERENCE_NEWS from Polygon
    NEWS_PRESS_RELEASES = "/api/v1/news/press-releases/"
    NEWS_SENTIMENT = "/api/v1/news/sentiment/"
    NEWS_SYMBOL = "/api/v1/news/{symbol}/"
    NEWS_SYMBOL_PRESS_RELEASES = "/api/v1/news/{symbol}/press-releases/"
    QUOTES_BATCH = "/api/v1/quotes/batch/"
    # QUOTES_LOSERS = "/api/v1/quotes/losers/"  # SIMILAR: Use STOCKS_SNAPSHOT_MOVERS from Polygon
    # QUOTES_MOST_ACTIVE = "/api/v1/quotes/most-active/"  # SIMILAR: Use STOCKS_SNAPSHOT_MOVERS from Polygon
    # QUOTES_SINGLE = "/api/v1/quotes/{symbol}/"  # SIMILAR: Use STOCKS_QUOTES from Polygon
    # REFERENCE_EXCHANGES = "/api/v1/reference/exchanges/"  # DUPLICATE: Use STOCKS_REFERENCE_EXCHANGES from Polygon
    REFERENCE_MARKET_CAP = "/api/v1/reference/market-cap/{symbol}/"
    # REFERENCE_TICKER = "/api/v1/reference/ticker/{symbol}/"  # SIMILAR: Use STOCKS_REFERENCE_TICKER from Polygon
    # REFERENCE_TICKER_EXECUTIVES = "/api/v1/reference/ticker/{symbol}/executives/"  # INTERNAL DUPLICATE: Use COMPANY_EXECUTIVES
    REFERENCE_TICKER_OUTLOOK = "/api/v1/reference/ticker/{symbol}/outlook/"
    # REFERENCE_TICKER_PROFILE = "/api/v1/reference/ticker/{symbol}/profile/"  # INTERNAL DUPLICATE: Use REFERENCE_TICKER
    REFERENCE_TICKERS = "/api/v1/reference/tickers/"
    SEARCH_CIK = "/api/v1/reference/search/cik/"
    SEARCH_CUSIP = "/api/v1/reference/search/cusip/"
    SEARCH_ISIN = "/api/v1/reference/search/isin/"
    SEC_10K = "/api/v1/sec/{symbol}/10k/"
    SEC_10Q = "/api/v1/sec/{symbol}/10q/"
    SEC_8K = "/api/v1/sec/{symbol}/8k/"
    SEC_FILINGS = "/api/v1/sec/{symbol}/filings/"
    SEC_RSS = "/api/v1/sec/rss-feed/"
    SHARES_FLOAT = "/api/v1/reference/ticker/{symbol}/shares-float/"
    SHARES_FLOAT_ALL = "/api/v1/reference/shares-float/all/"
    SYMBOL_CHANGE = "/api/v1/reference/symbol-change/"


class EndpointToFMP(Enum):
    COMPANY_EXECUTIVES = "/v3/company-executive/{symbol}"
    COMPANY_SCREENER_STABLE = "/stable/company-screener"
    EMPLOYEE_COUNT = "/v4/employee_count"
    EMPLOYEE_COUNT_HISTORICAL = "/v4/employee_count_historical"
    EXEC_COMP = "/v4/executive-compensation"
    EXEC_COMP_BENCHMARK = "/v4/executive-compensation-benchmark"
    EXCHANGE_VARIANTS = "/stable/search-exchange-variants"
    MERGERS_ACQUISITIONS = "/v4/mergers-acquisitions"
    MERGERS_ACQUISITIONS_SEARCH = "/v4/mergers-acquisitions-search"
    SEARCH_CIK = "/stable/search-cik"
    SEARCH_CUSIP = "/stable/search-cusip"
    SEARCH_ISIN = "/stable/search-isin"
    SHARES_FLOAT = "/v4/shares_float"
    SHARES_FLOAT_ALL = "/v4/shares_float_all"
    SYMBOL_CHANGE = "/stable/symbol-change"


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
    """
    Polygon endpoint parameter groups.

    Common: Pagination and sorting controls.
    AggregateCustomRange: Toggle adjusted values.
    AggregateGroupedDaily: Adjusted toggle and include OTC market.
    OpenClose: Adjusted values toggle for open/close endpoint.
    SnapshotMarket: Market snapshot filters such as OTC and tickers list.
    SnapshotUnified: Multi-asset snapshot filters.
    SnapshotMovers: Movers list modifiers.
    Trades: Trade stream filters.
    Quotes: Quote stream filters.
    IndicatorCommon: Shared indicator options like window and series type.
    IndicatorMACD: MACD-specific window sizes and options.
    ReferenceExchanges: Filter stock exchanges by asset class and locale.
    ReferenceConditions: Filter condition metadata by type and SIP.
    ReferenceIPOs: IPO filters like ISIN and listing date.
    ReferenceSplits: Split filters by execution date and ticker.
    ReferenceDividends: Dividend filters (dates, amount, frequency, ticker).
    ReferenceTickerEvents: Corporate event types filter.
    ReferenceFinancials: Filters for standardized financials.
    StocksShortInterest: Filters for short interest metrics.
    StocksShortVolume: Filters for FINRA short volume.
    ReferenceNews: Filters for news publishing time and ticker.
    ReferenceTickers/ReferenceTicker/ReferenceTickerTypes: Ticker catalog filters.
    """
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

    class AggregateCustomRange(Enum):
        adjusted = "adjusted"

    class AggregateGroupedDaily(Enum):
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


class FMPParams:
    """
    Financial Modeling Prep endpoint parameter groups.

    AnalystPriceTargets: Paging for analyst price target feed.
    AnalystUpgrades: Date range and paging for upgrades/downgrades feed.
    CompanyScreenerStable: Filters to discover companies by fundamentals and trading flags.
    EarningsCalendar: Date range to filter earnings calendar items.
    HistoricalIntraday: Date range for intraday bars.
    HistoricalRange: Controls for historical EOD series window and format.
    ExecutiveCompensation/Benchmark: Company symbol and year selectors.
    ExchangeVariants: Base symbol to find variants across exchanges.
    MergersAcquisitions/Search: Paging and query for M&A datasets.
    SearchCIK/CUSIP/ISIN: Identifier-based searches for companies/securities.
    """
    class AnalystPriceTargets(Enum):
        page = "page"

    class AnalystUpgrades(Enum):
        from_ = "from"
        page = "page"
        to = "to"

    class CompanyScreenerStable(Enum):
        betaLowerThan = "betaLowerThan"
        betaMoreThan = "betaMoreThan"
        country = "country"
        dividendLowerThan = "dividendLowerThan"
        dividendMoreThan = "dividendMoreThan"
        exchange = "exchange"
        includeAllShareClasses = "includeAllShareClasses"
        industry = "industry"
        isActivelyTrading = "isActivelyTrading"
        isEtf = "isEtf"
        isFund = "isFund"
        limit = "limit"
        marketCapLowerThan = "marketCapLowerThan"
        marketCapMoreThan = "marketCapMoreThan"
        priceLowerThan = "priceLowerThan"
        priceMoreThan = "priceMoreThan"
        sector = "sector"
        volumeLowerThan = "volumeLowerThan"
        volumeMoreThan = "volumeMoreThan"

    class EarningsCalendar(Enum):
        from_ = "from"
        to = "to"

    class HistoricalIntraday(Enum):
        from_ = "from"
        to = "to"

    class HistoricalRange(Enum):
        from_ = "from"
        serietype = "serietype"
        timeseries = "timeseries"
        to = "to"

    class ExecutiveCompensation(Enum):
        symbol = "symbol"
        year = "year"

    class ExecutiveCompensationBenchmark(Enum):
        symbol = "symbol"
        year = "year"

    class ExchangeVariants(Enum):
        symbol = "symbol"

    class MergersAcquisitions(Enum):
        page = "page"

    class MergersAcquisitionsSearch(Enum):
        page = "page"
        query = "query"

    class SearchCIK(Enum):
        cik = "cik"

    class SearchCUSIP(Enum):
        cusip = "cusip"

    class SearchISIN(Enum):
        isin = "isin"

class EndpointTo:
    FMP = EndpointToFMP
    Polygon = EndpointToPolygon

