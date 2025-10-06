from .base import PolygonBaseView
from .enums import EndpointFrom, EndpointTo, PolygonParams


class AggregateCustomRangeView(PolygonBaseView):
    """
    Return custom-range aggregate bars (OHLCV) for a stock, forwarding params directly to Polygon.

    App path:
        /api/v1/stocks/aggs/{stocksTicker}/range/{multiplier}/{timespan}/{from}/{to}/

    Provider path:
        /v2/aggs/ticker/{stocksTicker}/range/{multiplier}/{timespan}/{from}/{to}

    Path parameters:
        stocksTicker (str): Target stock ticker symbol.
        multiplier (int): Multiplier for the timespan (e.g., 1, 5, 15).
        timespan (str): Bar interval unit (e.g., minute, hour, day).
        from (str): Start datetime or date.
        to (str): End datetime or date.

    GET Parameters:
        adjusted (bool): Whether results are adjusted.
        limit (int): Maximum number of results.
        order (str): Sort order.
        sort (str): Sort field.

    Examples:
        /api/v1/stocks/aggs/AAPL/range/1/day/2024-01-01/2024-01-31/?adjusted=true
        /api/v1/stocks/aggs/AAPL/range/1/day/2024-01-01/2024-01-31/?limit=500
        /api/v1/stocks/aggs/AAPL/range/1/day/2024-01-01/2024-01-31/?order=asc
        /api/v1/stocks/aggs/AAPL/range/1/day/2024-01-01/2024-01-31/?sort=timestamp
    """

    endpoint_from = EndpointFrom.STOCKS_AGGREGATE_CUSTOM_RANGE
    endpoint_to = EndpointTo.Polygon.AGG_CUSTOM_RANGE
    allowed_params = [PolygonParams.Common, PolygonParams.AggregateCustomRange]


class AggregateGroupedDailyView(PolygonBaseView):
    """
    Return grouped daily aggregates across the market for a given date.

    App path:
        /api/v1/stocks/aggs/grouped/{date}/

    Provider path:
        /v2/aggs/grouped/locale/us/market/stocks/{date}

    Path parameters:
        date (str): Target date.

    GET Parameters:
        adjusted (bool): Whether results are adjusted.
        include_otc (bool): Include OTC data.
        limit (int): Maximum number of results.
        order (str): Sort order.
        sort (str): Sort field.

    Examples:
        /api/v1/stocks/aggs/grouped/2024-01-05/?adjusted=true
        /api/v1/stocks/aggs/grouped/2024-01-05/?include_otc=true
        /api/v1/stocks/aggs/grouped/2024-01-05/?limit=500
        /api/v1/stocks/aggs/grouped/2024-01-05/?order=desc
        /api/v1/stocks/aggs/grouped/2024-01-05/?sort=ticker
    """

    endpoint_from = EndpointFrom.STOCKS_AGGREGATE_GROUPED_DAILY
    endpoint_to = EndpointTo.Polygon.AGG_GROUPED_DAILY
    allowed_params = [PolygonParams.Common, PolygonParams.AggregateGroupedDaily]


class AggregatePreviousDayView(PolygonBaseView):
    """
    Return previous day's aggregate bar for a stock.

    App path:
        /api/v1/stocks/aggs/{stocksTicker}/prev/

    Provider path:
        /v2/aggs/ticker/{stocksTicker}/prev

    Path parameters:
        stocksTicker (str): Target stock ticker symbol.

    GET Parameters:
        adjusted (bool): Whether results are adjusted.
        limit (int): Maximum number of results.
        order (str): Sort order.
        sort (str): Sort field.

    Examples:
        /api/v1/stocks/aggs/AAPL/prev/?adjusted=true
        /api/v1/stocks/aggs/AAPL/prev/?limit=1
        /api/v1/stocks/aggs/AAPL/prev/?order=asc
        /api/v1/stocks/aggs/AAPL/prev/?sort=volume
    """

    endpoint_from = EndpointFrom.STOCKS_AGGREGATE_PREVIOUS_DAY
    endpoint_to = EndpointTo.Polygon.AGG_PREVIOUS_DAY
    allowed_params = [PolygonParams.Common, PolygonParams.OpenClose]


