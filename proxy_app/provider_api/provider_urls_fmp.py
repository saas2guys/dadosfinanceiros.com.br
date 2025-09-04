from __future__ import annotations

from django.urls import path

from .views_fmp import (
    AnalystEstimatesView,
    AnalystPriceTargetsView,
    AnalystRecommendationsView,
    AnalystUpgradesDowngradesView,
    BalanceSheetView,
    CashFlowView,
    CommoditiesAgriculturalView,
    CommoditiesEnergyView,
    CommoditiesHistoricalView,
    CommoditiesMetalsView,
    CryptoHistoricalView,
    CryptoListView,
    CryptoQuoteView,
    DCFView,
    DividendCalendarView,
    EarningsCalendarView,
    EarningsHistoryView,
    EarningsSurprisesView,
    EarningsTranscriptsView,
    EmployeeCountHistoricalView,
    EmployeeCountView,
    # EnterpriseValueView,  # COMMENTED: INTERNAL DUPLICATE
    ExecutiveCompensationBenchmarkView,
    ExecutiveCompensationView,
    ETFHoldingsView,
    ETFListView,
    ETFPerformanceView,
    ExampleFMPGainersView,
    ExchangeVariantsView,
    ForexPairView,
    ForexRatesView,
    GDPView,
    # GainersView,  # MISSING: View not found
    # HistoricalDividendsView,  # COMMENTED: DUPLICATE - Use Polygon
    HistoricalIntradayView,
    # HistoricalSplitsView,  # COMMENTED: DUPLICATE - Use Polygon
    # HistoricalView,  # COMMENTED: SIMILAR - Use Polygon
    InflationView,
    IncomeStatementView,
    InsiderTradingView,
    InstitutionalHoldersView,
    InternationalExchangesView,
    InternationalStocksView,
    # IPOCalendarView,  # COMMENTED: DUPLICATE - Use Polygon
    # InterestRatesView,  # MISSING: View not found
    # LosersView,  # COMMENTED: SIMILAR - Use Polygon
    MetricsView,
    MergersAcquisitionsSearchView,
    MergersAcquisitionsView,
    # MostActiveView,  # COMMENTED: SIMILAR - Use Polygon
    # MutualFundsListView,  # MISSING: View not found
    NewsSentimentView,
    NewsSymbolView,
    # NewsView,  # COMMENTED: DUPLICATE - Use Polygon
    PressReleasesSymbolView,
    PressReleasesView,
    QuoteBatchView,
    # QuoteView,  # COMMENTED: SIMILAR - Use Polygon
    # RatiosView,  # MISSING: View not found
    SearchCIKView,
    SearchCUSIPView,
    SearchISINView,
    # ReferenceExchangesView,  # COMMENTED: DUPLICATE - Use Polygon
    ReferenceMarketCapView,
    # ReferenceTickerExecutivesView,  # COMMENTED: INTERNAL DUPLICATE
    ReferenceTickerOutlookView,
    # ReferenceTickerProfileView,  # COMMENTED: INTERNAL DUPLICATE
    # ReferenceTickerView,  # COMMENTED: SIMILAR - Use Polygon
    ReferenceTickersView,
    SECFilingsView,
    SEC10KView,
    SEC10QView,
    SEC8KView,
    SECRSSFeedView,
    ScreenerView,
    SharesFloatAllView,
    SharesFloatView,
    SymbolChangeView,
    # StockSplitCalendarView,  # MISSING: View not found
    ThirteenFView,
    TreasuryRatesView,
    UnemploymentView,
)


