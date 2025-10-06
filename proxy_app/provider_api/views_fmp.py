from rest_framework import serializers
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication

from users.authentication import RequestTokenAuthentication
from users.permissions import DailyLimitPermission

from .base import FMPBaseView
from .enums import EndpointFrom, EndpointTo, FMPParams


class AnalystEstimatesView(FMPBaseView):
    """
    Return analyst earnings estimates for a company.

    App path:
        /api/v1/analysts/{symbol}/estimates/

    Provider path:
        /stable/analyst-estimates

    Parameters:
        symbol (str): Ticker symbol.
        period (str): Annual, quarter

    """

    endpoint_from = EndpointFrom.ANALYST_ESTIMATES
    endpoint_to = EndpointTo.FMP.ANALYST_ESTIMATES
    allowed_params = FMPParams.AnalystEstimates


class AnalystPriceTargetsView(FMPBaseView):
    """
    Return analyst price targets and related metadata.

    App path:
        /api/v1/analysts/{symbol}/price-targets/

    Provider path:
        /stable/price-target-summary

    Parameters:
        symbol (str): Ticker symbol. Forwards other query params.

    Examples:
        /api/v1/earnings/AAPL/calendar/?from=2024-01-01
        /api/v1/earnings/AAPL/calendar/?to=2024-03-31

    Examples:
        /api/v1/analysts/AAPL/price-targets/?page=1
    """

    endpoint_from = EndpointFrom.ANALYST_PRICE_TARGETS
    endpoint_to = EndpointTo.FMP.ANALYST_PRICE_TARGETS
    allowed_params = FMPParams.AnalystPriceTargets


class AnalystRecommendationsView(FMPBaseView):
    """
    Return analyst stock recommendation trends for a company.

    App path:
        /api/v1/analysts/{symbol}/recommendations/

    Provider path:
        /stable/rating-bulk

    Parameters:
        symbol (str): Ticker symbol.
    """

    endpoint_from = EndpointFrom.ANALYST_RECOMMENDATIONS
    endpoint_to = EndpointTo.FMP.ANALYST_RECOMMENDATIONS


class AnalystUpgradesDowngradesView(FMPBaseView):
    """
    Return analyst upgrades and downgrades for a symbol.

    App path:
        /api/v1/analysts/{symbol}/upgrades-downgrades/

    Provider path:
        /stable/grades

    Parameters:
        symbol (str): Ticker symbol. Forwards other query params.

    Examples:
        /api/v1/analysts/AAPL/upgrades-downgrades/?from=2024-01-01
        /api/v1/analysts/AAPL/upgrades-downgrades/?to=2024-01-31
        /api/v1/analysts/AAPL/upgrades-downgrades/?page=2
    """

    endpoint_from = EndpointFrom.ANALYST_UPGRADES_DOWNGRADES
    endpoint_to = EndpointTo.FMP.ANALYST_UPGRADES
    allowed_params = FMPParams.AnalystUpgrades


class BalanceSheetView(FMPBaseView):
    """
    Retrieve balance sheet data for a company.

    App path:
        /api/v1/fundamentals/{symbol}/balance-sheet/

    Provider path:
        /stable/balance-sheet-statement

    Parameters:
        symbol (str): Ticker symbol.
    """

    endpoint_from = EndpointFrom.FUNDAMENTALS_BALANCE_SHEET
    endpoint_to = EndpointTo.FMP.FUNDAMENTALS_BALANCE_SHEET
    allowed_params = FMPParams.BalanceSheet


class CashFlowView(FMPBaseView):
    """
    Retrieve cash flow statement data for a company.

    App path:
        /api/v1/fundamentals/{symbol}/cash-flow/

    Provider path:
        /stable/cash-flow-statement

    Parameters:
        symbol (str): Ticker symbol.
    """

    endpoint_from = EndpointFrom.FUNDAMENTALS_CASH_FLOW
    endpoint_to = EndpointTo.FMP.FUNDAMENTALS_CASH_FLOW
    allowed_params = FMPParams.CashFlow


class CommoditiesAgriculturalView(FMPBaseView):
    """
    Return commodity quotes for agricultural products.

    App path:
        /api/v1/commodities/agricultural/

    Provider path:
        /stable/commodities-list

    Parameters:
        Forwards any query parameters to the provider unmodified.
    """

    endpoint_from = EndpointFrom.COMMODITIES_AGRICULTURAL
    endpoint_to = EndpointTo.FMP.COMMODITIES_LIST


class CommoditiesEnergyView(FMPBaseView):
    """
    Return commodity quotes for energy products.

    App path:
        /api/v1/commodities/energy/

    Provider path:
        /stable/commodities-list

    Parameters:
        Forwards any query parameters to the provider unmodified.
    """

    endpoint_from = EndpointFrom.COMMODITIES_ENERGY
    endpoint_to = EndpointTo.FMP.COMMODITIES_LIST


class CommoditiesHistoricalView(FMPBaseView):
    """
    Return historical price series for a commodity symbol.

    App path:
        /api/v1/commodities/{symbol}/historical/

    Provider path:
        /stable/historical-price-eod/light

    Parameters:
        symbol (str): Commodity symbol.
    """

    endpoint_from = EndpointFrom.COMMODITIES_HISTORICAL
    endpoint_to = EndpointTo.FMP.HISTORICAL_PRICES
    allowed_params = FMPParams.HistoricalPrices


