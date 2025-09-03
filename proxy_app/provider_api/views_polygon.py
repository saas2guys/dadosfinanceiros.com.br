from __future__ import annotations

from .base import PolygonBaseView
from .enums import EndpointFrom, EndpointToPolygon
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication
from users.authentication import RequestTokenAuthentication
from users.permissions import DailyLimitPermission


class MarketStatusView(PolygonBaseView):
    endpoint_from = EndpointFrom.REFERENCE_MARKET_STATUS
    endpoint_to = EndpointToPolygon.REFERENCE_MARKET_STATUS


class MarketHolidaysView(PolygonBaseView):
    endpoint_from = EndpointFrom.REFERENCE_MARKET_HOLIDAYS
    endpoint_to = EndpointToPolygon.REFERENCE_MARKET_HOLIDAYS


class LastTradeView(PolygonBaseView):
    endpoint_from = EndpointFrom.QUOTES_LAST_TRADE
    endpoint_to = EndpointToPolygon.QUOTES_LAST_TRADE


class LastQuoteView(PolygonBaseView):
    endpoint_from = EndpointFrom.QUOTES_LAST_QUOTE
    endpoint_to = EndpointToPolygon.QUOTES_LAST_QUOTE


class PreviousCloseView(PolygonBaseView):
    endpoint_from = EndpointFrom.QUOTES_PREVIOUS_CLOSE
    endpoint_to = EndpointToPolygon.QUOTES_PREVIOUS_CLOSE


class GroupedDailyView(PolygonBaseView):
    endpoint_from = EndpointFrom.HISTORICAL_GROUPED
    endpoint_to = EndpointToPolygon.HISTORICAL_GROUPED


class OptionsContractsView(PolygonBaseView):
    endpoint_from = EndpointFrom.OPTIONS_CONTRACTS
    endpoint_to = EndpointToPolygon.OPTIONS_CONTRACTS


class OptionsChainView(PolygonBaseView):
    endpoint_from = EndpointFrom.OPTIONS_CHAIN
    endpoint_to = EndpointToPolygon.OPTIONS_CHAIN


class OptionsGreeksView(PolygonBaseView):
    endpoint_from = EndpointFrom.OPTIONS_GREEKS
    endpoint_to = EndpointToPolygon.OPTIONS_GREEKS


class OptionsOpenInterestView(PolygonBaseView):
    endpoint_from = EndpointFrom.OPTIONS_OPEN_INTEREST
    endpoint_to = EndpointToPolygon.OPTIONS_OPEN_INTEREST


class OptionsContractHistoricalView(PolygonBaseView):
    endpoint_from = EndpointFrom.OPTIONS_CONTRACT_HIST
    endpoint_to = EndpointToPolygon.OPTIONS_CONTRACT_HIST


class FuturesContractsView(PolygonBaseView):
    endpoint_from = EndpointFrom.FUTURES_CONTRACTS
    endpoint_to = EndpointToPolygon.FUTURES_CONTRACTS


class FuturesSnapshotView(PolygonBaseView):
    endpoint_from = EndpointFrom.FUTURES_SNAPSHOT
    endpoint_to = EndpointToPolygon.FUTURES_SNAPSHOT


class FuturesHistoricalView(PolygonBaseView):
    endpoint_from = EndpointFrom.FUTURES_HISTORICAL
    endpoint_to = EndpointToPolygon.FUTURES_HISTORICAL


class TickTradesView(PolygonBaseView):
    endpoint_from = EndpointFrom.TICKS_TRADES
    endpoint_to = EndpointToPolygon.TICKS_TRADES


class TickQuotesView(PolygonBaseView):
    endpoint_from = EndpointFrom.TICKS_QUOTES
    endpoint_to = EndpointToPolygon.TICKS_QUOTES


class TickAggregatesView(PolygonBaseView):
    endpoint_from = EndpointFrom.TICKS_AGGREGATES
    endpoint_to = EndpointToPolygon.TICKS_AGGREGATES


class ExamplePolygonTradesView(PolygonBaseView):
    endpoint_from = EndpointFrom.EXAMPLE_POLYGON_TRADES
    endpoint_to = EndpointToPolygon.TICKS_TRADES
    authentication_classes = [JWTAuthentication, RequestTokenAuthentication]
    permission_classes = [IsAuthenticated, DailyLimitPermission]
    pagination_class = LimitOffsetPagination
    paginate_locally = True
    param_specs = {
        "limit": {"type": "int", "min": 1, "max": 5000, "default": 100, "dest": "limit"},
        "offset": {"type": "int", "min": 0, "default": 0},
        "timestamp": {"type": "str"},
    }
    strict_unknown = True
    strict_types = True


