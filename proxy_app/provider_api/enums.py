from enum import Enum


class EndpointFrom(Enum):
    """
    Application route paths exposed by our API under PREFIX_ENDPOINT.
    Grouped by provider section comments (Polygon vs FMP). Values are app routes.
    """

    # Examples (keep)
    EXAMPLE_FMP_GAINERS = "/examples/fmp/gainers/"
    EXAMPLE_POLYGON_TRADES = "/examples/polygon/{symbol}/trades/"

    PREFIX_ENDPOINT = "/api/v1"

    # Polygon stock API endpoints (app routes)
    STOCKS_AGGREGATE_CUSTOM_RANGE = "/stocks/aggs/{stocksTicker}/range/{multiplier}/{timespan}/{from}/{to}/"
    STOCKS_AGGREGATE_GROUPED_DAILY = "/stocks/aggs/grouped/{date}/"
    STOCKS_AGGREGATE_PREVIOUS_DAY = "/stocks/aggs/{stocksTicker}/prev/"
    STOCKS_INDICATOR_EMA = "/stocks/indicators/ema/{stockTicker}/"
    STOCKS_INDICATOR_MACD = "/stocks/indicators/macd/{stockTicker}/"
    STOCKS_INDICATOR_RSI = "/stocks/indicators/rsi/{stockTicker}/"
    STOCKS_INDICATOR_SMA = "/stocks/indicators/sma/{stockTicker}/"
    STOCKS_OPEN_CLOSE = "/stocks/open-close/{stocksTicker}/{date}/"
    STOCKS_QUOTES = "/stocks/quotes/{stockTicker}/"  # Paid
    STOCKS_REFERENCE_CONDITIONS = "/stocks/reference/conditions/"
    STOCKS_REFERENCE_DIVIDENDS = "/stocks/reference/dividends/"
    STOCKS_REFERENCE_EXCHANGES = "/stocks/reference/exchanges/"
    STOCKS_REFERENCE_FINANCIALS = "/stocks/reference/financials/"
    STOCKS_REFERENCE_MARKET_HOLIDAYS = "/stocks/reference/market-holidays/"
    STOCKS_REFERENCE_MARKET_STATUS = "/stocks/reference/market-status/"
    STOCKS_REFERENCE_NEWS = "/stocks/reference/news/"
    STOCKS_REFERENCE_SPLITS = "/stocks/reference/splits/"
    STOCKS_REFERENCE_TICKER = "/stocks/reference/tickers/{ticker}/"
    STOCKS_REFERENCE_TICKER_EVENTS = "/stocks/reference/tickers/{id}/events/"
    STOCKS_REFERENCE_TICKER_TYPES = "/stocks/reference/tickers/types/"
    STOCKS_REFERENCE_TICKERS = "/stocks/reference/tickers/"
    STOCKS_RELATED_COMPANIES = "/stocks/related-companies/{ticker}/"
    STOCKS_SNAPSHOT_MARKET = "/stocks/snapshot/tickers/"  # Paid
    STOCKS_SNAPSHOT_MOVERS = "/stocks/snapshot/movers/{direction}/"  # Paid
    STOCKS_SNAPSHOT_TICKER = "/stocks/snapshot/tickers/{stocksTicker}/"
    STOCKS_SNAPSHOT_UNIFIED = "/snapshot/"  # Paid
    STOCKS_SHORT_INTEREST = "/stocks/short-interest/"
    STOCKS_SHORT_VOLUME = "/stocks/short-volume/"
    STOCKS_TRADES = "/stocks/trades/{stockTicker}/"  # Paid
    # STOCKS_LAST_NBBO = "/stocks/last-quote/{stocksTicker}/"
    # STOCKS_LAST_TRADE = "/stocks/last-trade/{stocksTicker}/"
    # STOCKS_REFERENCE_IPOS = "/stocks/reference/ipos/"

    # FMP app endpoints
    ANALYST_ESTIMATES = "/analysts/{symbol}/{period}/estimates/"
    ANALYST_PRICE_TARGETS = "/analysts/{symbol}/price-targets/"
    ANALYST_RECOMMENDATIONS = "/analysts/{symbol}/recommendations/"  # paid
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
    ECONOMY_TREASURY_RATES = "/economy/treasury-rates/"
    EARNINGS_CALENDAR = "/earnings/calendar/"
    EARNINGS_HISTORY = "/earnings/{symbol}/history/"
    EARNINGS_SURPRISES = "/earnings/{symbol}/surprises/"  # paid
    EARNINGS_TRANSCRIPTS = "/earnings/{symbol}/transcripts/"  # paid
    EMPLOYEE_COUNT = "/reference/ticker/{symbol}/employee-count/"
    EMPLOYEE_COUNT_HISTORICAL = "/reference/ticker/{symbol}/employee-count/historical/"
    ETF_HOLDINGS = "/etf/{symbol}/holdings/"  # paid
    ETF_PERFORMANCE = "/etf/{symbol}/performance/"  # paid
    EVENTS_DIVIDEND = "/events/dividend-calendar/"
    EXCHANGE_VARIANTS = "/reference/exchange-variants/"  # paid
    EXEC_COMP = "/corporate/{symbol}/executive-compensation/"
    EXEC_COMP_BENCHMARK = "/corporate/executive-compensation/benchmark/"  # paid
    FOREX_PAIR = "/forex/{symbol}/"
    FOREX_RATES = "/forex/rates/"  # paid
    FUNDAMENTALS_BALANCE_SHEET = "/fundamentals/{symbol}/balance-sheet/"
    FUNDAMENTALS_CASH_FLOW = "/fundamentals/{symbol}/cash-flow/"
    FUNDAMENTALS_DCF = "/fundamentals/{symbol}/dcf/"
    FUNDAMENTALS_INCOME_STATEMENT = "/fundamentals/{symbol}/income-statement/"
    FUNDAMENTALS_METRICS = "/fundamentals/{symbol}/metrics/"
    FUNDAMENTALS_SCREENER = "/fundamentals/screener/"
    HISTORICAL_INTRADAY = "/historical/{symbol}/intraday/"
    INSTITUTIONAL_13F = "/institutional/{symbol}/13f/"
    INSTITUTIONAL_HOLDERS = "/institutional/{symbol}/holders/"
    INSTITUTIONAL_INSIDER_TRADING = "/institutional/{symbol}/insider-trading/"
    INTERNATIONAL_EXCHANGES = "/international/exchanges/"
    INTERNATIONAL_STOCKS = "/international/{exchange}/stocks/"
    MERGERS_ACQUISITIONS = "/corporate/mergers-acquisitions/"
    MERGERS_ACQUISITIONS_SEARCH = "/corporate/mergers-acquisitions/search/"
    NEWS_PRESS_RELEASES = "/news/press-releases/"
    NEWS_SENTIMENT = "/news/sentiment/"
    NEWS_SYMBOL = "/news/{symbol}/"
    NEWS_SYMBOL_PRESS_RELEASES = "/news/{symbol}/press-releases/"
    QUOTES_BATCH = "/quotes/batch/"
    REFERENCE_MARKET_CAP = "/reference/market-cap/{symbol}/"
    SEARCH_CIK = "/reference/{cik}/search/cik/"
    SEARCH_CUSIP = "/reference/search/cusip/"
    SEARCH_ISIN = "/reference/search/isin/"
    SEC_FILINGS = "/sec/{symbol}/filings/"
    SEC_RSS = "/sec/rss-feed/"
    SHARES_FLOAT = "/reference/ticker/{symbol}/shares-float/"
    SHARES_FLOAT_ALL = "/reference/shares-float/all/"
    SYMBOL_CHANGE = "/reference/symbol-change/"  # paid
    # ECONOMY_GDP = "/economy/gdp/" #-
    # ECONOMY_UNEMPLOYMENT = "/economy/unemployment/" #-
    # ENTERPRISE_VALUES = "/fundamentals/{symbol}/enterprise-value/"  # INTERNAL DUPLICATE: Use FUNDAMENTALS_ENTERPRISE_VALUE
    # EVENTS_IPO = "/events/ipo-calendar/"  # DUPLICATE: Use STOCKS_REFERENCE_IPOS from Polygon
    # ETF_LIST = "/etf/list/" #Non existent endpoint in FMP
    # HISTORICAL = "/historical/{symbol}/"  # SIMILAR: Use STOCKS_AGGREGATE_CUSTOM_RANGE from Polygon
    # HISTORICAL_DIVIDENDS = "/historical/{symbol}/dividends/"  # DUPLICATE: Use STOCKS_REFERENCE_DIVIDENDS from Polygon
    # HISTORICAL_SPLITS = "/historical/{symbol}/splits/"  # DUPLICATE: Use STOCKS_REFERENCE_SPLITS from Polygon
    # NEWS = "/news/"  # DUPLICATE: Use STOCKS_REFERENCE_NEWS from Polygon
    # REFERENCE_EXCHANGES = "/reference/exchanges/"  # DUPLICATE: Use STOCKS_REFERENCE_EXCHANGES from Polygon
    # REFERENCE_TICKER = "/reference/ticker/{symbol}/"  # SIMILAR: Use STOCKS_REFERENCE_TICKER from Polygon
    # REFERENCE_TICKER_EXECUTIVES = "/reference/ticker/{symbol}/executives/"  # INTERNAL DUPLICATE: Use COMPANY_EXECUTIVES
    # REFERENCE_TICKER_PROFILE = "/reference/ticker/{symbol}/profile/"  # INTERNAL DUPLICATE: Use REFERENCE_TICKER
    # QUOTES_LOSERS = "/quotes/losers/"  # SIMILAR: Use STOCKS_SNAPSHOT_MOVERS from Polygon
    # QUOTES_MOST_ACTIVE = "/quotes/most-active/"  # SIMILAR: Use STOCKS_SNAPSHOT_MOVERS from Polygon
    # QUOTES_SINGLE = "/quotes/{symbol}/"  # SIMILAR: Use STOCKS_QUOTES from Polygon


