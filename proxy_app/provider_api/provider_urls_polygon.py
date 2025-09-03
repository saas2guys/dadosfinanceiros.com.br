from __future__ import annotations

from django.urls import path

from .views_polygon import (
    ExamplePolygonTradesView,
    FuturesContractsView,
    FuturesHistoricalView,
    FuturesSnapshotView,
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
    TickAggregatesView,
    TickQuotesView,
    TickTradesView,
)


urlpatterns = [
    ExamplePolygonTradesView.as_path(),
    FuturesContractsView.as_path(),
    FuturesHistoricalView.as_path(),
    FuturesSnapshotView.as_path(),
    GroupedDailyView.as_path(),
    LastQuoteView.as_path(),
    LastTradeView.as_path(),
    MarketHolidaysView.as_path(),
    MarketStatusView.as_path(),
    OptionsChainView.as_path(),
    OptionsContractHistoricalView.as_path(),
    OptionsContractsView.as_path(),
    OptionsGreeksView.as_path(),
    OptionsOpenInterestView.as_path(),
    PreviousCloseView.as_path(),
    TickAggregatesView.as_path(),
    TickQuotesView.as_path(),
    TickTradesView.as_path(),
]