class CommoditiesMetalsView(FMPBaseView):
    """
    Return commodity quotes for metals categories.

    App path:
        /api/v1/commodities/metals/

    Provider path:
        /stable/commodities-list

    Parameters:
        Forwards any query parameters to the provider unmodified.
    """

    endpoint_from = EndpointFrom.COMMODITIES_METALS
    endpoint_to = EndpointTo.FMP.COMMODITIES_LIST


class CryptoHistoricalView(FMPBaseView):
    """
    Return historical price series for a cryptocurrency.

    App path:
        /api/v1/crypto/{symbol}/historical/

    Provider path:
        /stable/historical-price-eod/light

    Parameters:
        symbol (str): Crypto ticker.
    """

    endpoint_from = EndpointFrom.CRYPTO_HISTORICAL
    endpoint_to = EndpointTo.FMP.HISTORICAL_PRICES
    allowed_params = FMPParams.HistoricalPrices


class CryptoListView(FMPBaseView):
    """
    List cryptocurrency tickers available from the provider.

    App path:
        /api/v1/crypto/list/

    Provider path:
        /stable/cryptocurrency-list

    Parameters:
        Forwards any query parameters to the provider unmodified.
    """

    endpoint_from = EndpointFrom.CRYPTO_LIST
    endpoint_to = EndpointTo.FMP.CRYPTO_LIST


class CryptoQuoteView(FMPBaseView):
    """
    Return a real-time quote for a cryptocurrency symbol.

    App path:
        /api/v1/crypto/{symbol}/

    Provider path:
        /stable/quote

    Parameters:
        symbol (str): Crypto ticker, e.g., "BTCUSD".
    """

    endpoint_from = EndpointFrom.CRYPTO_QUOTE
    endpoint_to = EndpointTo.FMP.CRYPTO_QUOTE
    allowed_params = FMPParams.CryptoQuote


class DCFView(FMPBaseView):
    """
    Return discounted cash flow estimates for a company.

    App path:
        /api/v1/fundamentals/{symbol}/dcf/

    Provider path:
        /stable/discounted-cash-flow

    Parameters:
        symbol (str): Ticker symbol.
    """

    endpoint_from = EndpointFrom.FUNDAMENTALS_DCF
    endpoint_to = EndpointTo.FMP.FUNDAMENTALS_DCF
    allowed_params = FMPParams.FundamentalsDCF


class DividendCalendarView(FMPBaseView):
    """
    List scheduled or historical dividend events.

    App path:
        /api/v1/events/dividend-calendar/

    Provider path:
        /stable/dividends-calendar

    Parameters:
        Forwards any query parameters to the provider unmodified.
    """

    endpoint_from = EndpointFrom.EVENTS_DIVIDEND
    endpoint_to = EndpointTo.FMP.EVENTS_DIVIDEND
    allowed_params = FMPParams.DividendsCalendar


class EarningsCalendarView(FMPBaseView):
    """
    Return upcoming or past earnings events for a symbol.

    App path:
        /api/v1/earnings/{symbol}/calendar/

    Provider path:
        /stable/earnings-calendar

    Parameters:
        symbol (str): Ticker symbol. Forwards other query params.
    """

    endpoint_from = EndpointFrom.EARNINGS_CALENDAR
    endpoint_to = EndpointTo.FMP.EARNINGS_CALENDAR
    allowed_params = FMPParams.EarningsCalendar


class EarningsHistoryView(FMPBaseView):
    """
    Return historical earnings calendar entries for a symbol.

    App path:
        /api/v1/earnings/{symbol}/history/

    Provider path:
        /stable/earnings

    Parameters:
        symbol (str): Ticker symbol.
    """

    endpoint_from = EndpointFrom.EARNINGS_HISTORY
    endpoint_to = EndpointTo.FMP.EARNINGS_HISTORY
    allowed_params = FMPParams.EarningsHistory


class EarningsSurprisesView(FMPBaseView):
    """
    Return earnings surprise data for a symbol.

    App path:
        /api/v1/earnings/{symbol}/surprises/

    Provider path:
        /stable/earnings-surprises-bulk

    Parameters:
        symbol (str): Ticker symbol.
    """

    endpoint_from = EndpointFrom.EARNINGS_SURPRISES
    endpoint_to = EndpointTo.FMP.EARNINGS_SURPRISES
    allowed_params = FMPParams.EarningsSurprises


class EarningsTranscriptsView(FMPBaseView):
    """
    Retrieve earnings call transcripts for a symbol.

    App path:
        /api/v1/earnings/{symbol}/transcripts/

    Provider path:
        /stable/earning-call-transcript-dates

    Parameters:
        symbol (str): Ticker symbol.
    """

    endpoint_from = EndpointFrom.EARNINGS_TRANSCRIPTS
    endpoint_to = EndpointTo.FMP.EARNINGS_TRANSCRIPTS
    allowed_params = FMPParams.EarningsTranscripts


# class EnterpriseValueView(FMPBaseView):
#     """
#     Return enterprise value history for a company.
#
#     App path:
#         /api/v1/fundamentals/{symbol}/enterprise-value/
#
#     Provider path:
#         /v3/enterprise-values/{symbol}
#
#     Parameters:
#         symbol (str): Ticker symbol.
#     """
#     # COMMENTED: INTERNAL DUPLICATE - Use FUNDAMENTALS_ENTERPRISE_VALUE
#     # endpoint_from = EndpointFrom.FUND_EV
#     # endpoint_to = EndpointTo.FMP.FUND_EV