class EndpointToFMP(Enum):
    """
    Provider-relative FMP endpoint paths used to build outbound requests.
    These values are joined with the configured FMP base URL by the client.
    """

    ANALYST_ESTIMATES = "/stable/analyst-estimates"
    ANALYST_PRICE_TARGETS = "/stable/price-target-summary"
    ANALYST_RECOMMENDATIONS = "/stable/rating-bulk"
    ANALYST_UPGRADES = "/stable/grades"
    COMMODITIES_LIST = "/stable/commodities-list"
    COMPANY_EXECUTIVES = "/stable/key-executives"
    CRYPTO_LIST = "/stable/cryptocurrency-list"
    CRYPTO_QUOTE = "/stable/quote"
    ECO_INDICATORS = "/stable/economic-indicators"
    ECO_TREASURY = "/stable/treasury-rates"
    EARNINGS_CALENDAR = "/stable/earnings-calendar"
    EARNINGS_HISTORY = "/stable/earnings"
    EARNINGS_SURPRISES = "/stable/earnings-surprises-bulk"
    EARNINGS_TRANSCRIPTS = "/stable/earning-call-transcript-dates"
    EMPLOYEE_COUNT = "/stable/employee-count"
    EMPLOYEE_COUNT_HISTORICAL = "/stable/historical-employee-count"
    EVENTS_DIVIDEND = "/stable/dividends-calendar"
    ETF_HOLDINGS = "/stable/etf/holdings"
    ETF_PERFORMANCE = "/stable/etf/info"
    EXCHANGE_VARIANTS = "/stable/search-exchange-variants"
    EXEC_COMP = "/stable/governance-executive-compensation"
    EXEC_COMP_BENCHMARK = "/stable/executive-compensation-benchmark"
    FOREX_PAIR = "/stable/quote"
    FOREX_RATES = "/stable/forex-list"
    FUND_IS = "/stable/income-statement"
    FUND_METRICS = "/stable/key-metrics"
    FUND_SCREENER = "/stable/company-screener"
    FUNDAMENTALS_BALANCE_SHEET = "/stable/balance-sheet-statement"
    FUNDAMENTALS_CASH_FLOW = "/stable/cash-flow-statement"
    FUNDAMENTALS_DCF = "/stable/discounted-cash-flow"
    HISTORICAL_INTRADAY = "/stable/historical-price-eod/light"
    HISTORICAL_PRICES = "/stable/historical-price-eod/light"
    INST_13F = "/stable/institutional-ownership/symbol-positions-summary"
    INST_HOLDERS = "/stable/institutional-ownership/extract-analytics/holder"
    INST_INSIDER = "/stable/insider-trading/search"
    INT_EXCHANGES = "/stable/available-exchanges"
    INT_STOCKS = "/stable/stock-list"
    MERGERS_ACQUISITIONS = "/stable/mergers-acquisitions-latest"
    MERGERS_ACQUISITIONS_SEARCH = "/stable/mergers-acquisitions-search"
    NEWS_PR = "/stable/news/press-releases-latest"
    NEWS_SYMBOL_PR = "/stable/news/press-releases"
    QUOTES_BATCH = "/stable/batch-quote"
    QUOTES_GAINERS = "/stable/biggest-gainers"
    REFERENCE_MARKET_CAP = "/stable/market-capitalization"
    SEARCH_CIK = "/stable/search-cik"
    SEARCH_CUSIP = "/stable/search-cusip"
    SEARCH_ISIN = "/stable/search-isin"
    SEC_FILINGS = "/stable/sec-filings-search/symbol"
    SHARES_FLOAT = "/stable/shares-float"
    SHARES_FLOAT_ALL = "/stable/shares-float-all"
    SYMBOL_CHANGE = "/stable/symbol-change"


