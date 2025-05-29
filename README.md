# Django Polygon.io Proxy Service

A simple and efficient Django REST API proxy service that forwards all HTTP requests to Polygon.io API with JWT authentication.

## Features

- JWT Authentication
- Direct request forwarding to Polygon.io
- Preserves all query parameters
- Maintains original response structure
- Simple setup and configuration
- Support for all Polygon.io endpoints (v1, v2, v3)
- Version-specific routing
- Proper error handling

## Prerequisites

- Python 3.8+
- UV (Python package installer)

## Installation

1. Clone the repository:
```bash
git clone git@github.com:iklobato/proxy_project.git
cd proxy_project
```

2. Create a virtual environment and install dependencies:
```bash
uv venv
source .venv/bin/activate
uv pip install -r requirements.txt
```

3. Run migrations:
```bash
uv run ./manage.py migrate
```

4. Create a superuser:
```bash
uv run ./manage.py createsuperuser
```

## Configuration

The service uses the following environment variables:
- `POLYGON_API_KEY`: Your Polygon.io API key
- `SECRET_KEY`: Django secret key
- `DEBUG`: Debug mode (True/False)
- `ALLOWED_HOSTS`: Comma-separated list of allowed hosts
- `ENV`: Environment (local/staging/production)

## Usage

1. Start the development server:
```bash
ENV=local uv run ./manage.py runserver
```

2. Get a JWT token:
```bash
curl -X POST http://localhost:8000/api/token/ \
  -H "Content-Type: application/json" \
  -d '{"username": "your_username", "password": "your_password"}'
```

## Available Endpoints

All endpoints use the `/v1/` prefix and are automatically mapped to the appropriate Polygon.io API version internally.

### Authentication Endpoints

```bash
POST /api/token/              # Get JWT token
POST /api/token/refresh/      # Refresh JWT token
POST /api/token/verify/       # Verify JWT token
```

### Stocks Endpoints

1. Reference Data:
```bash
GET /v1/reference/tickers
    ?market=stocks
    &active=true
    &order=asc
    &limit=100
    &sort=ticker             # List all stock tickers

GET /v1/reference/tickers/AAPL  # Get details for a specific ticker

GET /v1/related-companies/AAPL  # Get related companies for a ticker
```

2. Market Data:
```bash
# Aggregates (OHLC)
GET /v1/aggs/ticker/AAPL/range/1/day/2023-01-09/2023-02-10
    ?adjusted=true
    &sort=asc
    &limit=120              # Get daily aggregates for AAPL

GET /v1/aggs/ticker/AAPL/prev
    ?adjusted=true          # Get previous day's data

# Snapshots
GET /v1/snapshot/stocks/tickers/AAPL  # Single stock snapshot
GET /v1/snapshot/stocks/tickers       # Full market snapshot
GET /v1/snapshot                      # Unified market snapshot
GET /v1/snapshot/stocks/gainers       # Market gainers

# Real-time Quotes
GET /v1/trades/AAPL              # Get trades
GET /v1/last/trade/AAPL         # Get last trade
GET /v1/quotes/AAPL             # Get quotes
GET /v1/last/nbbo/AAPL          # Get last quote
```

### Options Endpoints

```bash
GET /v1/reference/options/contracts
    ?order=asc
    &limit=10
    &sort=ticker             # List all option contracts
```

### Indices Endpoints

```bash
GET /v1/reference/tickers
    ?market=indices
    &active=true
    &order=asc
    &limit=100
    &sort=ticker             # List all indices

GET /v1/reference/tickers/I:SPX  # Get details for S&P 500
```

### Forex Endpoints

```bash
GET /v1/reference/tickers
    ?market=fx
    &active=true
    &order=asc
    &limit=100
    &sort=ticker             # List all forex pairs

GET /v1/conversion/AUD/USD
    ?amount=100
    &precision=2             # Currency conversion
```

### Crypto Endpoints

```bash
GET /v1/reference/tickers
    ?market=crypto
    &active=true
    &order=asc
    &limit=100
    &sort=ticker             # List all crypto pairs
```

### Economy Endpoints

```bash
GET /v1/fed/vx/treasury-yields  # Get treasury yields data
```

### Partners Endpoints

```bash
GET /v1/benzinga/v1/ratings     # Get Benzinga analyst ratings
```

### Technical Indicators

```bash
GET /v1/indicators/rsi/AAPL
    ?timespan=day
    &window=14
    &series_type=close       # Get RSI for AAPL
```

## Response Formats

### Stocks Response Example
```json
{
  "results": {
    "ticker": "AAPL",
    "name": "Apple Inc.",
    "market": "stocks",
    "locale": "us",
    "primary_exchange": "XNAS",
    "type": "CS",
    "active": true,
    "currency_name": "usd",
    "cik": "0000320193",
    "composite_figi": "BBG000B9XRY4",
    "share_class_figi": "BBG001S5N8V8",
    "market_cap": 2952828995600
  },
  "status": "OK",
  "request_id": "6a7e466b6837652eca4def2f7b7adc56"
}
```

### Aggregates Response Example
```json
{
  "ticker": "AAPL",
  "adjusted": true,
  "queryCount": 23,
  "resultsCount": 23,
  "status": "OK",
  "results": [
    {
      "v": 64285687,
      "vw": 130.8365,
      "o": 130.465,
      "c": 130.73,
      "h": 133.41,
      "l": 129.89,
      "t": 1673251200000,
      "n": 691290
    }
  ]
}
```

## Important Notes

1. **API Key**: The proxy service automatically adds your configured API key to requests.

2. **Authentication**: 
   - All requests require a valid JWT token in the Authorization header in non-local environments
   - In local environment (ENV=local), no authentication is required

3. **Response Format**: The proxy service maintains Polygon.io's original response structure.

4. **Version Mapping**: All endpoints use `/v1/` prefix which maps internally to:
   - v3: Most modern endpoints (default)
   - v2: Aggregates, snapshots, and some reference data
   - v1: Legacy endpoints (open-close, meta/symbols, etc.)

5. **Rate Limiting**: The service respects Polygon.io's rate limits.

## Error Handling

The proxy service handles various error scenarios:
- 504: Gateway Timeout (when Polygon.io request times out)
- 502: Bad Gateway (when unable to reach Polygon.io)
- 500: Internal Server Error (for unexpected errors)
- 404: Not Found (when endpoint doesn't exist)
- 401: Unauthorized (when JWT token is invalid or missing)

## Security

- JWT Authentication required for all endpoints (except in local environment)
- API keys are never exposed to clients
- Secure headers configuration
- Environment-based authentication

## License

This project is licensed under the MIT License - see the LICENSE file for details. 