from __future__ import annotations

from .base import FMPBaseView
from .enums import CommonParams, EconomicParams, EndpointFrom, EndpointToFMP, NewsParams
from rest_framework import serializers
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication
from users.authentication import RequestTokenAuthentication
from users.permissions import DailyLimitPermission


class ReferenceTickersView(FMPBaseView):
    endpoint_from = EndpointFrom.REFERENCE_TICKERS
    endpoint_to = EndpointToFMP.REFERENCE_TICKERS


class ReferenceTickerView(FMPBaseView):
    endpoint_from = EndpointFrom.REFERENCE_TICKER
    endpoint_to = EndpointToFMP.REFERENCE_TICKER


class ReferenceTickerProfileView(FMPBaseView):
    endpoint_from = EndpointFrom.REFERENCE_TICKER_PROFILE
    endpoint_to = EndpointToFMP.REFERENCE_TICKER_PROFILE


class ReferenceTickerExecutivesView(FMPBaseView):
    endpoint_from = EndpointFrom.REFERENCE_TICKER_EXECUTIVES
    endpoint_to = EndpointToFMP.REFERENCE_TICKER_EXECUTIVES


class ReferenceTickerOutlookView(FMPBaseView):
    endpoint_from = EndpointFrom.REFERENCE_TICKER_OUTLOOK
    endpoint_to = EndpointToFMP.REFERENCE_TICKER_OUTLOOK


class ReferenceExchangesView(FMPBaseView):
    endpoint_from = EndpointFrom.REFERENCE_EXCHANGES
    endpoint_to = EndpointToFMP.REFERENCE_EXCHANGES


class ReferenceMarketCapView(FMPBaseView):
    endpoint_from = EndpointFrom.REFERENCE_MARKET_CAP
    endpoint_to = EndpointToFMP.REFERENCE_MARKET_CAP


class QuoteView(FMPBaseView):
    endpoint_from = EndpointFrom.QUOTES_SINGLE
    endpoint_to = EndpointToFMP.QUOTES_SINGLE


class QuoteBatchView(FMPBaseView):
    endpoint_from = EndpointFrom.QUOTES_BATCH
    endpoint_to = EndpointToFMP.QUOTES_BATCH


class GainersView(FMPBaseView):
    endpoint_from = EndpointFrom.QUOTES_GAINERS
    endpoint_to = EndpointToFMP.QUOTES_GAINERS


class LosersView(FMPBaseView):
    endpoint_from = EndpointFrom.QUOTES_LOSERS
    endpoint_to = EndpointToFMP.QUOTES_LOSERS


class MostActiveView(FMPBaseView):
    endpoint_from = EndpointFrom.QUOTES_MOST_ACTIVE
    endpoint_to = EndpointToFMP.QUOTES_MOST_ACTIVE


class HistoricalView(FMPBaseView):
    endpoint_from = EndpointFrom.HISTORICAL
    endpoint_to = EndpointToFMP.HISTORICAL


class HistoricalIntradayView(FMPBaseView):
    endpoint_from = EndpointFrom.HISTORICAL_INTRADAY
    endpoint_to = EndpointToFMP.HISTORICAL_INTRADAY


class HistoricalDividendsView(FMPBaseView):
    endpoint_from = EndpointFrom.HISTORICAL_DIVIDENDS
    endpoint_to = EndpointToFMP.HISTORICAL_DIVIDENDS


class HistoricalSplitsView(FMPBaseView):
    endpoint_from = EndpointFrom.HISTORICAL_SPLITS
    endpoint_to = EndpointToFMP.HISTORICAL_SPLITS


class IncomeStatementView(FMPBaseView):
    endpoint_from = EndpointFrom.FUND_IS
    endpoint_to = EndpointToFMP.FUND_IS


class BalanceSheetView(FMPBaseView):
    endpoint_from = EndpointFrom.FUND_BS
    endpoint_to = EndpointToFMP.FUND_BS


class CashFlowView(FMPBaseView):
    endpoint_from = EndpointFrom.FUND_CF
    endpoint_to = EndpointToFMP.FUND_CF


class RatiosView(FMPBaseView):
    endpoint_from = EndpointFrom.FUND_RATIOS
    endpoint_to = EndpointToFMP.FUND_RATIOS


class DCFView(FMPBaseView):
    endpoint_from = EndpointFrom.FUND_DCF
    endpoint_to = EndpointToFMP.FUND_DCF


class MetricsView(FMPBaseView):
    endpoint_from = EndpointFrom.FUND_METRICS
    endpoint_to = EndpointToFMP.FUND_METRICS