class IndicatorEMAView(PolygonBaseView):
    """
    Compute EMA indicator for a symbol using Polygon's indicators API.

    App path:
        /api/v1/stocks/indicators/ema/{stockTicker}/

    Provider path:
        /v1/indicators/ema/{stockTicker}

    Path parameters:
        stockTicker (str): Target stock ticker symbol.

    GET Parameters:
        expand_underlying (bool): Include underlying series.
        series_type (str): Series type.
        timestamp (str): Filter by timestamp.
        window (int): Window length.
        limit (int): Maximum number of results.
        order (str): Sort order.
        sort (str): Sort field.

    Examples:
        /api/v1/stocks/indicators/ema/AAPL/?window=14
        /api/v1/stocks/indicators/ema/AAPL/?series_type=close
        /api/v1/stocks/indicators/ema/AAPL/?timestamp=2024-01-02
        /api/v1/stocks/indicators/ema/AAPL/?expand_underlying=false
        /api/v1/stocks/indicators/ema/AAPL/?limit=500
        /api/v1/stocks/indicators/ema/AAPL/?order=asc
        /api/v1/stocks/indicators/ema/AAPL/?sort=timestamp
    """

    endpoint_from = EndpointFrom.STOCKS_INDICATOR_EMA
    endpoint_to = EndpointTo.Polygon.INDICATOR_EMA
    allowed_params = [PolygonParams.Common, PolygonParams.IndicatorCommon]


class IndicatorMACDView(PolygonBaseView):
    """
    Compute MACD indicator for a symbol using Polygon's indicators API.

    App path:
        /api/v1/stocks/indicators/macd/{stockTicker}/

    Provider path:
        /v1/indicators/macd/{stockTicker}

    Path parameters:
        stockTicker (str): Target stock ticker symbol.

    GET Parameters:
        expand_underlying (bool): Include underlying series.
        long_window (int): Long window length.
        series_type (str): Series type.
        short_window (int): Short window length.
        signal_window (int): Signal window length.
        timestamp (str): Filter by timestamp.
        limit (int): Maximum number of results.
        order (str): Sort order.
        sort (str): Sort field.

    Examples:
        /api/v1/stocks/indicators/macd/AAPL/?short_window=12
        /api/v1/stocks/indicators/macd/AAPL/?long_window=26
        /api/v1/stocks/indicators/macd/AAPL/?signal_window=9
        /api/v1/stocks/indicators/macd/AAPL/?series_type=close
        /api/v1/stocks/indicators/macd/AAPL/?expand_underlying=true
        /api/v1/stocks/indicators/macd/AAPL/?timestamp=2024-01-02
        /api/v1/stocks/indicators/macd/AAPL/?limit=500
        /api/v1/stocks/indicators/macd/AAPL/?order=desc
        /api/v1/stocks/indicators/macd/AAPL/?sort=timestamp
    """

    endpoint_from = EndpointFrom.STOCKS_INDICATOR_MACD
    endpoint_to = EndpointTo.Polygon.INDICATOR_MACD
    allowed_params = [PolygonParams.Common, PolygonParams.IndicatorMACD]


class IndicatorRSIView(PolygonBaseView):
    """
    Compute RSI indicator for a symbol using Polygon's indicators API.

    App path:
        /api/v1/stocks/indicators/rsi/{stockTicker}/

    Provider path:
        /v1/indicators/rsi/{stockTicker}

    Path parameters:
        stockTicker (str): Target stock ticker symbol.

    GET Parameters:
        expand_underlying (bool): Include underlying series.
        series_type (str): Series type.
        timestamp (str): Filter by timestamp.
        window (int): Window length.
        limit (int): Maximum number of results.
        order (str): Sort order.
        sort (str): Sort field.

    Examples:
        /api/v1/stocks/indicators/rsi/AAPL/?window=14
        /api/v1/stocks/indicators/rsi/AAPL/?series_type=close
        /api/v1/stocks/indicators/rsi/AAPL/?timestamp=2024-01-02
        /api/v1/stocks/indicators/rsi/AAPL/?expand_underlying=false
        /api/v1/stocks/indicators/rsi/AAPL/?limit=500
        /api/v1/stocks/indicators/rsi/AAPL/?order=asc
        /api/v1/stocks/indicators/rsi/AAPL/?sort=timestamp
    """

    endpoint_from = EndpointFrom.STOCKS_INDICATOR_RSI
    endpoint_to = EndpointTo.Polygon.INDICATOR_RSI
    allowed_params = [PolygonParams.Common, PolygonParams.IndicatorCommon]