class ETFHoldingsView(FMPBaseView):
    """
    Return holdings for a given ETF symbol.

    App path:
        /api/v1/etf/{symbol}/holdings/

    Provider path:
        stable/etf/holdings

    Parameters:
        symbol (str): ETF ticker.
    """

    endpoint_from = EndpointFrom.ETF_HOLDINGS
    endpoint_to = EndpointTo.FMP.ETF_HOLDINGS
    allowed_params = FMPParams.ETFHoldings


# Nonexistent endpoint in FMP
# class ETFListView(FMPBaseView):
#     """
#     List exchange-traded funds available from the provider.
#
#     App path:
#         /api/v1/etf/list/
#
#     Provider path:
#         /v3/etf/list
#
#     Parameters:
#         Forwards any query parameters to the provider unmodified.
#     """
#     endpoint_from = EndpointFrom.ETF_LIST
#     endpoint_to = EndpointTo.FMP.ETF_LIST


class ETFPerformanceView(FMPBaseView):
    """
    Return performance information for a given ETF symbol.

    App path:
        /api/v1/etf/{symbol}/performance/

    Provider path:
        /stable/etf/info

    Parameters:
        symbol (str): ETF ticker.
    """

    endpoint_from = EndpointFrom.ETF_PERFORMANCE
    endpoint_to = EndpointTo.FMP.ETF_PERFORMANCE
    allowed_params = FMPParams.ETFPerformance


class ForexPairView(FMPBaseView):
    """
    Return historical price series for a foreign exchange pair.

    App path:
        /api/v1/forex/{pair}/

    Provider path:
        /stable/quote

    Parameters:
        pair (str): Forex pair, e.g., "EURUSD".
    """

    endpoint_from = EndpointFrom.FOREX_PAIR
    endpoint_to = EndpointTo.FMP.FOREX_PAIR
    allowed_params = FMPParams.ForexPair


class ForexRatesView(FMPBaseView):
    """
    Return current foreign exchange rates.

    App path:
        /api/v1/forex/rates/

    Provider path:
        /stable/forex-list

    Parameters:
        Forwards any query parameters to the provider unmodified.
    """

    endpoint_from = EndpointFrom.FOREX_RATES
    endpoint_to = EndpointTo.FMP.FOREX_RATES


#
# class GDPView(FMPBaseView):
#     """
#     Return GDP series by name filter.
#
#     App path:
#         /api/v1/economy/gdp/
#
#     Provider path:
#         /stable/economic-indicators
#
#     Parameters:
#         name (str): Economic series name, e.g., "GDP".
#     """
#     endpoint_from = EndpointFrom.ECONOMY_GDP
#     endpoint_to = EndpointTo.FMP.ECO_INDICATORS


# class HistoricalDividendsView(FMPBaseView):
#     """
#     Return historical dividend events for a ticker.
#
#     App path:
#         /api/v1/historical/{symbol}/dividends/
#
#     Provider path:
#         /v3/historical-price-full/stock_dividend/{symbol}
#
#     Parameters:
#         symbol (str): Ticker symbol.
#     """
#     # COMMENTED: DUPLICATE - Use STOCKS_REFERENCE_DIVIDENDS from Polygon
#     # endpoint_from = EndpointFrom.HISTORICAL_DIVIDENDS
#     # endpoint_to = EndpointTo.FMP.HISTORICAL_DIVIDENDS


class HistoricalIntradayView(FMPBaseView):
    """
    Fetch intraday bar series for a ticker at a given interval.

    App path:
        /api/v1/historical/{symbol}/intraday/

    Provider path:
        /stable/historical-chart

    Parameters:
        symbol (str): Ticker symbol.
        interval (str): Bar interval, e.g., "1min", "5min".

    Examples:
        /api/v1/historical/AAPL/intraday/?from=2024-01-01
        /api/v1/historical/AAPL/intraday/?to=2024-01-02
    """

    endpoint_from = EndpointFrom.HISTORICAL_INTRADAY
    endpoint_to = EndpointTo.FMP.HISTORICAL_INTRADAY
    allowed_params = FMPParams.HistoricalIntraday


# class HistoricalSplitsView(FMPBaseView):
#     """
#     Return historical split events for a ticker.
#
#     App path:
#         /api/v1/historical/{symbol}/splits/
#
#     Provider path:
#         /v3/historical-price-full/stock_split/{symbol}
#
#     Parameters:
#         symbol (str): Ticker symbol.
#     """
#     # COMMENTED: DUPLICATE - Use STOCKS_REFERENCE_SPLITS from Polygon
#     # endpoint_from = EndpointFrom.HISTORICAL_SPLITS
#     # endpoint_to = EndpointTo.FMP.HISTORICAL_SPLITS


# class HistoricalView(FMPBaseView):
#     """
#     Fetch end-of-day historical price series for a ticker.
#
#     App path:
#         /api/v1/historical/{symbol}/
#
#     Provider path:
#         /v3/historical-price-full/{symbol}
#
#     Parameters:
#         symbol (str): Ticker symbol.
#     """
#     # COMMENTED: SIMILAR - Use STOCKS_AGGREGATE_CUSTOM_RANGE from Polygon
#     # endpoint_from = EndpointFrom.HISTORICAL
#     # endpoint_to = EndpointTo.FMP.HISTORICAL
#     # allowed_params = FMPParams.HistoricalRange


class IncomeStatementView(FMPBaseView):
    """
    Retrieve income statement data for a company.

    App path:
        /api/v1/fundamentals/{symbol}/income-statement/

    Provider path:
        /stable/income-statement

    Parameters:
        symbol (str): Ticker symbol.
    """

    endpoint_from = EndpointFrom.FUNDAMENTALS_INCOME_STATEMENT
    endpoint_to = EndpointTo.FMP.FUND_IS
    allowed_params = FMPParams.IncomeStatement


