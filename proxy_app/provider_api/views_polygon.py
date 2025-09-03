from __future__ import annotations

from .base import PolygonBaseView
from .enums import EndpointFrom, EndpointTo
from rest_framework import serializers
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication
from users.authentication import RequestTokenAuthentication
from users.permissions import DailyLimitPermission


class FuturesContractsView(PolygonBaseView):
    """
    List available futures contracts and related metadata.

    App path:
        /api/v1/futures/contracts/

    Provider path:
        /v3/reference/futures/contracts

    Parameters:
        Forwards any query parameters to the provider unmodified.
    """
    endpoint_from = EndpointFrom.FUTURES_CONTRACTS
    endpoint_to = EndpointTo.Polygon.FUTURES_CONTRACTS


class FuturesHistoricalView(PolygonBaseView):
    """
    Fetch historical aggregate bars for a futures ticker.

    App path:
        /api/v1/futures/{symbol}/historical/

    Provider path:
        /v2/aggs/ticker/{symbol}/range/{multiplier}/{timespan}/{from}/{to}

    Parameters:
        symbol (str): Futures ticker symbol.
        multiplier (int): Size of each aggregate window.
        timespan (str): Unit of time, e.g., "day".
        from (str): Start timestamp or date.
        to (str): End timestamp or date.
    """
    endpoint_from = EndpointFrom.FUTURES_HISTORICAL
    endpoint_to = EndpointTo.Polygon.FUTURES_HISTORICAL


class FuturesSnapshotView(PolygonBaseView):
    """
    Retrieve a real-time snapshot for a futures ticker.

    App path:
        /api/v1/futures/{symbol}/snapshot/

    Provider path:
        /v2/snapshot/locale/global/markets/futures/tickers/{symbol}

    Parameters:
        symbol (str): Futures ticker symbol.
    """
    endpoint_from = EndpointFrom.FUTURES_SNAPSHOT
    endpoint_to = EndpointTo.Polygon.FUTURES_SNAPSHOT


class GroupedDailyView(PolygonBaseView):
    """
    Return grouped daily aggregate bars for all U.S. stocks on a date.

    App path:
        /api/v1/historical/grouped/{date}/

    Provider path:
        /v2/aggs/grouped/locale/us/market/stocks/{date}

    Parameters:
        date (str): ISO date in the form YYYY-MM-DD.
    """
    endpoint_from = EndpointFrom.HISTORICAL_GROUPED
    endpoint_to = EndpointTo.Polygon.HISTORICAL_GROUPED


class LastQuoteView(PolygonBaseView):
    """
    Retrieve the last NBBO quote for a given equity symbol.

    App path:
        /api/v1/quotes/{symbol}/last-quote/

    Provider path:
        /v2/last/nbbo/{symbol}

    Parameters:
        symbol (str): Ticker symbol, e.g., "AAPL".
    """
    endpoint_from = EndpointFrom.QUOTES_LAST_QUOTE
    endpoint_to = EndpointTo.Polygon.QUOTES_LAST_QUOTE


class LastTradeView(PolygonBaseView):
    """
    Retrieve the most recent trade for a given equity symbol.

    App path:
        /api/v1/quotes/{symbol}/last-trade/

    Provider path:
        /v2/last/trade/{symbol}

    Parameters:
        symbol (str): Ticker symbol, e.g., "AAPL".
    """
    endpoint_from = EndpointFrom.QUOTES_LAST_TRADE
    endpoint_to = EndpointTo.Polygon.QUOTES_LAST_TRADE


class MarketHolidaysView(PolygonBaseView):
    """
    List upcoming U.S. market holidays.

    App path:
        /api/v1/reference/market-holidays/

    Provider path:
        /v1/marketstatus/upcoming

    Parameters:
        None. Forwards any query parameters to the provider unmodified.
    """
    endpoint_from = EndpointFrom.REFERENCE_MARKET_HOLIDAYS
    endpoint_to = EndpointTo.Polygon.REFERENCE_MARKET_HOLIDAYS


class MarketStatusView(PolygonBaseView):
    """
    Return current U.S. market status (open/closed and session details).

    App path:
        /api/v1/reference/market-status/

    Provider path:
        /v1/marketstatus/now

    Parameters:
        None. Forwards any query parameters to the provider unmodified.
    """
    endpoint_from = EndpointFrom.REFERENCE_MARKET_STATUS
    endpoint_to = EndpointTo.Polygon.REFERENCE_MARKET_STATUS


class OptionsChainView(PolygonBaseView):
    """
    Get a snapshot of the options chain for an underlying symbol.

    App path:
        /api/v1/options/chain/{symbol}/

    Provider path:
        /v3/snapshot/options/{symbol}

    Parameters:
        symbol (str): Underlying ticker, e.g., "AAPL".
    """
    endpoint_from = EndpointFrom.OPTIONS_CHAIN
    endpoint_to = EndpointTo.Polygon.OPTIONS_CHAIN


class OptionsContractsView(PolygonBaseView):
    """
    List available options contracts and related metadata.

    App path:
        /api/v1/options/contracts/

    Provider path:
        /v3/reference/options/contracts

    Parameters:
        Forwards any query parameters to the provider unmodified.
    """
    endpoint_from = EndpointFrom.OPTIONS_CONTRACTS
    endpoint_to = EndpointTo.Polygon.OPTIONS_CONTRACTS


