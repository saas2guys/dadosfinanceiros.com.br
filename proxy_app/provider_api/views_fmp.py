from __future__ import annotations

from .base import FMPBaseView
from .enums import CommonParams, EconomicParams, EndpointFrom, EndpointToFMP, NewsParams


class ReferenceTickersView(FMPBaseView):
    endpoint_from = EndpointFrom.REFERENCE_TICKERS.value
    endpoint_to = EndpointToFMP.REFERENCE_TICKERS.value


class ReferenceTickerView(FMPBaseView):
    endpoint_from = EndpointFrom.REFERENCE_TICKER.value
    endpoint_to = EndpointToFMP.REFERENCE_TICKER.value


class ReferenceTickerProfileView(FMPBaseView):
    endpoint_from = EndpointFrom.REFERENCE_TICKER_PROFILE.value
    endpoint_to = EndpointToFMP.REFERENCE_TICKER_PROFILE.value


class ReferenceTickerExecutivesView(FMPBaseView):
    endpoint_from = EndpointFrom.REFERENCE_TICKER_EXECUTIVES.value
    endpoint_to = EndpointToFMP.REFERENCE_TICKER_EXECUTIVES.value


class ReferenceTickerOutlookView(FMPBaseView):
    endpoint_from = EndpointFrom.REFERENCE_TICKER_OUTLOOK.value
    endpoint_to = EndpointToFMP.REFERENCE_TICKER_OUTLOOK.value


class ReferenceExchangesView(FMPBaseView):
    endpoint_from = EndpointFrom.REFERENCE_EXCHANGES.value
    endpoint_to = EndpointToFMP.REFERENCE_EXCHANGES.value


class ReferenceMarketCapView(FMPBaseView):
    endpoint_from = EndpointFrom.REFERENCE_MARKET_CAP.value
    endpoint_to = EndpointToFMP.REFERENCE_MARKET_CAP.value


class QuoteView(FMPBaseView):
    endpoint_from = EndpointFrom.QUOTES_SINGLE.value
    endpoint_to = EndpointToFMP.QUOTES_SINGLE.value


class QuoteBatchView(FMPBaseView):
    endpoint_from = EndpointFrom.QUOTES_BATCH.value
    endpoint_to = EndpointToFMP.QUOTES_BATCH.value


class GainersView(FMPBaseView):
    endpoint_from = EndpointFrom.QUOTES_GAINERS.value
    endpoint_to = EndpointToFMP.QUOTES_GAINERS.value
    allowed_params = CommonParams


class LosersView(FMPBaseView):
    endpoint_from = EndpointFrom.QUOTES_LOSERS.value
    endpoint_to = EndpointToFMP.QUOTES_LOSERS.value
    allowed_params = CommonParams


class MostActiveView(FMPBaseView):
    endpoint_from = EndpointFrom.QUOTES_MOST_ACTIVE.value
    endpoint_to = EndpointToFMP.QUOTES_MOST_ACTIVE.value
    allowed_params = CommonParams


class HistoricalView(FMPBaseView):
    endpoint_from = EndpointFrom.HISTORICAL.value
    endpoint_to = EndpointToFMP.HISTORICAL.value


class HistoricalIntradayView(FMPBaseView):
    endpoint_from = EndpointFrom.HISTORICAL_INTRADAY.value
    endpoint_to = EndpointToFMP.HISTORICAL_INTRADAY.value
    allowed_params = CommonParams


class HistoricalDividendsView(FMPBaseView):
    endpoint_from = EndpointFrom.HISTORICAL_DIVIDENDS.value
    endpoint_to = EndpointToFMP.HISTORICAL_DIVIDENDS.value


class HistoricalSplitsView(FMPBaseView):
    endpoint_from = EndpointFrom.HISTORICAL_SPLITS.value
    endpoint_to = EndpointToFMP.HISTORICAL_SPLITS.value


class IncomeStatementView(FMPBaseView):
    endpoint_from = EndpointFrom.FUND_IS.value
    endpoint_to = EndpointToFMP.FUND_IS.value


class BalanceSheetView(FMPBaseView):
    endpoint_from = EndpointFrom.FUND_BS.value
    endpoint_to = EndpointToFMP.FUND_BS.value


class CashFlowView(FMPBaseView):
    endpoint_from = EndpointFrom.FUND_CF.value
    endpoint_to = EndpointToFMP.FUND_CF.value


class RatiosView(FMPBaseView):
    endpoint_from = EndpointFrom.FUND_RATIOS.value
    endpoint_to = EndpointToFMP.FUND_RATIOS.value


class DCFView(FMPBaseView):
    endpoint_from = EndpointFrom.FUND_DCF.value
    endpoint_to = EndpointToFMP.FUND_DCF.value


