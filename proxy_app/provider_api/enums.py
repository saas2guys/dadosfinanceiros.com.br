from __future__ import annotations

from enum import Enum


class EndpointFrom(Enum):
    # Examples (keep)
    EXAMPLE_POLYGON_TRADES = "/examples/polygon/{symbol}/trades/"
    EXAMPLE_FMP_GAINERS = "/examples/fmp/gainers/"

    # Polygon stock API endpoints (app routes)
    STOCKS_AGGREGATE_CUSTOM_RANGE = "/stocks/aggs/{stocksTicker}/range/{multiplier}/{timespan}/{from}/{to}/"
    STOCKS_AGGREGATE_GROUPED_DAILY = "/stocks/aggs/grouped/{date}/"
    STOCKS_AGGREGATE_PREVIOUS_DAY = "/stocks/aggs/{stocksTicker}/prev/"
    STOCKS_INDICATOR_EMA = "/stocks/indicators/ema/{stockTicker}/"
    STOCKS_INDICATOR_MACD = "/stocks/indicators/macd/{stockTicker}/"
    STOCKS_INDICATOR_RSI = "/stocks/indicators/rsi/{stockTicker}/"
    STOCKS_INDICATOR_SMA = "/stocks/indicators/sma/{stockTicker}/"
    STOCKS_LAST_NBBO = "/stocks/last-quote/{stocksTicker}/"
    STOCKS_LAST_TRADE = "/stocks/last-trade/{stocksTicker}/"
    STOCKS_OPEN_CLOSE = "/stocks/open-close/{stocksTicker}/{date}/"
    STOCKS_QUOTES = "/stocks/quotes/{stockTicker}/"
    STOCKS_REFERENCE_CONDITIONS = "/stocks/reference/conditions/"
    STOCKS_REFERENCE_DIVIDENDS = "/stocks/reference/dividends/"
    STOCKS_REFERENCE_EXCHANGES = "/stocks/reference/exchanges/"
    STOCKS_REFERENCE_FINANCIALS = "/stocks/reference/financials/"
    STOCKS_REFERENCE_IPOS = "/stocks/reference/ipos/"
    STOCKS_REFERENCE_MARKET_HOLIDAYS = "/stocks/reference/market-holidays/"
    STOCKS_REFERENCE_MARKET_STATUS = "/stocks/reference/market-status/"
    STOCKS_REFERENCE_NEWS = "/stocks/reference/news/"
    STOCKS_REFERENCE_SPLITS = "/stocks/reference/splits/"
    STOCKS_REFERENCE_TICKER = "/stocks/reference/tickers/{ticker}/"
    STOCKS_REFERENCE_TICKER_EVENTS = "/stocks/reference/tickers/{id}/events/"
    STOCKS_REFERENCE_TICKER_TYPES = "/stocks/reference/tickers/types/"
    STOCKS_REFERENCE_TICKERS = "/stocks/reference/tickers/"
    STOCKS_RELATED_COMPANIES = "/stocks/related-companies/{ticker}/"
    STOCKS_SNAPSHOT_MARKET = "/stocks/snapshot/tickers/"
    STOCKS_SNAPSHOT_MOVERS = "/stocks/snapshot/movers/{direction}/"
    STOCKS_SNAPSHOT_TICKER = "/stocks/snapshot/tickers/{stocksTicker}/"
    STOCKS_SNAPSHOT_UNIFIED = "/snapshot/"
    STOCKS_SHORT_INTEREST = "/stocks/short-interest/"
    STOCKS_SHORT_VOLUME = "/stocks/short-volume/"
    STOCKS_TRADES = "/stocks/trades/{stockTicker}/"


    # FMP app endpoints
    ANALYST_ESTIMATES = "/analysts/{symbol}/{period}/estimates/"
    ANALYST_PRICE_TARGETS = "/analysts/{symbol}/price-targets/"
    ANALYST_RECOMMENDATIONS = "/analysts/{symbol}/recommendations/" #paid
    ANALYST_UPGRADES_DOWNGRADES = "/analysts/{symbol}/upgrades-downgrades/"
    COMMODITIES_AGRICULTURAL = "/commodities/agricultural/"
    COMMODITIES_ENERGY = "/commodities/energy/"
    COMMODITIES_HISTORICAL = "/commodities/{symbol}/historical/"
    COMMODITIES_METALS = "/commodities/metals/"
    COMPANY_EXECUTIVES = "/reference/ticker/{symbol}/company-executives/"
    CRYPTO_HISTORICAL = "/crypto/{symbol}/historical/"
    CRYPTO_LIST = "/crypto/list/"
    CRYPTO_QUOTE = "/crypto/{symbol}/"
    ECONOMY_INFLATION = "/economy/{name}/inflation/"
    ECONOMY_GDP = "/economy/gdp/" #-
    ECONOMY_TREASURY_RATES = "/economy/treasury-rates/"
    ECONOMY_UNEMPLOYMENT = "/economy/unemployment/" #-
    EARNINGS_CALENDAR = "/earnings/calendar/"
    EARNINGS_HISTORY = "/earnings/{symbol}/history/"
    EARNINGS_SURPRISES = "/earnings/{symbol}/surprises/" #paid
    EARNINGS_TRANSCRIPTS = "/earnings/{symbol}/transcripts/" #paid
    EMPLOYEE_COUNT = "/reference/ticker/{symbol}/employee-count/"
    EMPLOYEE_COUNT_HISTORICAL = "/reference/ticker/{symbol}/employee-count/historical/"
    # ENTERPRISE_VALUES = "/fundamentals/{symbol}/enterprise-value/"  # INTERNAL DUPLICATE: Use FUNDAMENTALS_ENTERPRISE_VALUE
    EVENTS_DIVIDEND = "/events/dividend-calendar/"
    # EVENTS_IPO = "/events/ipo-calendar/"  # DUPLICATE: Use STOCKS_REFERENCE_IPOS from Polygon
    ETF_HOLDINGS = "/etf/{symbol}/holdings/" #paid
    # ETF_LIST = "/etf/list/" #Non existent endpoint in FMP
    ETF_PERFORMANCE = "/etf/{symbol}/performance/" #paid
    EXEC_COMP = "/corporate/{symbol}/executive-compensation/"
    EXEC_COMP_BENCHMARK = "/corporate/executive-compensation/benchmark/" #paid
    EXCHANGE_VARIANTS = "/reference/exchange-variants/" #paid
    FOREX_PAIR = "/forex/{symbol}/"
    FOREX_RATES = "/forex/rates/" #paid
    FUNDAMENTALS_BALANCE_SHEET = "/fundamentals/{symbol}/balance-sheet/"
    FUNDAMENTALS_CASH_FLOW = "/fundamentals/{symbol}/cash-flow/"
    FUNDAMENTALS_DCF = "/fundamentals/{symbol}/dcf/"
    FUNDAMENTALS_INCOME_STATEMENT = "/fundamentals/{symbol}/income-statement/"
    FUNDAMENTALS_METRICS = "/fundamentals/{symbol}/metrics/"
    FUNDAMENTALS_SCREENER = "/fundamentals/screener/"
    # HISTORICAL = "/historical/{symbol}/"  # SIMILAR: Use STOCKS_AGGREGATE_CUSTOM_RANGE from Polygon
    # HISTORICAL_DIVIDENDS = "/historical/{symbol}/dividends/"  # DUPLICATE: Use STOCKS_REFERENCE_DIVIDENDS from Polygon
    HISTORICAL_INTRADAY = "/historical/{symbol}/intraday/"
    # HISTORICAL_SPLITS = "/historical/{symbol}/splits/"  # DUPLICATE: Use STOCKS_REFERENCE_SPLITS from Polygon
    INSTITUTIONAL_13F = "/institutional/{symbol}/13f/"
    INSTITUTIONAL_HOLDERS = "/institutional/{symbol}/holders/"
    INSTITUTIONAL_INSIDER_TRADING = "/institutional/{symbol}/insider-trading/"
    INTERNATIONAL_EXCHANGES = "/international/exchanges/"
    INTERNATIONAL_STOCKS = "/international/{exchange}/stocks/"
    MERGERS_ACQUISITIONS = "/corporate/mergers-acquisitions/"
    MERGERS_ACQUISITIONS_SEARCH = "/corporate/mergers-acquisitions/search/"
    # NEWS = "/news/"  # DUPLICATE: Use STOCKS_REFERENCE_NEWS from Polygon
    NEWS_PRESS_RELEASES = "/news/press-releases/"
    NEWS_SENTIMENT = "/news/sentiment/"
    NEWS_SYMBOL = "/news/{symbol}/"
    NEWS_SYMBOL_PRESS_RELEASES = "/news/{symbol}/press-releases/"
    QUOTES_BATCH = "/quotes/batch/"
    # QUOTES_LOSERS = "/quotes/losers/"  # SIMILAR: Use STOCKS_SNAPSHOT_MOVERS from Polygon
    # QUOTES_MOST_ACTIVE = "/quotes/most-active/"  # SIMILAR: Use STOCKS_SNAPSHOT_MOVERS from Polygon
    # QUOTES_SINGLE = "/quotes/{symbol}/"  # SIMILAR: Use STOCKS_QUOTES from Polygon
    # REFERENCE_EXCHANGES = "/reference/exchanges/"  # DUPLICATE: Use STOCKS_REFERENCE_EXCHANGES from Polygon
    REFERENCE_MARKET_CAP = "/reference/market-cap/{symbol}/"
    # REFERENCE_TICKER = "/reference/ticker/{symbol}/"  # SIMILAR: Use STOCKS_REFERENCE_TICKER from Polygon
    # REFERENCE_TICKER_EXECUTIVES = "/reference/ticker/{symbol}/executives/"  # INTERNAL DUPLICATE: Use COMPANY_EXECUTIVES
    REFERENCE_TICKER_OUTLOOK = "/reference/ticker/{symbol}/outlook/"
    # REFERENCE_TICKER_PROFILE = "/reference/ticker/{symbol}/profile/"  # INTERNAL DUPLICATE: Use REFERENCE_TICKER
    SEARCH_CIK = "/reference/{cik}/search/cik/"
    SEARCH_CUSIP = "/reference/search/cusip/"
    SEARCH_ISIN = "/reference/search/isin/"
    SEC_FILINGS = "/sec/{symbol}/filings/"
    SEC_RSS = "/sec/rss-feed/"
    SHARES_FLOAT = "/reference/ticker/{symbol}/shares-float/"
    SHARES_FLOAT_ALL = "/reference/shares-float/all/"
    SYMBOL_CHANGE = "/reference/symbol-change/" #paid


