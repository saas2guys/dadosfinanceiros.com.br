from __future__ import annotations

from .base import PolygonBaseView
from .enums import EndpointTo, EndpointFrom, PolygonParams


class AggCustomRangeView(PolygonBaseView):
    endpoint_from = EndpointFrom.STOCKS_AGG_CUSTOM_RANGE
    endpoint_to = EndpointTo.Polygon.AGG_CUSTOM_RANGE
    allowed_params = [PolygonParams.Common, PolygonParams.AggCustomRange]


class AggGroupedDailyView(PolygonBaseView):
    endpoint_from = EndpointFrom.STOCKS_AGG_GROUPED_DAILY
    endpoint_to = EndpointTo.Polygon.AGG_GROUPED_DAILY
    allowed_params = [PolygonParams.Common, PolygonParams.AggGroupedDaily]


class AggPreviousDayView(PolygonBaseView):
    endpoint_from = EndpointFrom.STOCKS_AGG_PREVIOUS_DAY
    endpoint_to = EndpointTo.Polygon.AGG_PREVIOUS_DAY
    allowed_params = [PolygonParams.Common, PolygonParams.OpenClose]


class IndicatorEMAView(PolygonBaseView):
    endpoint_from = EndpointFrom.STOCKS_INDICATOR_EMA
    endpoint_to = EndpointTo.Polygon.INDICATOR_EMA
    allowed_params = [PolygonParams.Common, PolygonParams.IndicatorCommon]


class IndicatorMACDView(PolygonBaseView):
    endpoint_from = EndpointFrom.STOCKS_INDICATOR_MACD
    endpoint_to = EndpointTo.Polygon.INDICATOR_MACD
    allowed_params = [PolygonParams.Common, PolygonParams.IndicatorMACD]


class IndicatorRSIView(PolygonBaseView):
    endpoint_from = EndpointFrom.STOCKS_INDICATOR_RSI
    endpoint_to = EndpointTo.Polygon.INDICATOR_RSI
    allowed_params = [PolygonParams.Common, PolygonParams.IndicatorCommon]


class IndicatorSMAView(PolygonBaseView):
    endpoint_from = EndpointFrom.STOCKS_INDICATOR_SMA
    endpoint_to = EndpointTo.Polygon.INDICATOR_SMA
    allowed_params = [PolygonParams.Common, PolygonParams.IndicatorCommon]


class LastNBBOView(PolygonBaseView):
    endpoint_from = EndpointFrom.STOCKS_LAST_NBBO
    endpoint_to = EndpointTo.Polygon.LAST_NBBO


class LastTradeView(PolygonBaseView):
    endpoint_from = EndpointFrom.STOCKS_LAST_TRADE
    endpoint_to = EndpointTo.Polygon.LAST_TRADE


class MarketHolidaysView(PolygonBaseView):
    endpoint_from = EndpointFrom.STOCKS_REFERENCE_MARKET_HOLIDAYS
    endpoint_to = EndpointTo.Polygon.REFERENCE_MARKET_HOLIDAYS


class MarketStatusView(PolygonBaseView):
    endpoint_from = EndpointFrom.STOCKS_REFERENCE_MARKET_STATUS
    endpoint_to = EndpointTo.Polygon.REFERENCE_MARKET_STATUS


class OpenCloseView(PolygonBaseView):
    endpoint_from = EndpointFrom.STOCKS_OPEN_CLOSE
    endpoint_to = EndpointTo.Polygon.OPEN_CLOSE
    allowed_params = [PolygonParams.Common, PolygonParams.OpenClose]


class QuotesView(PolygonBaseView):
    endpoint_from = EndpointFrom.STOCKS_QUOTES
    endpoint_to = EndpointTo.Polygon.QUOTES
    allowed_params = [PolygonParams.Common, PolygonParams.Quotes]


class ReferenceConditionsView(PolygonBaseView):
    endpoint_from = EndpointFrom.STOCKS_REFERENCE_CONDITIONS
    endpoint_to = EndpointTo.Polygon.REFERENCE_CONDITIONS
    allowed_params = [PolygonParams.Common, PolygonParams.ReferenceConditions]


class ReferenceDividendsView(PolygonBaseView):
    endpoint_from = EndpointFrom.STOCKS_REFERENCE_DIVIDENDS
    endpoint_to = EndpointTo.Polygon.REFERENCE_DIVIDENDS
    allowed_params = [PolygonParams.Common, PolygonParams.ReferenceDividends]


class ReferenceExchangesView(PolygonBaseView):
    endpoint_from = EndpointFrom.STOCKS_REFERENCE_EXCHANGES
    endpoint_to = EndpointTo.Polygon.REFERENCE_EXCHANGES
    allowed_params = [PolygonParams.Common, PolygonParams.ReferenceExchanges]