class MetricsView(FMPBaseView):
    endpoint_from = EndpointFrom.FUND_METRICS.value
    endpoint_to = EndpointToFMP.FUND_METRICS.value


class EnterpriseValueView(FMPBaseView):
    endpoint_from = EndpointFrom.FUND_EV.value
    endpoint_to = EndpointToFMP.FUND_EV.value


class ScreenerView(FMPBaseView):
    endpoint_from = EndpointFrom.FUND_SCREENER.value
    endpoint_to = EndpointToFMP.FUND_SCREENER.value
    allowed_params = CommonParams


class NewsView(FMPBaseView):
    endpoint_from = EndpointFrom.NEWS.value
    endpoint_to = EndpointToFMP.NEWS.value
    allowed_params = CommonParams


class NewsSymbolView(FMPBaseView):
    endpoint_from = EndpointFrom.NEWS_SYMBOL.value
    endpoint_to = EndpointToFMP.NEWS_SYMBOL.value
    allowed_params = NewsParams


class PressReleasesView(FMPBaseView):
    endpoint_from = EndpointFrom.NEWS_PR.value
    endpoint_to = EndpointToFMP.NEWS_PR.value


class PressReleasesSymbolView(FMPBaseView):
    endpoint_from = EndpointFrom.NEWS_SYMBOL_PR.value
    endpoint_to = EndpointToFMP.NEWS_SYMBOL_PR.value


class NewsSentimentView(FMPBaseView):
    endpoint_from = EndpointFrom.NEWS_SENTIMENT.value
    endpoint_to = EndpointToFMP.NEWS_SENTIMENT.value


class AnalystEstimatesView(FMPBaseView):
    endpoint_from = EndpointFrom.ANALYST_EST.value
    endpoint_to = EndpointToFMP.ANALYST_EST.value


class AnalystRecommendationsView(FMPBaseView):
    endpoint_from = EndpointFrom.ANALYST_RECO.value
    endpoint_to = EndpointToFMP.ANALYST_RECO.value


class AnalystPriceTargetsView(FMPBaseView):
    endpoint_from = EndpointFrom.ANALYST_PRICE_TARGETS.value
    endpoint_to = EndpointToFMP.ANALYST_PRICE_TARGETS.value
    allowed_params = CommonParams


class AnalystUpgradesDowngradesView(FMPBaseView):
    endpoint_from = EndpointFrom.ANALYST_UPGRADES.value
    endpoint_to = EndpointToFMP.ANALYST_UPGRADES.value
    allowed_params = CommonParams


class EarningsCalendarView(FMPBaseView):
    endpoint_from = EndpointFrom.EARNINGS_CAL.value
    endpoint_to = EndpointToFMP.EARNINGS_CAL.value
    allowed_params = CommonParams


class EarningsTranscriptsView(FMPBaseView):
    endpoint_from = EndpointFrom.EARNINGS_TRANSCRIPTS.value
    endpoint_to = EndpointToFMP.EARNINGS_TRANSCRIPTS.value


class EarningsHistoryView(FMPBaseView):
    endpoint_from = EndpointFrom.EARNINGS_HISTORY.value
    endpoint_to = EndpointToFMP.EARNINGS_HISTORY.value


class EarningsSurprisesView(FMPBaseView):
    endpoint_from = EndpointFrom.EARNINGS_SURPRISES.value
    endpoint_to = EndpointToFMP.EARNINGS_SURPRISES.value


class IPOCalendarView(FMPBaseView):
    endpoint_from = EndpointFrom.EVENTS_IPO.value
    endpoint_to = EndpointToFMP.EVENTS_IPO.value


class StockSplitCalendarView(FMPBaseView):
    endpoint_from = EndpointFrom.EVENTS_SPLIT.value
    endpoint_to = EndpointToFMP.EVENTS_SPLIT.value


class DividendCalendarView(FMPBaseView):
    endpoint_from = EndpointFrom.EVENTS_DIVIDEND.value
    endpoint_to = EndpointToFMP.EVENTS_DIVIDEND.value


class ThirteenFView(FMPBaseView):
    endpoint_from = EndpointFrom.INST_13F.value
    endpoint_to = EndpointToFMP.INST_13F.value


class InstitutionalHoldersView(FMPBaseView):
    endpoint_from = EndpointFrom.INST_HOLDERS.value
    endpoint_to = EndpointToFMP.INST_HOLDERS.value


class InsiderTradingView(FMPBaseView):
    endpoint_from = EndpointFrom.INST_INSIDER.value
    endpoint_to = EndpointToFMP.INST_INSIDER.value
    allowed_params = CommonParams


class SECFilingsView(FMPBaseView):
    endpoint_from = EndpointFrom.SEC_FILINGS.value
    endpoint_to = EndpointToFMP.SEC_FILINGS.value