class EndpointToFMP(Enum):
    COMPANY_EXECUTIVES = "/stable/key-executives"
    EMPLOYEE_COUNT = "/stable/employee-count"
    EMPLOYEE_COUNT_HISTORICAL = "/stable/historical-employee-count"
    EXEC_COMP = "/stable/governance-executive-compensation"
    EXEC_COMP_BENCHMARK = "/stable/executive-compensation-benchmark"
    EXCHANGE_VARIANTS = "/stable/search-exchange-variants"
    MERGERS_ACQUISITIONS = "/stable/mergers-acquisitions-latest"
    MERGERS_ACQUISITIONS_SEARCH = "/stable/mergers-acquisitions-search"
    SEARCH_CIK = "/stable/search-cik"
    SEARCH_CUSIP = "/stable/search-cusip"
    SEARCH_ISIN = "/stable/search-isin"
    SHARES_FLOAT = "/stable/shares-float"
    SHARES_FLOAT_ALL = "/stable/shares-float-all"
    SYMBOL_CHANGE = "/stable/symbol-change"
    ANALYST_ESTIMATES = "/stable/analyst-estimates"
    ANALYST_PRICE_TARGETS = "/stable/price-target-summary"
    ANALYST_RECOMMENDATIONS = "/stable/rating-bulk"
    ANALYST_UPGRADES = "/stable/grades"
    FUNDAMENTALS_BALANCE_SHEET = "/stable/balance-sheet-statement"
    FUNDAMENTALS_CASH_FLOW = "/stable/cash-flow-statement"
    COMMODITIES_LIST = "/stable/commodities-list"
    HISTORICAL_PRICES = "/stable/historical-price-eod/light"
    CRYPTO_LIST = "/stable/cryptocurrency-list"
    CRYPTO_QUOTE = "/stable/quote"
    FUNDAMENTALS_DCF = "/stable/discounted-cash-flow"
    EVENTS_DIVIDEND = "/stable/dividends-calendar"
    EARNINGS_CALENDAR = "/stable/earnings-calendar"
    EARNINGS_HISTORY = "/stable/earnings"
    EARNINGS_SURPRISES = "/stable/earnings-surprises-bulk"
    EARNINGS_TRANSCRIPTS = "/stable/earning-call-transcript-dates"
    ETF_HOLDINGS = "/stable/etf/holdings"
    ETF_PERFORMANCE = "/stable/etf/info"
    FOREX_PAIR = "/stable/quote"
    FOREX_RATES = "/stable/forex-list"
    ECO_INDICATORS = "/stable/economic-indicators"
    ECO_TREASURY = "/stable/treasury-rates"

    FUND_IS = "/stable/income-statement"
    FUND_METRICS = "/stable/key-metrics"
    FUND_SCREENER = "/stable/company-screener"

    HISTORICAL_INTRADAY = "/stable/historical-price-eod/light"

    INST_13F = "/stable/institutional-ownership/symbol-positions-summary"
    INST_HOLDERS = "/stable/institutional-ownership/extract-analytics/holder"
    INST_INSIDER = "/stable/insider-trading/search"

    INT_EXCHANGES = "/stable/available-exchanges"
    INT_STOCKS = "/stable/stock-list"

    NEWS_PR = "/stable/news/press-releases-latest"
    NEWS_SYMBOL_PR = "/stable/news/press-releases"

    QUOTES_GAINERS = "/stable/biggest-gainers"
    QUOTES_BATCH = "/stable/batch-quote"

    REFERENCE_MARKET_CAP = "/stable/market-capitalization"

    SEC_FILINGS = "/stable/sec-filings-search/symbol"


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

    class AnalystEstimates(Enum):
        symbol = "symbol"
        period = "period"
        page = "page"
        limit = "limit"


    class AnalystPriceTargets(Enum):
        symbol = "symbol"

    class AnalystUpgrades(Enum):
        symbol = "symbol"

    class BalanceSheet(Enum):
        symbol = "symbol"
        limit = "limit"
        period = "period"

    class CashFlow(Enum):
        symbol = "symbol"
        limit = "limit"
        period = "period"

    class HistoricalPrices(Enum):
        symbol = "symbol"
        from_= "from"
        to = "to"

    class CryptoQuote(Enum):
        symbol = "symbol"

    class FundamentalsDCF(Enum):
        symbol = "symbol"

    class DividendsCalendar(Enum):
        from_ = "from"
        to = "to"

    class EarningsHistory(Enum):
        symbol = "symbol"
        limit = "limit"

    class EarningsSurprises(Enum):
        year = "year"

    class EarningsTranscripts(Enum):
        symbol = "symbol"

    class ETFHoldings(Enum):
        symbol = "symbol"

    class SymbolChange(Enum):
        invalid = "invalid"
        limit = "limit"

    class ETFPerformance(Enum):
        symbol = "symbol"

    class ForexPair(Enum):
        symbol = "symbol"

    class EconomicIndicators(Enum):
        name = "name"
        from_ = "from"
        to = "to"

    class TreasuryRates(Enum):
        from_ = "from"
        to = "to"

    class IPOCalendar(Enum):
        from_ = "from"
        to = "to"
        page = "page"
        limit = "limit"

    class IncomeStatement(Enum):
        symbol = "symbol"
        limit = "limit"
        period = "period"

    class EnterpriseValues(Enum):
        symbol = "symbol"
        limit = "limit"
        period = "period"

    class KeyMetrics(Enum):
        symbol = "symbol"
        limit = "limit"
        period = "period"

    class DividendsCompany(Enum):
        symbol = "symbol"
        from_ = "from"
        to = "to"
        page = "page"
        limit = "limit"

    class Splits(Enum):
        symbol = "symbol"
        from_ = "from"
        to = "to"
        page = "page"
        limit = "limit"

    class InstitutionalOwnership(Enum):
        symbol = "symbol"
        cik = "cik"
        year = "year"
        quarter = "quarter"
        page = "page"
        limit = "limit"
        date = "date"

    class InstitutionalHolders(Enum):
        symbol = "symbol"
        year = "year"
        quarter = "quarter"
        page = "page"
        limit = "limit"

    class InsiderTrading(Enum):
        symbol = "symbol"
        page = "page"
        limit = "limit"
        reportingCik = "reportingCik"
        companyCik = "companyCik"
        transactionType = "transactionType"

    class ExchangeList(Enum):
        page = "page"
        limit = "limit"

    class StockList(Enum):
        exchange = "exchange"
        page = "page"
        limit = "limit"

    class GeneralNews(Enum):
        page = "page"
        limit = "limit"
        from_ = "from"
        to = "to"
        symbols = "symbols"

    class PressReleases(Enum):
        from_ = "from"
        to = "to"
        page = "page"
        limit = "limit"

    class PressReleasesSymbol(Enum):
        symbols = "symbols"
        from_ = "from"
        to = "to"
        page = "page"
        limit = "limit"

    class CompanyExecutives(Enum):
        symbol = "symbol"
        active = "active"

    class ProfileParams(Enum):
        symbol = "symbol"

    class QuoteBatch(Enum):
        symbols = "symbols"

    class MarketCapitalization(Enum):
        symbol = "symbol"

    class SharesFloatAll(Enum):
        limit = "limit"
        page = "page"

    class SharesFloat(Enum):
        symbol = "symbol"

    class CompanyScreenerStable(Enum):
        marketCapLowerThan = "marketCapLowerThan"
        marketCapMoreThan = "marketCapMoreThan"
        sector = "sector"
        industry = "industry"
        betaLowerThan = "betaLowerThan"
        betaMoreThan = "betaMoreThan"
        priceLowerThan = "priceLowerThan"
        priceMoreThan = "priceMoreThan"
        dividendLowerThan = "dividendLowerThan"
        dividendMoreThan = "dividendMoreThan"
        volumeLowerThan = "volumeLowerThan"
        volumeMoreThan = "volumeMoreThan"
        exchange = "exchange"
        country = "country"
        isEtf = "isEtf"
        isFund = "isFund"
        includeAllShareClasses = "includeAllShareClasses"
        isActivelyTrading = "isActivelyTrading"
        limit = "limit"

    class Unemployment(Enum):
        name = "name"
        from_ = "from"
        to = "to"

    class EarningsCalendar(Enum):
        from_ = "from"
        to = "to"

    class HistoricalIntraday(Enum):
        symbol = "symbol"
        nonadjusted = "nonadjusted"
        from_ = "from"
        to = "to"

    class HistoricalRange(Enum):
        from_ = "from"
        serietype = "serietype"
        timeseries = "timeseries"
        to = "to"

    class EmployeeCount(Enum):
        symbol = "symbol"
        limit = "limit"

    class EmployeeCountHistorical(Enum):
        symbol = "symbol"
        limit = "limit"

    class ThirteenFFilings(Enum):
        symbol = "symbol"
        year = "year"
        quarter = "quarter"

    class ExecutiveCompensation(Enum):
        symbol = "symbol"

    class SECFilings(Enum):
        symbol = "symbol"
        from_ = "from"
        to = "to"
        page = "page"
        limit = "limit"

    class ExecutiveCompensationBenchmark(Enum):
        year = "year"

    class ExchangeVariants(Enum):
        symbol = "symbol"

    class MergersAcquisitions(Enum):
        page = "page"
        limit = "limit"

    class MergersAcquisitionsSearch(Enum):
        name = "name"

    class SearchCIK(Enum):
        cik = "cik"
        limit = "limit"

    class SearchCUSIP(Enum):
        cusip = "cusip"

    class SearchISIN(Enum):
        isin = "isin"

class DeniedHosts(Enum):
    """
    Enum containing provider base URLs that should be filtered from responses.
    These URLs will be detected and removed/rewritten by the ProviderResponseSerializer.
    """
    FMP_BASE_URL = "https://financialmodelingprep.com"
    POLYGON_BASE_URL = "https://api.polygon.io"
    
    # Alternative domains that might appear in responses
    FMP_ALT_DOMAIN = "financialmodelingprep.com"
    POLYGON_ALT_DOMAIN = "api.polygon.io"
    
    # Polygon subdomains and CDN URLs
    POLYGON_S3_DOMAIN = "s3.polygon.io"
    POLYGON_CDN_DOMAIN = "polygon.io"


class EndpointTo:
    FMP = EndpointToFMP
    Polygon = EndpointToPolygon