class EnterpriseValueView(FMPBaseView):
    endpoint_from = EndpointFrom.FUND_EV
    endpoint_to = EndpointToFMP.FUND_EV


class ScreenerView(FMPBaseView):
    endpoint_from = EndpointFrom.FUND_SCREENER
    endpoint_to = EndpointToFMP.FUND_SCREENER


class NewsView(FMPBaseView):
    endpoint_from = EndpointFrom.NEWS
    endpoint_to = EndpointToFMP.NEWS


class NewsSymbolView(FMPBaseView):
    endpoint_from = EndpointFrom.NEWS_SYMBOL
    endpoint_to = EndpointToFMP.NEWS_SYMBOL


class PressReleasesView(FMPBaseView):
    endpoint_from = EndpointFrom.NEWS_PR
    endpoint_to = EndpointToFMP.NEWS_PR


class PressReleasesSymbolView(FMPBaseView):
    endpoint_from = EndpointFrom.NEWS_SYMBOL_PR
    endpoint_to = EndpointToFMP.NEWS_SYMBOL_PR


class NewsSentimentView(FMPBaseView):
    endpoint_from = EndpointFrom.NEWS_SENTIMENT
    endpoint_to = EndpointToFMP.NEWS_SENTIMENT


class AnalystEstimatesView(FMPBaseView):
    endpoint_from = EndpointFrom.ANALYST_EST
    endpoint_to = EndpointToFMP.ANALYST_EST


class AnalystRecommendationsView(FMPBaseView):
    endpoint_from = EndpointFrom.ANALYST_RECO
    endpoint_to = EndpointToFMP.ANALYST_RECO


class AnalystPriceTargetsView(FMPBaseView):
    endpoint_from = EndpointFrom.ANALYST_PRICE_TARGETS
    endpoint_to = EndpointToFMP.ANALYST_PRICE_TARGETS
    allowed_params = CommonParams


class AnalystUpgradesDowngradesView(FMPBaseView):
    endpoint_from = EndpointFrom.ANALYST_UPGRADES
    endpoint_to = EndpointToFMP.ANALYST_UPGRADES
    allowed_params = CommonParams


class EarningsCalendarView(FMPBaseView):
    endpoint_from = EndpointFrom.EARNINGS_CAL
    endpoint_to = EndpointToFMP.EARNINGS_CAL
    allowed_params = CommonParams


class EarningsTranscriptsView(FMPBaseView):
    endpoint_from = EndpointFrom.EARNINGS_TRANSCRIPTS
    endpoint_to = EndpointToFMP.EARNINGS_TRANSCRIPTS


class EarningsHistoryView(FMPBaseView):
    endpoint_from = EndpointFrom.EARNINGS_HISTORY
    endpoint_to = EndpointToFMP.EARNINGS_HISTORY


class EarningsSurprisesView(FMPBaseView):
    endpoint_from = EndpointFrom.EARNINGS_SURPRISES
    endpoint_to = EndpointToFMP.EARNINGS_SURPRISES


class IPOCalendarView(FMPBaseView):
    endpoint_from = EndpointFrom.EVENTS_IPO
    endpoint_to = EndpointToFMP.EVENTS_IPO


class StockSplitCalendarView(FMPBaseView):
    endpoint_from = EndpointFrom.EVENTS_SPLIT
    endpoint_to = EndpointToFMP.EVENTS_SPLIT


class DividendCalendarView(FMPBaseView):
    endpoint_from = EndpointFrom.EVENTS_DIVIDEND
    endpoint_to = EndpointToFMP.EVENTS_DIVIDEND


class ThirteenFView(FMPBaseView):
    endpoint_from = EndpointFrom.INST_13F
    endpoint_to = EndpointToFMP.INST_13F


class InstitutionalHoldersView(FMPBaseView):
    endpoint_from = EndpointFrom.INST_HOLDERS
    endpoint_to = EndpointToFMP.INST_HOLDERS


class InsiderTradingView(FMPBaseView):
    endpoint_from = EndpointFrom.INST_INSIDER
    endpoint_to = EndpointToFMP.INST_INSIDER
    allowed_params = CommonParams


class SECFilingsView(FMPBaseView):
    endpoint_from = EndpointFrom.SEC_FILINGS
    endpoint_to = EndpointToFMP.SEC_FILINGS


class SEC10KView(FMPBaseView):
    endpoint_from = EndpointFrom.SEC_10K
    endpoint_to = EndpointToFMP.SEC_10K


class SEC10QView(FMPBaseView):
    endpoint_from = EndpointFrom.SEC_10Q
    endpoint_to = EndpointToFMP.SEC_10Q