class InflationView(FMPBaseView):
    """
    Return CPI/inflation series by name.

    App path:
        /api/v1/economy/{name}/inflation/

    Provider path:
        /stable/economic-indicators

    Parameters:
        name (str): Series name, e.g., "CPIAUCSL".
    """

    endpoint_from = EndpointFrom.ECONOMY_INFLATION
    endpoint_to = EndpointTo.FMP.ECO_INDICATORS
    allowed_params = FMPParams.EconomicIndicators


class InsiderTradingView(FMPBaseView):
    """
    Return reported insider transactions for a company.

    App path:
        /api/v1/institutional/{symbol}/insider-trading/

    Provider path:
        /stable/insider-trading/search

    Parameters:
        symbol (str): Ticker symbol. Forwards other query params.
    """

    endpoint_from = EndpointFrom.INSTITUTIONAL_INSIDER_TRADING
    endpoint_to = EndpointTo.FMP.INST_INSIDER
    allowed_params = FMPParams.InsiderTrading


class InstitutionalHoldersView(FMPBaseView):
    """
    Return institutional shareholder positions for a company.

    App path:
        /api/v1/institutional/{symbol}/holders/

    Provider path:
        /stable/institutional-ownership/extract-analytics/holder

    Parameters:
        symbol (str): Ticker symbol.
    """

    endpoint_from = EndpointFrom.INSTITUTIONAL_HOLDERS
    endpoint_to = EndpointTo.FMP.INST_HOLDERS
    allowed_params = FMPParams.InstitutionalHolders


class InternationalExchangesView(FMPBaseView):
    """
    List international exchanges supported by the provider.

    App path:
        /api/v1/international/exchanges/

    Provider path:
        /stable/available-exchanges

    Parameters:
        Forwards any query parameters to the provider unmodified.
    """

    endpoint_from = EndpointFrom.INTERNATIONAL_EXCHANGES
    endpoint_to = EndpointTo.FMP.INT_EXCHANGES


class InternationalStocksView(FMPBaseView):
    """
    List stocks listed on an international exchange.

    App path:
        /api/v1/international/{exchange}/stocks/

    Provider path:
        /stable/stock-list

    Parameters:
        exchange (str): Exchange code.
    """

    endpoint_from = EndpointFrom.INTERNATIONAL_STOCKS
    endpoint_to = EndpointTo.FMP.INT_STOCKS


# class IPOCalendarView(FMPBaseView):
#     """
#     List upcoming initial public offerings.
#
#     App path:
#         /api/v1/events/ipo-calendar/
#
#     Provider path:
#         /v3/ipo_calendar
#
#     Parameters:
#         Forwards any query parameters to the provider unmodified.
#     """
#     # COMMENTED: DUPLICATE - Use STOCKS_REFERENCE_IPOS from Polygon
#     # endpoint_from = EndpointFrom.EVENTS_IPO
#     # endpoint_to = EndpointTo.FMP.EVENTS_IPO


# class LosersView(FMPBaseView):
#     """
#     List top market losers for the current session.
#
#     App path:
#         /api/v1/quotes/losers/
#
#     Provider path:
#         /v3/losers
#
#     Parameters:
#         Forwards any query parameters to the provider unmodified.
#     """
#     # COMMENTED: SIMILAR - Use STOCKS_SNAPSHOT_MOVERS from Polygon
#     # endpoint_from = EndpointFrom.QUOTES_LOSERS
#     # endpoint_to = EndpointTo.FMP.QUOTES_LOSERS


class MetricsView(FMPBaseView):
    """
    Return key financial and operating metrics for a company.

    App path:
        /api/v1/fundamentals/{symbol}/metrics/

    Provider path:
        /stable/key-metrics

    Parameters:
        symbol (str): Ticker symbol.
    """

    endpoint_from = EndpointFrom.FUNDAMENTALS_METRICS
    endpoint_to = EndpointTo.FMP.FUND_METRICS
    allowed_params = FMPParams.KeyMetrics


# class MostActiveView(FMPBaseView):
#     """
#     List most actively traded tickers by volume.
#
#     App path:
#         /api/v1/quotes/most-active/
#
#     Provider path:
#         /v3/actives
#
#     Parameters:
#         Forwards any query parameters to the provider unmodified.
#     """
#     # COMMENTED: SIMILAR - Use STOCKS_SNAPSHOT_MOVERS from Polygon
#     # endpoint_from = EndpointFrom.QUOTES_MOST_ACTIVE
#     # endpoint_to = EndpointTo.FMP.QUOTES_MOST_ACTIVE


# class NewsSentimentView(FMPBaseView):
#     """
#     Return historical social sentiment series.
#
#     App path:
#         /api/v1/news/sentiment/
#
#     Provider path:
#         /v4/historical/social-sentiment
#
#     Parameters:
#         Forwards any query parameters to the provider unmodified.
#     """
#     endpoint_from = EndpointFrom.NEWS_SENTIMENT
#     endpoint_to = EndpointTo.FMP.NEWS_SENTIMENT


# class NewsSymbolView(FMPBaseView):
#     """
#     Return latest news filtered by ticker symbol.
#
#     App path:
#         /api/v1/news/{symbol}/
#
#     Provider path:
#         /v3/stock_news
#
#     Parameters:
#         symbol (str): Ticker symbol.
#     """
#     endpoint_from = EndpointFrom.NEWS_SYMBOL
#     endpoint_to = EndpointTo.FMP.NEWS_SYMBOL