class IndicatorSMAView(PolygonBaseView):
    """
    Compute SMA indicator for a symbol using Polygon's indicators API.

    App path:
        /api/v1/stocks/indicators/sma/{stockTicker}/

    Provider path:
        /v1/indicators/sma/{stockTicker}

    Path parameters:
        stockTicker (str): Target stock ticker symbol.

    GET Parameters:
        expand_underlying (bool): Include underlying series.
        series_type (str): Series type.
        timestamp (str): Filter by timestamp.
        window (int): Window length.
        limit (int): Maximum number of results.
        order (str): Sort order.
        sort (str): Sort field.

    Examples:
        /api/v1/stocks/indicators/sma/AAPL/?window=20
        /api/v1/stocks/indicators/sma/AAPL/?series_type=close
        /api/v1/stocks/indicators/sma/AAPL/?timestamp=2024-01-02
        /api/v1/stocks/indicators/sma/AAPL/?expand_underlying=false
        /api/v1/stocks/indicators/sma/AAPL/?limit=500
        /api/v1/stocks/indicators/sma/AAPL/?order=asc
        /api/v1/stocks/indicators/sma/AAPL/?sort=timestamp
    """

    endpoint_from = EndpointFrom.STOCKS_INDICATOR_SMA
    endpoint_to = EndpointTo.Polygon.INDICATOR_SMA
    allowed_params = [PolygonParams.Common, PolygonParams.IndicatorCommon]


# class LastNBBOView(PolygonBaseView):
#     """
#     Return the last NBBO quote for a stock.
#
#     App path:
#         /api/v1/stocks/last-quote/{stocksTicker}/
#
#     Provider path:
#         /v2/last/nbbo/stocks/{stocksTicker}
#
#     Path parameters:
#         stocksTicker (str): Target stock ticker symbol.
#
#     GET Parameters:
#         None: Direct passthrough.
#     """
#     endpoint_from = EndpointFrom.STOCKS_LAST_NBBO
#     endpoint_to = EndpointTo.Polygon.LAST_NBBO


# class LastTradeView(PolygonBaseView):
#     """
#     Return the last trade for a stock.
#
#     App path:
#         /api/v1/stocks/last-trade/{stocksTicker}/
#
#     Provider path:
#         /v2/last/trade/stocks/{stocksTicker}
#
#     Path parameters:
#         stocksTicker (str): Target stock ticker symbol.
#
#     GET Parameters:
#         None: Direct passthrough.
#     """
#     endpoint_from = EndpointFrom.STOCKS_LAST_TRADE
#     endpoint_to = EndpointTo.Polygon.LAST_TRADE


class MarketHolidaysView(PolygonBaseView):
    """
    Return upcoming market holidays.

    App path:
        /api/v1/stocks/reference/market-holidays/

    Provider path:
        /v1/marketstatus/upcoming

    Path parameters:
        None.

    GET Parameters:
        None.
    """

    endpoint_from = EndpointFrom.STOCKS_REFERENCE_MARKET_HOLIDAYS
    endpoint_to = EndpointTo.Polygon.REFERENCE_MARKET_HOLIDAYS


class MarketStatusView(PolygonBaseView):
    """
    Return current market status (open/closed and session info).

    App path:
        /api/v1/stocks/reference/market-status/

    Provider path:
        /v1/marketstatus/now

    Path parameters:
        None.

    GET Parameters:
        None.
    """

    endpoint_from = EndpointFrom.STOCKS_REFERENCE_MARKET_STATUS
    endpoint_to = EndpointTo.Polygon.REFERENCE_MARKET_STATUS


class OpenCloseView(PolygonBaseView):
    """
    Return open/close and after-hours for a given date and stock.

    App path:
        /api/v1/stocks/open-close/{stocksTicker}/{date}/

    Provider path:
        /v1/open-close/{stocksTicker}/{date}

    Path parameters:
        stocksTicker (str): Target stock ticker symbol.
        date (str): Target date.

    GET Parameters:
        adjusted (bool): Whether results are adjusted.
        limit (int): Maximum number of results.
        order (str): Sort order.
        sort (str): Sort field.

    Examples:
        /api/v1/stocks/open-close/AAPL/2024-01-05/?adjusted=true
        /api/v1/stocks/open-close/AAPL/2024-01-05/?limit=1
        /api/v1/stocks/open-close/AAPL/2024-01-05/?order=asc
        /api/v1/stocks/open-close/AAPL/2024-01-05/?sort=symbol
    """

    endpoint_from = EndpointFrom.STOCKS_OPEN_CLOSE
    endpoint_to = EndpointTo.Polygon.OPEN_CLOSE
    allowed_params = [PolygonParams.Common, PolygonParams.OpenClose]