class SEC10KView(FMPBaseView):
    endpoint_from = EndpointFrom.SEC_10K.value
    endpoint_to = EndpointToFMP.SEC_10K.value
    extra_query_params = {"type": "10-K"}


class SEC10QView(FMPBaseView):
    endpoint_from = EndpointFrom.SEC_10Q.value
    endpoint_to = EndpointToFMP.SEC_10Q.value
    extra_query_params = {"type": "10-Q"}


class SEC8KView(FMPBaseView):
    endpoint_from = EndpointFrom.SEC_8K.value
    endpoint_to = EndpointToFMP.SEC_8K.value
    extra_query_params = {"type": "8-K"}


class SECRSSFeedView(FMPBaseView):
    endpoint_from = EndpointFrom.SEC_RSS.value
    endpoint_to = EndpointToFMP.SEC_RSS.value


class GDPView(FMPBaseView):
    endpoint_from = EndpointFrom.ECO_GDP.value
    endpoint_to = EndpointToFMP.ECO_GDP.value
    allowed_params = EconomicParams


class InflationView(FMPBaseView):
    endpoint_from = EndpointFrom.ECO_CPI.value
    endpoint_to = EndpointToFMP.ECO_CPI.value
    allowed_params = EconomicParams


class UnemploymentView(FMPBaseView):
    endpoint_from = EndpointFrom.ECO_UNEMP.value
    endpoint_to = EndpointToFMP.ECO_UNEMP.value
    allowed_params = EconomicParams


class InterestRatesView(FMPBaseView):
    endpoint_from = EndpointFrom.ECO_RATES.value
    endpoint_to = EndpointToFMP.ECO_RATES.value
    allowed_params = EconomicParams


class TreasuryRatesView(FMPBaseView):
    endpoint_from = EndpointFrom.ECO_TREASURY.value
    endpoint_to = EndpointToFMP.ECO_TREASURY.value


class ETFListView(FMPBaseView):
    endpoint_from = EndpointFrom.ETF_LIST.value
    endpoint_to = EndpointToFMP.ETF_LIST.value


class ETFHoldingsView(FMPBaseView):
    endpoint_from = EndpointFrom.ETF_HOLDINGS.value
    endpoint_to = EndpointToFMP.ETF_HOLDINGS.value


class ETFPerformanceView(FMPBaseView):
    endpoint_from = EndpointFrom.ETF_PERF.value
    endpoint_to = EndpointToFMP.ETF_PERF.value


class MutualFundsListView(FMPBaseView):
    endpoint_from = EndpointFrom.MF_LIST.value
    endpoint_to = EndpointToFMP.MF_LIST.value


class CommoditiesMetalsView(FMPBaseView):
    endpoint_from = EndpointFrom.COM_METALS.value
    endpoint_to = EndpointToFMP.COM_QUOTES.value


class CommoditiesEnergyView(FMPBaseView):
    endpoint_from = EndpointFrom.COM_ENERGY.value
    endpoint_to = EndpointToFMP.COM_QUOTES.value


class CommoditiesAgriculturalView(FMPBaseView):
    endpoint_from = EndpointFrom.COM_AGRI.value
    endpoint_to = EndpointToFMP.COM_QUOTES.value


class CommoditiesHistoricalView(FMPBaseView):
    endpoint_from = EndpointFrom.COM_HIST.value
    endpoint_to = EndpointToFMP.COM_HIST.value


class CryptoListView(FMPBaseView):
    endpoint_from = EndpointFrom.CRYPTO_LIST.value
    endpoint_to = EndpointToFMP.CRYPTO_LIST.value


class CryptoQuoteView(FMPBaseView):
    endpoint_from = EndpointFrom.CRYPTO_QUOTE.value
    endpoint_to = EndpointToFMP.CRYPTO_QUOTE.value


class CryptoHistoricalView(FMPBaseView):
    endpoint_from = EndpointFrom.CRYPTO_HIST.value
    endpoint_to = EndpointToFMP.CRYPTO_HIST.value


class InternationalExchangesView(FMPBaseView):
    endpoint_from = EndpointFrom.INT_EXCHANGES.value
    endpoint_to = EndpointToFMP.INT_EXCHANGES.value


class InternationalStocksView(FMPBaseView):
    endpoint_from = EndpointFrom.INT_STOCKS.value
    endpoint_to = EndpointToFMP.INT_STOCKS.value


class ForexRatesView(FMPBaseView):
    endpoint_from = EndpointFrom.FOREX_RATES.value
    endpoint_to = EndpointToFMP.FOREX_RATES.value


class ForexPairView(FMPBaseView):
    endpoint_from = EndpointFrom.FOREX_PAIR.value
    endpoint_to = EndpointToFMP.FOREX_PAIR.value