urlpatterns = [
    AnalystEstimatesView.as_path(),
    AnalystPriceTargetsView.as_path(),
    AnalystRecommendationsView.as_path(),
    AnalystUpgradesDowngradesView.as_path(),
    BalanceSheetView.as_path(),
    CashFlowView.as_path(),
    CommoditiesAgriculturalView.as_path(),
    CommoditiesEnergyView.as_path(),
    CommoditiesHistoricalView.as_path(),
    CommoditiesMetalsView.as_path(),
    CryptoHistoricalView.as_path(),
    CryptoListView.as_path(),
    CryptoQuoteView.as_path(),
    DCFView.as_path(),
    DividendCalendarView.as_path(),
    EarningsCalendarView.as_path(),
    EarningsHistoryView.as_path(),
    EarningsSurprisesView.as_path(),
    EarningsTranscriptsView.as_path(),
    EmployeeCountHistoricalView.as_path(),
    EmployeeCountView.as_path(),
    # EnterpriseValueView.as_path(),  # COMMENTED: INTERNAL DUPLICATE
    ExecutiveCompensationBenchmarkView.as_path(),
    ExecutiveCompensationView.as_path(),
    ETFHoldingsView.as_path(),
    ETFListView.as_path(),
    ETFPerformanceView.as_path(),
    ExampleFMPGainersView.as_path(),
    ExchangeVariantsView.as_path(),
    ForexPairView.as_path(),
    ForexRatesView.as_path(),
    GDPView.as_path(),
    # GainersView.as_path(),  # MISSING: View not found
    # HistoricalDividendsView.as_path(),  # COMMENTED: DUPLICATE - Use Polygon
    HistoricalIntradayView.as_path(),
    # HistoricalSplitsView.as_path(),  # COMMENTED: DUPLICATE - Use Polygon
    # HistoricalView.as_path(),  # COMMENTED: SIMILAR - Use Polygon
    InflationView.as_path(),
    IncomeStatementView.as_path(),
    InsiderTradingView.as_path(),
    InstitutionalHoldersView.as_path(),
    InternationalExchangesView.as_path(),
    InternationalStocksView.as_path(),
    # IPOCalendarView.as_path(),  # COMMENTED: DUPLICATE - Use Polygon
    # InterestRatesView.as_path(),  # MISSING: View not found
    MergersAcquisitionsSearchView.as_path(),
    MergersAcquisitionsView.as_path(),
    # LosersView.as_path(),  # COMMENTED: SIMILAR - Use Polygon
    MetricsView.as_path(),
    # MostActiveView.as_path(),  # COMMENTED: SIMILAR - Use Polygon
    # MutualFundsListView.as_path(),  # MISSING: View not found
    NewsSentimentView.as_path(),
    NewsSymbolView.as_path(),
    # NewsView.as_path(),  # COMMENTED: DUPLICATE - Use Polygon
    PressReleasesSymbolView.as_path(),
    PressReleasesView.as_path(),
    QuoteBatchView.as_path(),
    # QuoteView.as_path(),  # COMMENTED: SIMILAR - Use Polygon
    # RatiosView.as_path(),  # MISSING: View not found
    SearchCIKView.as_path(),
    SearchCUSIPView.as_path(),
    SearchISINView.as_path(),
    # ReferenceExchangesView.as_path(),  # COMMENTED: DUPLICATE - Use Polygon
    ReferenceMarketCapView.as_path(),
    # ReferenceTickerExecutivesView.as_path(),  # COMMENTED: INTERNAL DUPLICATE
    ReferenceTickerOutlookView.as_path(),
    # ReferenceTickerProfileView.as_path(),  # COMMENTED: INTERNAL DUPLICATE
    # ReferenceTickerView.as_path(),  # COMMENTED: SIMILAR - Use Polygon
    ReferenceTickersView.as_path(),
    SECFilingsView.as_path(),
    SEC10KView.as_path(),
    SEC10QView.as_path(),
    SEC8KView.as_path(),
    SECRSSFeedView.as_path(),
    ScreenerView.as_path(),
    SharesFloatAllView.as_path(),
    SharesFloatView.as_path(),
    SymbolChangeView.as_path(),
    # StockSplitCalendarView.as_path(),  # MISSING: View not found
    ThirteenFView.as_path(),
    TreasuryRatesView.as_path(),
    UnemploymentView.as_path(),
]