class QuotesView(PolygonBaseView):
    """
    Stream of quotes for a ticker (paginated via Polygon).

    App path:
        /api/v1/stocks/quotes/{stockTicker}/

    Provider path:
        /v3/quotes/{stockTicker}

    Path parameters:
        stockTicker (str): Target stock ticker symbol.

    GET Parameters:
        timestamp (str): Filter by timestamp.
        limit (int): Maximum number of results.
        order (str): Sort order.
        sort (str): Sort field.

    Examples:
        /api/v1/stocks/quotes/AAPL/?timestamp=2024-01-02T15:30:00Z
        /api/v1/stocks/quotes/AAPL/?limit=100
        /api/v1/stocks/quotes/AAPL/?order=asc
        /api/v1/stocks/quotes/AAPL/?sort=price
    """

    endpoint_from = EndpointFrom.STOCKS_QUOTES
    endpoint_to = EndpointTo.Polygon.QUOTES
    allowed_params = [PolygonParams.Common, PolygonParams.Quotes]


class ReferenceConditionsView(PolygonBaseView):
    """
    List reference trade/quote conditions.

    App path:
        /api/v1/stocks/reference/conditions/

    Provider path:
        /v3/reference/conditions

    Path parameters:
        None.

    GET Parameters:
        asset_class (str): Asset class filter.
        data_type (str): Data type filter.
        id (str): Condition identifier.
        sip (str): SIP filter.
        limit (int): Max results.
        order (str): Sort order.
        sort (str): Sort field.

    Examples:
        /api/v1/stocks/reference/conditions/?asset_class=stocks
        /api/v1/stocks/reference/conditions/?data_type=trade
        /api/v1/stocks/reference/conditions/?id=1
        /api/v1/stocks/reference/conditions/?sip=cta
        /api/v1/stocks/reference/conditions/?limit=100
        /api/v1/stocks/reference/conditions/?order=asc
        /api/v1/stocks/reference/conditions/?sort=id
    """

    endpoint_from = EndpointFrom.STOCKS_REFERENCE_CONDITIONS
    endpoint_to = EndpointTo.Polygon.REFERENCE_CONDITIONS
    allowed_params = [PolygonParams.Common, PolygonParams.ReferenceConditions]


class ReferenceDividendsView(PolygonBaseView):
    """
    List reference dividend events.

    App path:
        /api/v1/stocks/reference/dividends/

    Provider path:
        /v3/reference/dividends

    Path parameters:
        None.

    GET Parameters:
        cash_amount (str): Cash amount filter.
        declaration_date (str): Declaration date filter.
        dividend_type (str): Dividend type filter.
        ex_dividend_date (str): Ex-dividend date filter.
        frequency (str): Frequency filter.
        pay_date (str): Pay date filter.
        record_date (str): Record date filter.
        ticker (str): Ticker filter.
        limit (int): Max results.
        order (str): Sort order.
        sort (str): Sort field.

    Examples:
        /api/v1/stocks/reference/dividends/?ticker=AAPL
        /api/v1/stocks/reference/dividends/?cash_amount=0.24
        /api/v1/stocks/reference/dividends/?declaration_date=2024-01-01
        /api/v1/stocks/reference/dividends/?dividend_type=CD
        /api/v1/stocks/reference/dividends/?ex_dividend_date=2024-01-15
        /api/v1/stocks/reference/dividends/?frequency=quarterly
        /api/v1/stocks/reference/dividends/?pay_date=2024-02-01
        /api/v1/stocks/reference/dividends/?record_date=2024-01-20
        /api/v1/stocks/reference/dividends/?limit=50
        /api/v1/stocks/reference/dividends/?order=desc
        /api/v1/stocks/reference/dividends/?sort=pay_date
    """

    endpoint_from = EndpointFrom.STOCKS_REFERENCE_DIVIDENDS
    endpoint_to = EndpointTo.Polygon.REFERENCE_DIVIDENDS
    allowed_params = [PolygonParams.Common, PolygonParams.ReferenceDividends]


class ReferenceExchangesView(PolygonBaseView):
    """
    List stock exchanges supported by Polygon.

    App path:
        /api/v1/stocks/reference/exchanges/

    Provider path:
        /v3/reference/exchanges

    Path parameters:
        None.

    GET Parameters:
        asset_class (str): Asset class filter.
        locale (str): Locale filter.
        limit (int): Max results.
        order (str): Sort order.
        sort (str): Sort field.

    Examples:
        /api/v1/stocks/reference/exchanges/?asset_class=stocks
        /api/v1/stocks/reference/exchanges/?locale=us
        /api/v1/stocks/reference/exchanges/?limit=50
        /api/v1/stocks/reference/exchanges/?order=asc
        /api/v1/stocks/reference/exchanges/?sort=mic
    """

    endpoint_from = EndpointFrom.STOCKS_REFERENCE_EXCHANGES
    endpoint_to = EndpointTo.Polygon.REFERENCE_EXCHANGES
    allowed_params = [PolygonParams.Common, PolygonParams.ReferenceExchanges]


