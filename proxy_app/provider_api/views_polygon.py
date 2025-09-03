from __future__ import annotations

from .base import PolygonBaseView
from .enums import EndpointFrom, EndpointToPolygon


class MarketStatusView(PolygonBaseView):
    endpoint_from = EndpointFrom.REFERENCE_MARKET_STATUS.value
    endpoint_to = EndpointToPolygon.REFERENCE_MARKET_STATUS.value


class MarketHolidaysView(PolygonBaseView):
    endpoint_from = EndpointFrom.REFERENCE_MARKET_HOLIDAYS.value
    endpoint_to = EndpointToPolygon.REFERENCE_MARKET_HOLIDAYS.value


class LastTradeView(PolygonBaseView):
    endpoint_from = EndpointFrom.QUOTES_LAST_TRADE.value
    endpoint_to = EndpointToPolygon.QUOTES_LAST_TRADE.value


class LastQuoteView(PolygonBaseView):
    endpoint_from = EndpointFrom.QUOTES_LAST_QUOTE.value
    endpoint_to = EndpointToPolygon.QUOTES_LAST_QUOTE.value


class PreviousCloseView(PolygonBaseView):
    endpoint_from = EndpointFrom.QUOTES_PREVIOUS_CLOSE.value
    endpoint_to = EndpointToPolygon.QUOTES_PREVIOUS_CLOSE.value


class GroupedDailyView(PolygonBaseView):
    endpoint_from = EndpointFrom.HISTORICAL_GROUPED.value
    endpoint_to = EndpointToPolygon.HISTORICAL_GROUPED.value


class OptionsContractsView(PolygonBaseView):
    endpoint_from = EndpointFrom.OPTIONS_CONTRACTS.value
    endpoint_to = EndpointToPolygon.OPTIONS_CONTRACTS.value


class OptionsChainView(PolygonBaseView):
    endpoint_from = EndpointFrom.OPTIONS_CHAIN.value
    endpoint_to = EndpointToPolygon.OPTIONS_CHAIN.value


class OptionsGreeksView(PolygonBaseView):
    endpoint_from = EndpointFrom.OPTIONS_GREEKS.value
    endpoint_to = EndpointToPolygon.OPTIONS_GREEKS.value


class OptionsOpenInterestView(PolygonBaseView):
    endpoint_from = EndpointFrom.OPTIONS_OPEN_INTEREST.value
    endpoint_to = EndpointToPolygon.OPTIONS_OPEN_INTEREST.value


class OptionsContractHistoricalView(PolygonBaseView):
    endpoint_from = EndpointFrom.OPTIONS_CONTRACT_HIST.value
    endpoint_to = EndpointToPolygon.OPTIONS_CONTRACT_HIST.value


class FuturesContractsView(PolygonBaseView):
    endpoint_from = EndpointFrom.FUTURES_CONTRACTS.value
    endpoint_to = EndpointToPolygon.FUTURES_CONTRACTS.value


class FuturesSnapshotView(PolygonBaseView):
    endpoint_from = EndpointFrom.FUTURES_SNAPSHOT.value
    endpoint_to = EndpointToPolygon.FUTURES_SNAPSHOT.value


class FuturesHistoricalView(PolygonBaseView):
    endpoint_from = EndpointFrom.FUTURES_HISTORICAL.value
    endpoint_to = EndpointToPolygon.FUTURES_HISTORICAL.value


class TickTradesView(PolygonBaseView):
    endpoint_from = EndpointFrom.TICKS_TRADES.value
    endpoint_to = EndpointToPolygon.TICKS_TRADES.value


class TickQuotesView(PolygonBaseView):
    endpoint_from = EndpointFrom.TICKS_QUOTES.value
    endpoint_to = EndpointToPolygon.TICKS_QUOTES.value


class TickAggregatesView(PolygonBaseView):
    endpoint_from = EndpointFrom.TICKS_AGGREGATES.value
    endpoint_to = EndpointToPolygon.TICKS_AGGREGATES.value