class ReferenceFinancialsView(PolygonBaseView):
    endpoint_from = EndpointFrom.STOCKS_REFERENCE_FINANCIALS
    endpoint_to = EndpointTo.Polygon.REFERENCE_FINANCIALS
    allowed_params = [PolygonParams.Common, PolygonParams.ReferenceFinancials]


class ReferenceIPOsView(PolygonBaseView):
    endpoint_from = EndpointFrom.STOCKS_REFERENCE_IPOS
    endpoint_to = EndpointTo.Polygon.REFERENCE_IPOS
    allowed_params = [PolygonParams.Common, PolygonParams.ReferenceIPOs]


class ReferenceNewsView(PolygonBaseView):
    endpoint_from = EndpointFrom.STOCKS_REFERENCE_NEWS
    endpoint_to = EndpointTo.Polygon.REFERENCE_NEWS
    allowed_params = [PolygonParams.Common, PolygonParams.ReferenceNews]


class ReferenceSplitsView(PolygonBaseView):
    endpoint_from = EndpointFrom.STOCKS_REFERENCE_SPLITS
    endpoint_to = EndpointTo.Polygon.REFERENCE_SPLITS
    allowed_params = [PolygonParams.Common, PolygonParams.ReferenceSplits]


class ReferenceTickerEventsView(PolygonBaseView):
    endpoint_from = EndpointFrom.STOCKS_REFERENCE_TICKER_EVENTS
    endpoint_to = EndpointTo.Polygon.REFERENCE_TICKER_EVENTS
    allowed_params = [PolygonParams.Common, PolygonParams.ReferenceTickerEvents]


class ReferenceTickerTypesView(PolygonBaseView):
    endpoint_from = EndpointFrom.STOCKS_REFERENCE_TICKER_TYPES
    endpoint_to = EndpointTo.Polygon.REFERENCE_TICKER_TYPES
    allowed_params = [PolygonParams.Common, PolygonParams.ReferenceTickerTypes]


class ReferenceTickerView(PolygonBaseView):
    endpoint_from = EndpointFrom.STOCKS_REFERENCE_TICKER
    endpoint_to = EndpointTo.Polygon.REFERENCE_TICKER
    allowed_params = [PolygonParams.Common, PolygonParams.ReferenceTicker]


class ReferenceTickersView(PolygonBaseView):
    endpoint_from = EndpointFrom.STOCKS_REFERENCE_TICKERS
    endpoint_to = EndpointTo.Polygon.REFERENCE_TICKERS
    allowed_params = [PolygonParams.Common, PolygonParams.ReferenceTickers]


class RelatedCompaniesView(PolygonBaseView):
    endpoint_from = EndpointFrom.STOCKS_RELATED_COMPANIES
    endpoint_to = EndpointTo.Polygon.RELATED_COMPANIES


class SnapshotMarketView(PolygonBaseView):
    endpoint_from = EndpointFrom.STOCKS_SNAPSHOT_MARKET
    endpoint_to = EndpointTo.Polygon.SNAPSHOT_MARKET
    allowed_params = [PolygonParams.Common, PolygonParams.SnapshotMarket]


class SnapshotMoversView(PolygonBaseView):
    endpoint_from = EndpointFrom.STOCKS_SNAPSHOT_MOVERS
    endpoint_to = EndpointTo.Polygon.SNAPSHOT_MOVERS
    allowed_params = [PolygonParams.Common, PolygonParams.SnapshotMovers]


class SnapshotTickerView(PolygonBaseView):
    endpoint_from = EndpointFrom.STOCKS_SNAPSHOT_TICKER
    endpoint_to = EndpointTo.Polygon.SNAPSHOT_TICKER


class SnapshotUnifiedView(PolygonBaseView):
    endpoint_from = EndpointFrom.STOCKS_SNAPSHOT_UNIFIED
    endpoint_to = EndpointTo.Polygon.SNAPSHOT_UNIFIED
    allowed_params = [PolygonParams.Common, PolygonParams.SnapshotUnified]


class StocksShortInterestView(PolygonBaseView):
    endpoint_from = EndpointFrom.STOCKS_SHORT_INTEREST
    endpoint_to = EndpointTo.Polygon.STOCKS_SHORT_INTEREST
    allowed_params = [PolygonParams.Common, PolygonParams.StocksShortInterest]


class StocksShortVolumeView(PolygonBaseView):
    endpoint_from = EndpointFrom.STOCKS_SHORT_VOLUME
    endpoint_to = EndpointTo.Polygon.STOCKS_SHORT_VOLUME
    allowed_params = [PolygonParams.Common, PolygonParams.StocksShortVolume]


class TradesView(PolygonBaseView):
    endpoint_from = EndpointFrom.STOCKS_TRADES
    endpoint_to = EndpointTo.Polygon.TRADES
    allowed_params = [PolygonParams.Common, PolygonParams.Trades]