class ReferenceFinancialsView(PolygonBaseView):
    """
    List standardized financials with extensive filters.

    App path:
        /api/v1/stocks/reference/financials/

    Provider path:
        /vX/reference/financials

    Path parameters:
        None.

    GET Parameters:
        cik (str): SEC CIK.
        company_name (str): Company name filter.
        filing_date (str): Filing date filter.
        include_sources (bool): Include sources.
        period_of_report_date (str): Report date filter.
        sic (str): SIC filter.
        ticker (str): Ticker filter.
        timeframe (str): Timeframe filter.
        limit (int): Max results.
        order (str): Sort order.
        sort (str): Sort field.

    Examples:
        /api/v1/stocks/reference/financials/?cik=0000320193
        /api/v1/stocks/reference/financials/?company_name=Apple
        /api/v1/stocks/reference/financials/?filing_date=2024-01-01
        /api/v1/stocks/reference/financials/?include_sources=true
        /api/v1/stocks/reference/financials/?period_of_report_date=2023-12-31
        /api/v1/stocks/reference/financials/?sic=3571
        /api/v1/stocks/reference/financials/?ticker=AAPL
        /api/v1/stocks/reference/financials/?timeframe=quarterly
        /api/v1/stocks/reference/financials/?limit=100
        /api/v1/stocks/reference/financials/?order=asc
        /api/v1/stocks/reference/financials/?sort=filing_date
    """

    endpoint_from = EndpointFrom.STOCKS_REFERENCE_FINANCIALS
    endpoint_to = EndpointTo.Polygon.REFERENCE_FINANCIALS
    allowed_params = [PolygonParams.Common, PolygonParams.ReferenceFinancials]


# class ReferenceIPOsView(PolygonBaseView):
#     """
#     List IPOs with filters.
#
#     App path:
#         /api/v1/stocks/reference/ipos/
#
#     Provider path:
#         /v3/reference/ipos
#
#     Path parameters:
#         None.
#
#     GET Parameters:
#         isin (str): ISIN filter.
#         ticker (str): Ticker filter.
#         us_code (str): US code filter.
#         listing_date (str): Listing date filter.
#         limit (int): Max results.
#         order (str): Sort order.
#         sort (str): Sort field.
#
#     Examples:
#         /api/v1/stocks/reference/ipos/?ticker=AAPL
#         /api/v1/stocks/reference/ipos/?isin=US0378331005
#         /api/v1/stocks/reference/ipos/?us_code=US
#         /api/v1/stocks/reference/ipos/?listing_date=2024-01-05
#         /api/v1/stocks/reference/ipos/?limit=50
#         /api/v1/stocks/reference/ipos/?order=desc
#         /api/v1/stocks/reference/ipos/?sort=listing_date
#     """
#     endpoint_from = EndpointFrom.STOCKS_REFERENCE_IPOS
#     endpoint_to = EndpointTo.Polygon.REFERENCE_IPOS
#     allowed_params = [PolygonParams.Common, PolygonParams.ReferenceIPOs]


class ReferenceNewsView(PolygonBaseView):
    """
    List reference news items.

    App path:
        /api/v1/stocks/reference/news/

    Provider path:
        /v2/reference/news

    Path parameters:
        None.

    GET Parameters:
        published_utc (str): Publish time filter.
        ticker (str): Ticker filter.
        limit (int): Max results.
        order (str): Sort order.
        sort (str): Sort field.

    Examples:
        /api/v1/stocks/reference/news/?ticker=AAPL
        /api/v1/stocks/reference/news/?published_utc=2024-01-01
        /api/v1/stocks/reference/news/?limit=50
        /api/v1/stocks/reference/news/?order=desc
        /api/v1/stocks/reference/news/?sort=published_utc
    """

    endpoint_from = EndpointFrom.STOCKS_REFERENCE_NEWS
    endpoint_to = EndpointTo.Polygon.REFERENCE_NEWS
    allowed_params = [PolygonParams.Common, PolygonParams.ReferenceNews]


