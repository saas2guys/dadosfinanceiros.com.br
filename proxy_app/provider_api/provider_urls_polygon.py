from __future__ import annotations

from django.urls import path

from .views_polygon import (
    GroupedDailyView,
    LastQuoteView,
    LastTradeView,
    MarketHolidaysView,
    MarketStatusView,
    OptionsChainView,
    OptionsContractHistoricalView,
    OptionsContractsView,
    OptionsGreeksView,
    OptionsOpenInterestView,
    PreviousCloseView,
    FuturesContractsView,
    FuturesHistoricalView,
    FuturesSnapshotView,
    TickAggregatesView,
    TickQuotesView,
    TickTradesView,
)


urlpatterns = [
    MarketStatusView.as_path(),
    MarketHolidaysView.as_path(),
    LastTradeView.as_path(),
    LastQuoteView.as_path(),
    PreviousCloseView.as_path(),
    GroupedDailyView.as_path(),
    OptionsContractsView.as_path(),
    OptionsChainView.as_path(),
    OptionsGreeksView.as_path(),
    OptionsOpenInterestView.as_path(),
    OptionsContractHistoricalView.as_path(),
    FuturesContractsView.as_path(),
    FuturesSnapshotView.as_path(),
    FuturesHistoricalView.as_path(),
    TickTradesView.as_path(),
    TickQuotesView.as_path(),
    TickAggregatesView.as_path(),
]