class OptionsContractHistoricalView(PolygonBaseView):
    """
    Fetch historical aggregate bars for an option contract.

    App path:
        /api/v1/options/{contract}/historical/

    Provider path:
        /v2/aggs/ticker/{contract}/range/{multiplier}/{timespan}/{from}/{to}

    Parameters:
        contract (str): Option contract identifier.
        multiplier (int): Size of each aggregate window.
        timespan (str): Unit of time, e.g., "day".
        from (str): Start timestamp or date.
        to (str): End timestamp or date.
    """
    endpoint_from = EndpointFrom.OPTIONS_CONTRACT_HIST
    endpoint_to = EndpointTo.Polygon.OPTIONS_CONTRACT_HIST


class OptionsGreeksView(PolygonBaseView):
    """
    Get a snapshot of options greeks for a symbol.

    App path:
        /api/v1/options/{symbol}/greeks/

    Provider path:
        /v3/snapshot/options/{symbol}

    Parameters:
        symbol (str): Option or underlying symbol.
    """
    endpoint_from = EndpointFrom.OPTIONS_GREEKS
    endpoint_to = EndpointTo.Polygon.OPTIONS_GREEKS


class OptionsOpenInterestView(PolygonBaseView):
    """
    Get a snapshot of options open interest for a symbol.

    App path:
        /api/v1/options/{symbol}/open-interest/

    Provider path:
        /v3/snapshot/options/{symbol}

    Parameters:
        symbol (str): Option or underlying symbol.
    """
    endpoint_from = EndpointFrom.OPTIONS_OPEN_INTEREST
    endpoint_to = EndpointTo.Polygon.OPTIONS_OPEN_INTEREST


class PreviousCloseView(PolygonBaseView):
    """
    Get the previous trading session's aggregate bar for a symbol.

    App path:
        /api/v1/quotes/{symbol}/previous-close/

    Provider path:
        /v2/aggs/ticker/{symbol}/prev

    Parameters:
        symbol (str): Ticker symbol, e.g., "AAPL".
    """
    endpoint_from = EndpointFrom.QUOTES_PREVIOUS_CLOSE
    endpoint_to = EndpointTo.Polygon.QUOTES_PREVIOUS_CLOSE


class TickAggregatesView(PolygonBaseView):
    """
    Retrieve time-aggregated bars for a ticker.

    App path:
        /api/v1/ticks/{symbol}/aggregates/

    Provider path:
        /v2/aggs/ticker/{symbol}/range/{multiplier}/{timespan}/{from}/{to}

    Parameters:
        symbol (str): Ticker symbol.
        multiplier (int): Size of each aggregate window.
        timespan (str): Unit of time, e.g., "minute", "day".
        from (str): Start timestamp or date.
        to (str): End timestamp or date.
    """
    endpoint_from = EndpointFrom.TICKS_AGGREGATES
    endpoint_to = EndpointTo.Polygon.TICKS_AGGREGATES


class TickQuotesView(PolygonBaseView):
    """
    Stream or fetch tick-level quotes for a ticker.

    App path:
        /api/v1/ticks/{symbol}/quotes/

    Provider path:
        /v3/quotes/{symbol}

    Parameters:
        symbol (str): Ticker symbol.
    """
    endpoint_from = EndpointFrom.TICKS_QUOTES
    endpoint_to = EndpointTo.Polygon.TICKS_QUOTES


class TickTradesView(PolygonBaseView):
    """
    Stream or fetch tick-level trades for a ticker.

    App path:
        /api/v1/ticks/{symbol}/trades/

    Provider path:
        /v3/trades/{symbol}

    Parameters:
        symbol (str): Ticker symbol.
    """
    endpoint_from = EndpointFrom.TICKS_TRADES
    endpoint_to = EndpointTo.Polygon.TICKS_TRADES


class ExamplePolygonTradesView(PolygonBaseView):
    """
    Demonstration endpoint showcasing auth, pagination, and query validation.

    App path:
        /api/v1/examples/polygon/{symbol}/trades/

    Provider path:
        /v3/trades/{symbol}

    Parameters:
        symbol (str): Ticker symbol.
        limit (int): Max number of items to return per page.
        offset (int): Offset for pagination.
        timestamp (str): Optional timestamp filter.
    """
    active = True
    authentication_classes = [JWTAuthentication, RequestTokenAuthentication]
    endpoint_from = EndpointFrom.EXAMPLE_POLYGON_TRADES
    endpoint_to = EndpointTo.Polygon.TICKS_TRADES
    name = "example_polygon_trades"
    pagination_class = LimitOffsetPagination
    permission_classes = [IsAuthenticated, DailyLimitPermission]
    timeout = 15.0
    
    class QuerySerializer(serializers.Serializer):
        limit = serializers.IntegerField(min_value=1, max_value=5000, required=False, default=100)
        offset = serializers.IntegerField(min_value=0, required=False, default=0)
        timestamp = serializers.CharField(required=False)

    serializer_class = QuerySerializer