class ReferenceSplitsView(PolygonBaseView):
    """
    List reference split events.

    App path:
        /api/v1/stocks/reference/splits/

    Provider path:
        /v3/reference/splits

    Path parameters:
        None.

    GET Parameters:
        execution_date (str): Execution date filter.
        reverse_split (bool): Reverse split filter.
        ticker (str): Ticker filter.
        limit (int): Max results.
        order (str): Sort order.
        sort (str): Sort field.

    Examples:
        /api/v1/stocks/reference/splits/?ticker=AAPL
        /api/v1/stocks/reference/splits/?execution_date=2020-08-31
        /api/v1/stocks/reference/splits/?reverse_split=false
        /api/v1/stocks/reference/splits/?limit=100
        /api/v1/stocks/reference/splits/?order=asc
        /api/v1/stocks/reference/splits/?sort=execution_date
    """

    endpoint_from = EndpointFrom.STOCKS_REFERENCE_SPLITS
    endpoint_to = EndpointTo.Polygon.REFERENCE_SPLITS
    allowed_params = [PolygonParams.Common, PolygonParams.ReferenceSplits]


class ReferenceTickerEventsView(PolygonBaseView):
    """
    List corporate events for a ticker.

    App path:
        /api/v1/stocks/reference/tickers/{id}/events/

    Provider path:
        /vX/reference/tickers/{id}/events

    Path parameters:
        id (str): Ticker identifier.

    GET Parameters:
        types (str): Event types filter.
        limit (int): Max results.
        order (str): Sort order.
        sort (str): Sort field.

    Examples:
        /api/v1/stocks/reference/tickers/1234/events/?types=dividend
        /api/v1/stocks/reference/tickers/1234/events/?limit=100
        /api/v1/stocks/reference/tickers/1234/events/?order=desc
        /api/v1/stocks/reference/tickers/1234/events/?sort=event_date
    """

    endpoint_from = EndpointFrom.STOCKS_REFERENCE_TICKER_EVENTS
    endpoint_to = EndpointTo.Polygon.REFERENCE_TICKER_EVENTS
    allowed_params = [PolygonParams.Common, PolygonParams.ReferenceTickerEvents]


class ReferenceTickerTypesView(PolygonBaseView):
    """
    List available ticker types.

    App path:
        /api/v1/stocks/reference/tickers/types/

    Provider path:
        /v3/reference/tickers/types

    Path parameters:
        None.

    GET Parameters:
        asset_class (str): Asset class filter.
        locale (str): Locale filter.
        limit (int): Max results.
        order (str): Sort order.
        sort (str): Sort field.

    Examples:
        /api/v1/stocks/reference/tickers/types/?asset_class=stocks
        /api/v1/stocks/reference/tickers/types/?locale=us
        /api/v1/stocks/reference/tickers/types/?limit=100
        /api/v1/stocks/reference/tickers/types/?order=asc
        /api/v1/stocks/reference/tickers/types/?sort=locale
    """

    endpoint_from = EndpointFrom.STOCKS_REFERENCE_TICKER_TYPES
    endpoint_to = EndpointTo.Polygon.REFERENCE_TICKER_TYPES
    allowed_params = [PolygonParams.Common, PolygonParams.ReferenceTickerTypes]


class ReferenceTickerView(PolygonBaseView):
    """
    Return reference information for a single ticker.

    App path:
        /api/v1/stocks/reference/tickers/{ticker}/

    Provider path:
        /v3/reference/tickers/{ticker}

    Path parameters:
        ticker (str): Ticker symbol.

    GET Parameters:
        date (str): As-of date.
        limit (int): Max results.
        order (str): Sort order.
        sort (str): Sort field.

    Examples:
        /api/v1/stocks/reference/tickers/AAPL/?date=2024-01-01
        /api/v1/stocks/reference/tickers/AAPL/?limit=1
        /api/v1/stocks/reference/tickers/AAPL/?order=asc
        /api/v1/stocks/reference/tickers/AAPL/?sort=ticker
    """

    endpoint_from = EndpointFrom.STOCKS_REFERENCE_TICKER
    endpoint_to = EndpointTo.Polygon.REFERENCE_TICKER
    allowed_params = [PolygonParams.Common, PolygonParams.ReferenceTicker]