class EndpointToPolygon(Enum):
    """
    Provider-relative Polygon endpoint paths used to build outbound requests.
    These values are joined with the configured Polygon base URL by the client.
    """

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
    REFERENCE_MARKET_HOLIDAYS = "/v1/marketstatus/upcoming"
    REFERENCE_MARKET_STATUS = "/v1/marketstatus/now"
    REFERENCE_NEWS = "/v2/reference/news"
    REFERENCE_SPLITS = "/v3/reference/splits"
    REFERENCE_TICKER = "/v3/reference/tickers/{ticker}"
    REFERENCE_TICKER_EVENTS = "/vX/reference/tickers/{id}/events"
    REFERENCE_TICKER_TYPES = "/v3/reference/tickers/types"
    REFERENCE_TICKERS = "/v3/reference/tickers"
    RELATED_COMPANIES = "/v1/related-companies/{ticker}"
    SNAPSHOT_MARKET = "/v2/snapshot/locale/us/markets/stocks/tickers"
    SNAPSHOT_MOVERS = "/v2/snapshot/locale/us/markets/stocks/{direction}"
    SNAPSHOT_TICKER = "/v2/snapshot/locale/us/markets/stocks/tickers/{stocksTicker}"
    SNAPSHOT_UNIFIED = "/v3/snapshot"
    STOCKS_SHORT_INTEREST = "/stocks/v1/short-interest"
    STOCKS_SHORT_VOLUME = "/stocks/v1/short-volume"
    TRADES = "/v3/trades/{stockTicker}"


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

    This top-level class documents the grouping; each nested Enum defines the
    allowed query parameters for a specific Polygon endpoint or category.
    """

    class AggregateCustomRange(Enum):
        adjusted = "adjusted"

    class AggregateGroupedDaily(Enum):
        adjusted = "adjusted"
        include_otc = "include_otc"

    class Common(Enum):
        cursor = "cursor"

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

    class OpenClose(Enum):
        adjusted = "adjusted"

    class Quotes(Enum):
        timestamp = "timestamp"

    class ReferenceConditions(Enum):
        asset_class = "asset_class"
        data_type = "data_type"
        id = "id"
        sip = "sip"

    class ReferenceDividends(Enum):
        cash_amount = "cash_amount"
        declaration_date = "declaration_date"
        dividend_type = "dividend_type"
        ex_dividend_date = "ex_dividend_date"
        frequency = "frequency"
        pay_date = "pay_date"
        record_date = "record_date"
        ticker = "ticker"

    class ReferenceExchanges(Enum):
        asset_class = "asset_class"
        locale = "locale"

    class ReferenceFinancials(Enum):
        cik = "cik"
        company_name = "company_name"
        filing_date = "filing_date"
        include_sources = "include_sources"
        period_of_report_date = "period_of_report_date"
        sic = "sic"
        ticker = "ticker"
        timeframe = "timeframe"

    class ReferenceIPOs(Enum):
        isin = "isin"
        listing_date = "listing_date"
        ticker = "ticker"
        us_code = "us_code"

    class ReferenceNews(Enum):
        published_utc = "published_utc"
        ticker = "ticker"

    class ReferenceSplits(Enum):
        execution_date = "execution_date"
        reverse_split = "reverse_split"
        ticker = "ticker"

    class ReferenceTicker(Enum):
        date = "date"

    class ReferenceTickerEvents(Enum):
        types = "types"

    class ReferenceTickerTypes(Enum):
        asset_class = "asset_class"
        locale = "locale"

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

    class SnapshotMarket(Enum):
        include_otc = "include_otc"
        tickers = "tickers"

    class SnapshotMovers(Enum):
        include_otc = "include_otc"

    class SnapshotUnified(Enum):
        ticker = "ticker"
        type = "type"

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

    class Trades(Enum):
        timestamp = "timestamp"


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

    This top-level class documents the grouping; each nested Enum defines the
    allowed query parameters for a specific FMP endpoint or category.
    """

    class AnalystEstimates(Enum):
        limit = "limit"
        page = "page"
        period = "period"
        symbol = "symbol"

    class AnalystPriceTargets(Enum):
        symbol = "symbol"

    class AnalystUpgrades(Enum):
        symbol = "symbol"

    class BalanceSheet(Enum):
        limit = "limit"
        period = "period"
        symbol = "symbol"

    class CashFlow(Enum):
        limit = "limit"
        period = "period"
        symbol = "symbol"

    class CompanyExecutives(Enum):
        active = "active"
        symbol = "symbol"

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

    class CryptoQuote(Enum):
        symbol = "symbol"

    class DividendsCalendar(Enum):
        from_ = "from"
        to = "to"

    class DividendsCompany(Enum):
        from_ = "from"
        limit = "limit"
        page = "page"
        symbol = "symbol"
        to = "to"

    class EconomicIndicators(Enum):
        from_ = "from"
        name = "name"
        to = "to"

    class EmployeeCount(Enum):
        limit = "limit"
        symbol = "symbol"

    class EmployeeCountHistorical(Enum):
        limit = "limit"
        symbol = "symbol"

    class EnterpriseValues(Enum):
        limit = "limit"
        period = "period"
        symbol = "symbol"

    class ETFHoldings(Enum):
        symbol = "symbol"

    class ETFPerformance(Enum):
        symbol = "symbol"

    class ExchangeList(Enum):
        limit = "limit"
        page = "page"

    class ExchangeVariants(Enum):
        symbol = "symbol"

    class ExecutiveCompensation(Enum):
        symbol = "symbol"

    class ExecutiveCompensationBenchmark(Enum):
        year = "year"

    class EarningsCalendar(Enum):
        from_ = "from"
        to = "to"

    class EarningsHistory(Enum):
        limit = "limit"
        symbol = "symbol"

    class EarningsSurprises(Enum):
        year = "year"

    class EarningsTranscripts(Enum):
        symbol = "symbol"

    class ForexPair(Enum):
        symbol = "symbol"

    class GeneralNews(Enum):
        from_ = "from"
        limit = "limit"
        page = "page"
        symbols = "symbols"
        to = "to"

    class HistoricalIntraday(Enum):
        from_ = "from"
        nonadjusted = "nonadjusted"
        symbol = "symbol"
        to = "to"

    class HistoricalPrices(Enum):
        from_ = "from"
        symbol = "symbol"
        to = "to"

    class HistoricalRange(Enum):
        from_ = "from"
        serietype = "serietype"
        timeseries = "timeseries"
        to = "to"

    class IncomeStatement(Enum):
        limit = "limit"
        period = "period"
        symbol = "symbol"

    class InsiderTrading(Enum):
        companyCik = "companyCik"
        limit = "limit"
        page = "page"
        reportingCik = "reportingCik"
        symbol = "symbol"
        transactionType = "transactionType"

    class InstitutionalHolders(Enum):
        limit = "limit"
        page = "page"
        quarter = "quarter"
        symbol = "symbol"
        year = "year"

    class InstitutionalOwnership(Enum):
        cik = "cik"
        date = "date"
        limit = "limit"
        page = "page"
        quarter = "quarter"
        symbol = "symbol"
        year = "year"

    class IPOCalendar(Enum):
        from_ = "from"
        limit = "limit"
        page = "page"
        to = "to"

    class KeyMetrics(Enum):
        limit = "limit"
        period = "period"
        symbol = "symbol"

    class MarketCapitalization(Enum):
        symbol = "symbol"

    class MergersAcquisitions(Enum):
        limit = "limit"
        page = "page"

    class MergersAcquisitionsSearch(Enum):
        name = "name"

    class PressReleases(Enum):
        from_ = "from"
        limit = "limit"
        page = "page"
        to = "to"

    class PressReleasesSymbol(Enum):
        from_ = "from"
        limit = "limit"
        page = "page"
        symbols = "symbols"
        to = "to"

    class ProfileParams(Enum):
        symbol = "symbol"

    class QuoteBatch(Enum):
        symbols = "symbols"

    class SECFilings(Enum):
        from_ = "from"
        limit = "limit"
        page = "page"
        symbol = "symbol"
        to = "to"

    class SearchCIK(Enum):
        cik = "cik"
        limit = "limit"

    class SearchCUSIP(Enum):
        cusip = "cusip"

    class SearchISIN(Enum):
        isin = "isin"

    class SharesFloat(Enum):
        symbol = "symbol"

    class SharesFloatAll(Enum):
        limit = "limit"
        page = "page"

    class Splits(Enum):
        from_ = "from"
        limit = "limit"
        page = "page"
        symbol = "symbol"
        to = "to"

    class StockList(Enum):
        exchange = "exchange"
        limit = "limit"
        page = "page"

    class SymbolChange(Enum):
        invalid = "invalid"
        limit = "limit"

    class ThirteenFFilings(Enum):
        quarter = "quarter"
        symbol = "symbol"
        year = "year"

    class TreasuryRates(Enum):
        from_ = "from"
        to = "to"

    class FundamentalsDCF(Enum):
        symbol = "symbol"