# class NewsView(FMPBaseView):
#     """
#     Return latest stock market news items.
#
#     App path:
#         /api/v1/news/
#
#     Provider path:
#         /v3/stock_news
#
#     Parameters:
#         Forwards any query parameters to the provider unmodified.
#     """
#     # COMMENTED: DUPLICATE - Use STOCKS_REFERENCE_NEWS from Polygon
#     # endpoint_from = EndpointFrom.NEWS
#     # endpoint_to = EndpointTo.FMP.NEWS


class PressReleasesSymbolView(FMPBaseView):
    """
    List press releases for a specific ticker.

    App path:
        /api/v1/news/{symbol}/press-releases/

    Provider path:
        /v3/press-releases/{symbol}

    Parameters:
        symbol (str): Ticker symbol.
    """

    endpoint_from = EndpointFrom.NEWS_SYMBOL_PRESS_RELEASES
    endpoint_to = EndpointTo.FMP.NEWS_SYMBOL_PR
    allowed_params = FMPParams.PressReleasesSymbol


class PressReleasesView(FMPBaseView):
    """
    List recent press releases.

    App path:
        /api/v1/news/press-releases/

    Provider path:
        /v3/press-releases

    Parameters:
        Forwards any query parameters to the provider unmodified.
    """

    endpoint_from = EndpointFrom.NEWS_PRESS_RELEASES
    endpoint_to = EndpointTo.FMP.NEWS_PR
    allowed_params = FMPParams.PressReleases


class QuoteBatchView(FMPBaseView):
    """
    Return real-time quotes for multiple tickers.

    App path:
        /api/v1/quotes/batch/

    Provider path:
        /stable/batch-quote

    Parameters:
        symbols (str): Comma-separated ticker list, e.g., "AAPL,MSFT".
    """

    endpoint_from = EndpointFrom.QUOTES_BATCH
    endpoint_to = EndpointTo.FMP.QUOTES_BATCH
    allowed_params = FMPParams.QuoteBatch


# class QuoteView(FMPBaseView):
#     """
#     Return the latest real-time quote for a ticker.
#
#     App path:
#         /api/v1/quotes/{symbol}/
#
#     Provider path:
#         /v3/quote/{symbol}
#
#     Parameters:
#         symbol (str): Ticker symbol.
#     """
#     # COMMENTED: SIMILAR - Use STOCKS_QUOTES from Polygon
#     # endpoint_from = EndpointFrom.QUOTES_SINGLE
#     # endpoint_to = EndpointTo.FMP.QUOTES_SINGLE


# class ReferenceExchangesView(FMPBaseView):
#     """
#     List supported stock exchanges.
#
#     App path:
#         /api/v1/reference/exchanges/
#
#     Provider path:
#         /v3/exchanges-list
#
#     Parameters:
#         Forwards any query parameters to the provider unmodified.
#     """
#     # COMMENTED: DUPLICATE - Use STOCKS_REFERENCE_EXCHANGES from Polygon
#     # endpoint_from = EndpointFrom.REFERENCE_EXCHANGES
#     # endpoint_to = EndpointTo.FMP.REFERENCE_EXCHANGES


class ReferenceMarketCapView(FMPBaseView):
    """
    Retrieve historical market capitalization for a ticker.

    App path:
        /api/v1/reference/market-cap/{symbol}/

    Provider path:
        /stable/market-capitalization

    Parameters:
        symbol (str): Ticker symbol.
    """

    endpoint_from = EndpointFrom.REFERENCE_MARKET_CAP
    endpoint_to = EndpointTo.FMP.REFERENCE_MARKET_CAP
    allowed_params = FMPParams.MarketCapitalization


# class ReferenceTickerExecutivesView(FMPBaseView):
#     """
#     List key executives for a company by symbol.
#
#     App path:
#         /api/v1/reference/ticker/{symbol}/executives/
#
#     Provider path:
#         /v3/key-executives/{symbol}
#
#     Parameters:
#         symbol (str): Ticker symbol.
#     """
#     # COMMENTED: INTERNAL DUPLICATE - Use COMPANY_EXECUTIVES
#     # endpoint_from = EndpointFrom.REFERENCE_TICKER_EXECUTIVES
#     # endpoint_to = EndpointTo.FMP.REFERENCE_TICKER_EXECUTIVES


# class ReferenceTickerOutlookView(FMPBaseView):
#     """
#     Retrieve a company's outlook including qualitative and quantitative metrics.
#
#     App path:
#         /api/v1/reference/ticker/{symbol}/outlook/
#
#     Provider path:
#         /v4/company-outlook
#
#     Parameters:
#         symbol (str): Ticker symbol.
#     """
#     endpoint_from = EndpointFrom.REFERENCE_TICKER_OUTLOOK
#     endpoint_to = EndpointTo.FMP.REFERENCE_TICKER_OUTLOOK


# class ReferenceTickerProfileView(FMPBaseView):
#     """
#     Retrieve detailed company profile information by symbol.
#
#     App path:
#         /api/v1/reference/ticker/{symbol}/profile/
#
#     Provider path:
#         /v3/profile/{symbol}
#
#     Parameters:
#         symbol (str): Ticker symbol.
#     """
#     # COMMENTED: INTERNAL DUPLICATE - Use REFERENCE_TICKER
#     # endpoint_from = EndpointFrom.REFERENCE_TICKER_PROFILE
#     # endpoint_to = EndpointTo.FMP.REFERENCE_TICKER_PROFILE