class ReferenceTickersView(PolygonBaseView):
    """
    Search and list tickers with extensive filters.

    App path:
        /api/v1/stocks/reference/tickers/

    Provider path:
        /v3/reference/tickers

    Path parameters:
        None.

    GET Parameters:
        active (bool): Active flag.
        cik (str): SEC CIK.
        cusip (str): CUSIP.
        date (str): As-of date.
        exchange (str): Exchange filter.
        market (str): Market filter.
        search (str): Text search.
        ticker (str): Ticker filter.
        type (str): Type filter.
        limit (int): Max results.
        order (str): Sort order.
        sort (str): Sort field.

    Examples:
        /api/v1/stocks/reference/tickers/?active=true
        /api/v1/stocks/reference/tickers/?cik=0000320193
        /api/v1/stocks/reference/tickers/?cusip=037833100
        /api/v1/stocks/reference/tickers/?date=2024-01-01
        /api/v1/stocks/reference/tickers/?exchange=XNAS
        /api/v1/stocks/reference/tickers/?market=stocks
        /api/v1/stocks/reference/tickers/?search=Apple
        /api/v1/stocks/reference/tickers/?ticker=AAPL
        /api/v1/stocks/reference/tickers/?type=CS
        /api/v1/stocks/reference/tickers/?limit=50
        /api/v1/stocks/reference/tickers/?order=asc
        /api/v1/stocks/reference/tickers/?sort=ticker
    """

    endpoint_from = EndpointFrom.STOCKS_REFERENCE_TICKERS
    endpoint_to = EndpointTo.Polygon.REFERENCE_TICKERS
    allowed_params = [PolygonParams.Common, PolygonParams.ReferenceTickers]


class RelatedCompaniesView(PolygonBaseView):
    """
    Return related companies for a given ticker.

    App path:
        /api/v1/stocks/related-companies/{ticker}/

    Provider path:
        /v1/related-companies/{ticker}

    Path parameters:
        ticker (str): Ticker symbol.

    GET Parameters:
        None.
    """

    endpoint_from = EndpointFrom.STOCKS_RELATED_COMPANIES
    endpoint_to = EndpointTo.Polygon.RELATED_COMPANIES


class SnapshotMarketView(PolygonBaseView):
    """
    Return snapshots for many tickers in the market.

    App path:
        /api/v1/stocks/snapshot/tickers/

    Provider path:
        /v2/snapshot/locale/us/markets/stocks/tickers

    Path parameters:
        None.

    GET Parameters:
        include_otc (bool): Include OTC.
        tickers (str): Comma separated tickers.
        limit (int): Max results.
        order (str): Sort order.
        sort (str): Sort field.

    Examples:
        /api/v1/stocks/snapshot/tickers/?include_otc=false
        /api/v1/stocks/snapshot/tickers/?tickers=AAPL,MSFT
        /api/v1/stocks/snapshot/tickers/?limit=50
        /api/v1/stocks/snapshot/tickers/?order=desc
        /api/v1/stocks/snapshot/tickers/?sort=price
    """

    endpoint_from = EndpointFrom.STOCKS_SNAPSHOT_MARKET
    endpoint_to = EndpointTo.Polygon.SNAPSHOT_MARKET
    allowed_params = [PolygonParams.Common, PolygonParams.SnapshotMarket]


class SnapshotMoversView(PolygonBaseView):
    """
    Return top gainers or losers snapshots.

    App path:
        /api/v1/stocks/snapshot/movers/{direction}/

    Provider path:
        /v2/snapshot/locale/us/markets/stocks/{direction}

    Path parameters:
        direction (str): movers direction (gainers|losers).

    GET Parameters:
        include_otc (bool): Include OTC.
        limit (int): Max results.
        order (str): Sort order.
        sort (str): Sort field.

    Examples:
        /api/v1/stocks/snapshot/movers/gainers/?include_otc=false
        /api/v1/stocks/snapshot/movers/gainers/?limit=20
        /api/v1/stocks/snapshot/movers/gainers/?order=desc
        /api/v1/stocks/snapshot/movers/gainers/?sort=change
    """

    endpoint_from = EndpointFrom.STOCKS_SNAPSHOT_MOVERS
    endpoint_to = EndpointTo.Polygon.SNAPSHOT_MOVERS
    allowed_params = [PolygonParams.Common, PolygonParams.SnapshotMovers]


class SnapshotTickerView(PolygonBaseView):
    """
    Return snapshot for a single ticker.

    App path:
        /api/v1/stocks/snapshot/tickers/{stocksTicker}/

    Provider path:
        /v2/snapshot/locale/us/markets/stocks/tickers/{stocksTicker}

    Path parameters:
        stocksTicker (str): Ticker symbol.

    GET Parameters:
        None.
    """

    endpoint_from = EndpointFrom.STOCKS_SNAPSHOT_TICKER
    endpoint_to = EndpointTo.Polygon.SNAPSHOT_TICKER