class DeniedHosts(Enum):
    """
    Enum containing provider base URLs that should be filtered from responses.
    These URLs will be detected and removed/rewritten by the ProviderResponseSerializer.
    They are scrubbed from serialized responses to prevent leaking provider URLs.
    """

    FMP_ALT_DOMAIN = "financialmodelingprep.com"
    FMP_BASE_URL = "https://financialmodelingprep.com"
    POLYGON_ALT_DOMAIN = "api.polygon.io"
    POLYGON_BASE_URL = "https://api.polygon.io"
    POLYGON_CDN_DOMAIN = "polygon.io"
    POLYGON_S3_DOMAIN = "s3.polygon.io"


class DeniedParameters(Enum):
    """
    Enum containing parameter names that should be filtered from responses.
    These parameters contain URLs that cannot be accessed by clients or should be hidden.
    These keys are removed from serialized payloads to avoid exposing internal links or provider metadata.
    """

    _SOURCE = "_source"
    FAVICON_URL = "favicon_url"
    ICON_URL = "icon_url"
    IMAGE_URL = "image_url"  # If it points to provider CDNs
    LOGO_URL = "logo_url"

    # Request ID from Polygon
    REQUEST_ID = "request_id"

    # Status from Polygon
    STATUS = "status"

    # Common parameters that might contain problematic URLs
    THUMBNAIL_URL = "thumbnail_url"


class EndpointTo:
    """
    Namespace binding that exposes provider-specific "to" endpoint enums.
    Use to reference provider routes without importing provider-specific classes.
    """

    FMP = EndpointToFMP
    Polygon = EndpointToPolygon