# class ReferenceTickerView(FMPBaseView):
#     """
#     Retrieve a company's basic reference profile by symbol.
#
#     App path:
#         /api/v1/reference/ticker/{symbol}/
#
#     Provider path:
#         /v3/profile/{symbol}
#
#     Parameters:
#         symbol (str): Ticker symbol, e.g., "AAPL".
#     """
#     # COMMENTED: SIMILAR - Use STOCKS_REFERENCE_TICKER from Polygon
#     # endpoint_from = EndpointFrom.REFERENCE_TICKER
#     # endpoint_to = EndpointTo.FMP.REFERENCE_TICKER


# class ReferenceTickersView(FMPBaseView):
#     """
#     List reference tickers available from the provider.
#
#     App path:
#         /api/v1/reference/tickers/
#
#     Provider path:
#         /v3/stock/list
#
#     Parameters:
#         Forwards any query parameters to the provider unmodified.
#     """
#     endpoint_from = EndpointFrom.REFERENCE_TICKERS
#     endpoint_to = EndpointTo.FMP.REFERENCE_TICKERS


class ScreenerView(FMPBaseView):
    """
    Screen stocks using provider-supported criteria.

    App path:
        /api/v1/fundamentals/screener/

    Provider path:
        /stable/company-screener

    Parameters:
        Forwards any query parameters to the provider unmodified.
    """

    endpoint_from = EndpointFrom.FUNDAMENTALS_SCREENER
    endpoint_to = EndpointTo.FMP.FUND_SCREENER
    allowed_params = FMPParams.CompanyScreenerStable


class SECFilingsView(FMPBaseView):
    """
    Return SEC filings for a company (10-K, 10-Q, etc.).

    App path:
        /api/v1/sec/{symbol}/filings/

    Provider path:
        /stable/sec-filings-search/symbol

    Parameters:
        symbol (str): Ticker symbol. Forwards other query params.
    """

    endpoint_from = EndpointFrom.SEC_FILINGS
    endpoint_to = EndpointTo.FMP.SEC_FILINGS
    allowed_params = FMPParams.SECFilings


# class SEC10KView(FMPBaseView):
#     """
#     Return 10-K (annual) filings for a company.
#
#     App path:
#         /api/v1/sec/{symbol}/10k/
#
#     Provider path:
#         /v3/sec_filings/{symbol}
#
#     Parameters:
#         symbol (str): Ticker symbol. Filing type selected upstream.
#     """
#     endpoint_from = EndpointFrom.SEC_10K
#     endpoint_to = EndpointTo.FMP.SEC_10K
#
#
# class SEC10QView(FMPBaseView):
#     """
#     Return 10-Q (quarterly) filings for a company.
#
#     App path:
#         /api/v1/sec/{symbol}/10q/
#
#     Provider path:
#         /v3/sec_filings/{symbol}
#
#     Parameters:
#         symbol (str): Ticker symbol. Filing type selected upstream.
#     """
#     endpoint_from = EndpointFrom.SEC_10Q
#     endpoint_to = EndpointTo.FMP.SEC_10Q
#
#
# class SEC8KView(FMPBaseView):
#     """
#     Return 8-K (current event) filings for a company.
#
#     App path:
#         /api/v1/sec/{symbol}/8k/
#
#     Provider path:
#         /v3/sec_filings/{symbol}
#
#     Parameters:
#         symbol (str): Ticker symbol. Filing type selected upstream.
#     """
#     endpoint_from = EndpointFrom.SEC_8K
#     endpoint_to = EndpointTo.FMP.SEC_8K


# class SECRSSFeedView(FMPBaseView):
#     """
#     Return the SEC RSS feed items.
#
#     App path:
#         /api/v1/sec/rss-feed/
#
#     Provider path:
#         /v4/rss_feed
#
#     Parameters:
#         Forwards any query parameters to the provider unmodified.
#     """
#     endpoint_from = EndpointFrom.SEC_RSS
#     endpoint_to = EndpointTo.FMP.SEC_RSS


class ThirteenFView(FMPBaseView):
    """
    Return institutional 13F filings for a company.

    App path:
        /api/v1/institutional/{symbol}/13f/

    Provider path:
        /stable/institutional-ownership/symbol-positions-summary

    Parameters:
        symbol (str): Ticker symbol.
    """

    endpoint_from = EndpointFrom.INSTITUTIONAL_13F
    endpoint_to = EndpointTo.FMP.INST_13F
    allowed_params = FMPParams.ThirteenFFilings


class TreasuryRatesView(FMPBaseView):
    """
    Return treasury yield curve and related rates.

    App path:
        /api/v1/economy/treasury-rates/

    Provider path:
        /stable/treasury-rates

    Parameters:
        Forwards any query parameters to the provider unmodified.
    """

    endpoint_from = EndpointFrom.ECONOMY_TREASURY_RATES
    endpoint_to = EndpointTo.FMP.ECO_TREASURY
    allowed_params = FMPParams.TreasuryRates


# class UnemploymentView(FMPBaseView):
#     """
#     Return unemployment rate series by name.
#
#     App path:
#         /api/v1/economy/unemployment/
#
#     Provider path:
#         /stable/economic-indicators
#
#     Parameters:
#         name (str): Series name, e.g., "UNRATE".
#     """
#     endpoint_from = EndpointFrom.ECONOMY_UNEMPLOYMENT
#     endpoint_to = EndpointTo.FMP.ECO_INDICATORS
#     allowed_params = FMPParams.Unemployment