class SnapshotUnifiedView(PolygonBaseView):
    """
    Return unified snapshot data (multi-asset) per Polygon.

    App path:
        /api/v1/snapshot/

    Provider path:
        /v3/snapshot

    Path parameters:
        None.

    GET Parameters:
        ticker (str): Ticker filter.
        type (str): Asset type filter.
        limit (int): Max results.
        order (str): Sort order.
        sort (str): Sort field.

    Examples:
        /api/v1/snapshot/?ticker=AAPL
        /api/v1/snapshot/?type=stocks
        /api/v1/snapshot/?limit=50
        /api/v1/snapshot/?order=desc
        /api/v1/snapshot/?sort=volume
    """

    endpoint_from = EndpointFrom.STOCKS_SNAPSHOT_UNIFIED
    endpoint_to = EndpointTo.Polygon.SNAPSHOT_UNIFIED
    allowed_params = [PolygonParams.Common, PolygonParams.SnapshotUnified]


class StocksShortInterestView(PolygonBaseView):
    """
    Return short interest metrics.

    App path:
        /api/v1/stocks/short-interest/

    Provider path:
        /stocks/v1/short-interest

    Path parameters:
        None.

    GET Parameters:
        avg_daily_volume (int): Average daily volume.
        days_to_cover (float): Days to cover.
        settlement_date (str): Settlement date.
        ticker (str): Ticker filter.
        limit (int): Max results.
        order (str): Sort order.
        sort (str): Sort field.

    Examples:
        /api/v1/stocks/short-interest/?ticker=AAPL
        /api/v1/stocks/short-interest/?avg_daily_volume=1000000
        /api/v1/stocks/short-interest/?days_to_cover=2.5
        /api/v1/stocks/short-interest/?settlement_date=2024-01-15
        /api/v1/stocks/short-interest/?limit=50
        /api/v1/stocks/short-interest/?order=asc
        /api/v1/stocks/short-interest/?sort=settlement_date
    """

    endpoint_from = EndpointFrom.STOCKS_SHORT_INTEREST
    endpoint_to = EndpointTo.Polygon.STOCKS_SHORT_INTEREST
    allowed_params = [PolygonParams.Common, PolygonParams.StocksShortInterest]


class StocksShortVolumeView(PolygonBaseView):
    """
    Return FINRA short volume by day.

    App path:
        /api/v1/stocks/short-volume/

    Provider path:
        /stocks/v1/short-volume

    Path parameters:
        None.

    GET Parameters:
        date (str): Target date.
        short_volume_ratio (float): Ratio filter.
        ticker (str): Ticker filter.
        total_volume (int): Total volume filter.
        limit (int): Max results.
        order (str): Sort order.
        sort (str): Sort field.

    Examples:
        /api/v1/stocks/short-volume/?ticker=AAPL
        /api/v1/stocks/short-volume/?date=2024-01-05
        /api/v1/stocks/short-volume/?short_volume_ratio=0.25
        /api/v1/stocks/short-volume/?total_volume=10000000
        /api/v1/stocks/short-volume/?limit=50
        /api/v1/stocks/short-volume/?order=asc
        /api/v1/stocks/short-volume/?sort=date
    """

    endpoint_from = EndpointFrom.STOCKS_SHORT_VOLUME
    endpoint_to = EndpointTo.Polygon.STOCKS_SHORT_VOLUME
    allowed_params = [PolygonParams.Common, PolygonParams.StocksShortVolume]


class TradesView(PolygonBaseView):
    """
    Return trade prints for a given ticker.

    App path:
        /api/v1/stocks/trades/{stockTicker}/

    Provider path:
        /v3/trades/{stockTicker}

    Path parameters:
        stockTicker (str): Ticker symbol.

    GET Parameters:
        timestamp (str): Timestamp filter.
        limit (int): Max results.
        order (str): Sort order.
        sort (str): Sort field.

    Examples:
        /api/v1/stocks/trades/AAPL/?timestamp=2024-01-02T15:30:00Z
        /api/v1/stocks/trades/AAPL/?limit=100
        /api/v1/stocks/trades/AAPL/?order=asc
        /api/v1/stocks/trades/AAPL/?sort=timestamp
    """

    endpoint_from = EndpointFrom.STOCKS_TRADES
    endpoint_to = EndpointTo.Polygon.TRADES
    allowed_params = [PolygonParams.Common, PolygonParams.Trades]