class SEC8KView(FMPBaseView):
    endpoint_from = EndpointFrom.SEC_8K
    endpoint_to = EndpointToFMP.SEC_8K


class SECRSSFeedView(FMPBaseView):
    endpoint_from = EndpointFrom.SEC_RSS
    endpoint_to = EndpointToFMP.SEC_RSS


class GDPView(FMPBaseView):
    endpoint_from = EndpointFrom.ECO_GDP
    endpoint_to = EndpointToFMP.ECO_GDP


class InflationView(FMPBaseView):
    endpoint_from = EndpointFrom.ECO_CPI
    endpoint_to = EndpointToFMP.ECO_CPI


class UnemploymentView(FMPBaseView):
    endpoint_from = EndpointFrom.ECO_UNEMP
    endpoint_to = EndpointToFMP.ECO_UNEMP


class InterestRatesView(FMPBaseView):
    endpoint_from = EndpointFrom.ECO_RATES
    endpoint_to = EndpointToFMP.ECO_RATES


class TreasuryRatesView(FMPBaseView):
    endpoint_from = EndpointFrom.ECO_TREASURY
    endpoint_to = EndpointToFMP.ECO_TREASURY


class ETFListView(FMPBaseView):
    endpoint_from = EndpointFrom.ETF_LIST
    endpoint_to = EndpointToFMP.ETF_LIST


class ETFHoldingsView(FMPBaseView):
    endpoint_from = EndpointFrom.ETF_HOLDINGS
    endpoint_to = EndpointToFMP.ETF_HOLDINGS


class ETFPerformanceView(FMPBaseView):
    endpoint_from = EndpointFrom.ETF_PERF
    endpoint_to = EndpointToFMP.ETF_PERF


class MutualFundsListView(FMPBaseView):
    endpoint_from = EndpointFrom.MF_LIST
    endpoint_to = EndpointToFMP.MF_LIST


class CommoditiesMetalsView(FMPBaseView):
    endpoint_from = EndpointFrom.COM_METALS
    endpoint_to = EndpointToFMP.COM_QUOTES


class CommoditiesEnergyView(FMPBaseView):
    endpoint_from = EndpointFrom.COM_ENERGY
    endpoint_to = EndpointToFMP.COM_QUOTES


class CommoditiesAgriculturalView(FMPBaseView):
    endpoint_from = EndpointFrom.COM_AGRI
    endpoint_to = EndpointToFMP.COM_QUOTES


class CommoditiesHistoricalView(FMPBaseView):
    endpoint_from = EndpointFrom.COM_HIST
    endpoint_to = EndpointToFMP.COM_HIST


class CryptoListView(FMPBaseView):
    endpoint_from = EndpointFrom.CRYPTO_LIST
    endpoint_to = EndpointToFMP.CRYPTO_LIST


class CryptoQuoteView(FMPBaseView):
    endpoint_from = EndpointFrom.CRYPTO_QUOTE
    endpoint_to = EndpointToFMP.CRYPTO_QUOTE


class CryptoHistoricalView(FMPBaseView):
    endpoint_from = EndpointFrom.CRYPTO_HIST
    endpoint_to = EndpointToFMP.CRYPTO_HIST


class InternationalExchangesView(FMPBaseView):
    endpoint_from = EndpointFrom.INT_EXCHANGES
    endpoint_to = EndpointToFMP.INT_EXCHANGES


class InternationalStocksView(FMPBaseView):
    endpoint_from = EndpointFrom.INT_STOCKS
    endpoint_to = EndpointToFMP.INT_STOCKS


class ForexRatesView(FMPBaseView):
    endpoint_from = EndpointFrom.FOREX_RATES
    endpoint_to = EndpointToFMP.FOREX_RATES


class ForexPairView(FMPBaseView):
    endpoint_from = EndpointFrom.FOREX_PAIR
    endpoint_to = EndpointToFMP.FOREX_PAIR


class ExampleFMPGainersView(FMPBaseView):
    endpoint_from = EndpointFrom.EXAMPLE_FMP_GAINERS
    endpoint_to = EndpointToFMP.QUOTES_GAINERS
    authentication_classes = [JWTAuthentication, RequestTokenAuthentication]
    permission_classes = [IsAuthenticated, DailyLimitPermission]
    pagination_class = PageNumberPagination
    
    class QuerySerializer(serializers.Serializer):
        limit = serializers.IntegerField(min_value=1, max_value=1000, required=False, default=50)
        page = serializers.IntegerField(min_value=1, required=False, default=1)
        market = serializers.ChoiceField(choices=["stocks", "etf"], required=False)

    serializer_class = QuerySerializer