class CompanyExecutivesView(FMPBaseView):
    """
    List company executives by ticker symbol, directly proxying to FMP and returning the provider JSON.

    App path:
        /api/v1/reference/ticker/{symbol}/company-executives/

    Provider path:
        /stable/key-executives

    Path parameters:
        symbol (str): Target ticker symbol.

    GET Parameters:
        None. Additional query parameters are forwarded unchanged.
    """

    endpoint_from = EndpointFrom.COMPANY_EXECUTIVES
    endpoint_to = EndpointTo.FMP.COMPANY_EXECUTIVES
    allowed_params = FMPParams.CompanyExecutives


# same view as ScreenerView
# class CompanyScreenerStableView(FMPBaseView):
#     """
#     Screen companies using the stable screener endpoint, forwarding filters to FMP and returning raw results.
#
#     App path:
#         /api/v1/fundamentals/screener/stable/
#
#     Provider path:
#         /stable/company-screener
#
#     Path parameters:
#         None.
#
#     GET Parameters:
#         Any screener filter supported by FMP. All parameters are forwarded unchanged.
#
#     Examples:
#         /api/v1/fundamentals/screener/stable/?sector=Technology
#         /api/v1/fundamentals/screener/stable/?marketCapMoreThan=1000000000
#         /api/v1/fundamentals/screener/stable/?isActivelyTrading=true
#     """
#     endpoint_from = EndpointFrom.COMPANY_SCREENER_STABLE
#     endpoint_to = EndpointTo.FMP.COMPANY_SCREENER_STABLE
#     allowed_params = FMPParams.CompanyScreenerStable


class EmployeeCountHistoricalView(FMPBaseView):
    """
    Return historical employee count entries for a company using FMP v4 endpoints.

    App path:
        /api/v1/reference/ticker/{symbol}/employee-count/historical/

    Provider path:
        /stable/historical-employee-count

    Path parameters:
        symbol (str): Target ticker symbol.

    GET Parameters:
        None. Additional query parameters are forwarded unchanged.
    """

    endpoint_from = EndpointFrom.EMPLOYEE_COUNT_HISTORICAL
    endpoint_to = EndpointTo.FMP.EMPLOYEE_COUNT_HISTORICAL
    allowed_params = FMPParams.EmployeeCountHistorical


class EmployeeCountView(FMPBaseView):
    """
    Return the most recent employee count for a company via FMP v4 endpoint.

    App path:
        /api/v1/reference/ticker/{symbol}/employee-count/

    Provider path:
        /stable/employee_count

    Path parameters:
        symbol (str): Target ticker symbol.

    GET Parameters:
        None. Additional query parameters are forwarded unchanged.
    """

    endpoint_from = EndpointFrom.EMPLOYEE_COUNT
    endpoint_to = EndpointTo.FMP.EMPLOYEE_COUNT
    allowed_params = FMPParams.EmployeeCount


class ExecutiveCompensationBenchmarkView(FMPBaseView):
    """
    Benchmark executive compensation for similar companies using FMP's benchmarking endpoint.

    App path:
        /api/v1/corporate/executive-compensation/benchmark/

    Provider path:
        /stable/executive-compensation-benchmark

    Path parameters:
        None.

    GET Parameters:
        year (int): Four-digit year to filter compensation records.

    Examples:
        /api/v1/corporate/executive-compensation/benchmark/?symbol=AAPL
    """

    endpoint_from = EndpointFrom.EXEC_COMP_BENCHMARK
    endpoint_to = EndpointTo.FMP.EXEC_COMP_BENCHMARK
    allowed_params = FMPParams.ExecutiveCompensationBenchmark


class ExecutiveCompensationView(FMPBaseView):
    """
    Return executive compensation records for a company and year directly from FMP.

    App path:
        /api/v1/corporate/executive-compensation/

    Provider path:
        /stable/governance-executive-compensation

    Path parameters:
        None.

    GET Parameters:
        symbol (str): Target ticker symbol.

    Examples:
        /api/v1/corporate/executive-compensation/?symbol=AAPL
    """

    endpoint_from = EndpointFrom.EXEC_COMP
    endpoint_to = EndpointTo.FMP.EXEC_COMP
    allowed_params = FMPParams.ExecutiveCompensation


class ExchangeVariantsView(FMPBaseView):
    """
    Return exchange variants for a given symbol across exchanges using FMP stable search.

    App path:
        /api/v1/reference/exchange-variants/

    Provider path:
        /stable/search-exchange-variants?symbol={symbol}

    Path parameters:
        None.

    GET Parameters:
        symbol (str): Base ticker symbol to search variants for.

    Examples:
        /api/v1/reference/exchange-variants/?symbol=AAPL
    """

    endpoint_from = EndpointFrom.EXCHANGE_VARIANTS
    endpoint_to = EndpointTo.FMP.EXCHANGE_VARIANTS
    allowed_params = FMPParams.ExchangeVariants


class MergersAcquisitionsSearchView(FMPBaseView):
    """
    Search mergers and acquisitions by keyword using FMP v4 search endpoint.

    App path:
        /api/v1/corporate/mergers-acquisitions/search/

    Provider path:
        /stable/mergers-acquisitions-search

    Path parameters:
        None.

    GET Parameters:
        query (str): Search keyword to match M&A entries.
        page (int): Optional page number (0-based).

    Examples:
        /api/v1/corporate/mergers-acquisitions/search/?query=Apple
        /api/v1/corporate/mergers-acquisitions/search/?page=2
    """

    endpoint_from = EndpointFrom.MERGERS_ACQUISITIONS_SEARCH
    endpoint_to = EndpointTo.FMP.MERGERS_ACQUISITIONS_SEARCH
    allowed_params = FMPParams.MergersAcquisitionsSearch


class MergersAcquisitionsView(FMPBaseView):
    """
    Return the latest mergers and acquisitions feed with optional pagination.

    App path:
        /api/v1/corporate/mergers-acquisitions/

    Provider path:
        /stable/mergers-acquisitions-latest

    Path parameters:
        None.

    GET Parameters:
        page (int): Optional page number (default 0).

    Examples:
        /api/v1/corporate/mergers-acquisitions/?page=3
    """

    endpoint_from = EndpointFrom.MERGERS_ACQUISITIONS
    endpoint_to = EndpointTo.FMP.MERGERS_ACQUISITIONS
    allowed_params = FMPParams.MergersAcquisitions


class SearchCIKView(FMPBaseView):
    """
    Search companies by SEC CIK identifier using FMP stable search endpoint.

    App path:
        /api/v1/reference/search/cik/

    Provider path:
        /stable/search-cik?cik={cik}

    Path parameters:
        None.

    GET Parameters:
        cik (str): SEC Central Index Key.

    Examples:
        /api/v1/reference/search/cik/?cik=0000320193
    """

    endpoint_from = EndpointFrom.SEARCH_CIK
    endpoint_to = EndpointTo.FMP.SEARCH_CIK
    allowed_params = FMPParams.SearchCIK


class SearchCUSIPView(FMPBaseView):
    """
    Search securities by CUSIP code using FMP stable search endpoint.

    App path:
        /api/v1/reference/search/cusip/

    Provider path:
        /stable/search-cusip?cusip={cusip}

    Path parameters:
        None.

    GET Parameters:
        cusip (str): CUSIP security identifier.

    Examples:
        /api/v1/reference/search/cusip/?cusip=037833100
    """

    endpoint_from = EndpointFrom.SEARCH_CUSIP
    endpoint_to = EndpointTo.FMP.SEARCH_CUSIP
    allowed_params = FMPParams.SearchCUSIP


class SearchISINView(FMPBaseView):
    """
    Search securities by ISIN using FMP stable search endpoint.

    App path:
        /api/v1/reference/search/isin/

    Provider path:
        /stable/search-isin?isin={isin}

    Path parameters:
        None.

    GET Parameters:
        isin (str): International Securities Identification Number.

    Examples:
        /api/v1/reference/search/isin/?isin=US0378331005
    """

    endpoint_from = EndpointFrom.SEARCH_ISIN
    endpoint_to = EndpointTo.FMP.SEARCH_ISIN
    allowed_params = FMPParams.SearchISIN


class SharesFloatAllView(FMPBaseView):
    """
    Return shares float data for all tickers available via FMP.

    App path:
        /api/v1/reference/shares-float/all/

    Provider path:
        /stable/shares_float_all

    Path parameters:
        None.

    GET Parameters:
        None. Additional query parameters are forwarded unchanged.
    """

    endpoint_from = EndpointFrom.SHARES_FLOAT_ALL
    endpoint_to = EndpointTo.FMP.SHARES_FLOAT_ALL
    allowed_params = FMPParams.SharesFloatAll


class SharesFloatView(FMPBaseView):
    """
    Return shares float and outstanding shares for a specific ticker.

    App path:
        /api/v1/reference/ticker/{symbol}/shares-float/

    Provider path:
        /stable/shares_float

    Path parameters:
        symbol (str): Target ticker symbol.

    GET Parameters:
        None. Additional query parameters are forwarded unchanged.
    """

    endpoint_from = EndpointFrom.SHARES_FLOAT
    endpoint_to = EndpointTo.FMP.SHARES_FLOAT
    allowed_params = FMPParams.SharesFloat


class SymbolChangeView(FMPBaseView):
    """
    List recent stock symbol changes as provided by FMP stable endpoint.

    App path:
        /api/v1/reference/symbol-change/

    Provider path:
        /stable/symbol-change

    Path parameters:
        None.

    GET Parameters:
        None. Additional query parameters are forwarded unchanged.
    """

    endpoint_from = EndpointFrom.SYMBOL_CHANGE
    endpoint_to = EndpointTo.FMP.SYMBOL_CHANGE
    allowed_params = FMPParams.SymbolChange


class ExampleFMPGainersView(FMPBaseView):
    """
    Demonstration endpoint showcasing auth, pagination, and query validation using FMP gainers list.

    App path:
        /api/v1/examples/fmp/gainers/

    Provider path:
        /v3/gainers

    Path parameters:
        None.

    GET Parameters:
        limit (int): Max items per page.
        page (int): Page number (1-based).
        market (str): Market filter, "stocks" or "etf".
    """

    active = True
    authentication_classes = [JWTAuthentication, RequestTokenAuthentication]
    endpoint_from = EndpointFrom.EXAMPLE_FMP_GAINERS
    endpoint_to = EndpointTo.FMP.QUOTES_GAINERS
    name = "example_fmp_gainers"
    pagination_class = PageNumberPagination
    permission_classes = [IsAuthenticated, DailyLimitPermission]
    timeout = 15.0

    class QuerySerializer(serializers.Serializer):
        limit = serializers.IntegerField(min_value=1, max_value=1000, required=False, default=50)
        page = serializers.IntegerField(min_value=1, required=False, default=1)
        market = serializers.ChoiceField(choices=["stocks", "etf"], required=False)

    serializer_class = QuerySerializer
