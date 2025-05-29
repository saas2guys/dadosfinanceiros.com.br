# Django Polygon.io Proxy Service

A simple and efficient Django REST API proxy service that forwards all HTTP requests to Polygon.io API with JWT authentication and request token validation.

## Features

- JWT Authentication for user management
- Request Token authentication for API access
- Daily request limits per user
- Direct request forwarding to Polygon.io
- Preserves all query parameters
- Maintains original response structure
- Simple setup and configuration
- Support for all Polygon.io endpoints (v1, v2, v3)
- Version-specific routing
- Proper error handling
- **Django REST Framework Authentication System**
- **Custom Authentication and Permission Classes**
- **Clean Separation of Concerns**

## Architecture Overview

### Django REST Framework Integration

The service has been refactored to use Django REST Framework's built-in authentication and permission system instead of custom middleware. This provides:

#### Benefits of the New Architecture:
- **Separation of Concerns**: Authentication, permissions, and business logic are properly separated
- **DRF Best Practices**: Uses standard DRF authentication and permission classes
- **Maintainability**: Easier to maintain, test, and extend
- **Performance**: More efficient than middleware-based authentication
- **Flexibility**: Supports multiple authentication methods simultaneously
- **Standards Compliance**: Follows Django and DRF conventions

#### Authentication Classes:

1. **`RequestTokenAuthentication`** (`users/authentication.py`):
   - Custom DRF authentication class for request token validation
   - Handles `X-Request-Token` header authentication
   - Validates token expiration and user status
   - Provides user context for authenticated requests

2. **`JWTAuthentication`** (from DRF Simple JWT):
   - Standard JWT token authentication
   - Used for user management endpoints (`/api/*`)
   - Bearer token authentication via Authorization header

#### Permission Classes:

1. **`DailyLimitPermission`** (`users/permissions.py`):
   - Custom DRF permission class for daily request limits
   - Checks if user has exceeded daily quota
   - Automatically resets counters for new days
   - Increments request count on successful requests

2. **`IsAuthenticated`** (from DRF):
   - Standard DRF permission for authenticated users
   - Used in combination with custom permissions

#### View Configuration:

The `PolygonProxyView` now dynamically configures authentication based on environment:

```python
def _set_authentication(self):
    """Set authentication and permission classes based on environment."""
    if settings.ENV != "local":
        # Production: Dual authentication support
        self.authentication_classes = [JWTAuthentication, RequestTokenAuthentication]
        self.permission_classes = [IsAuthenticated, DailyLimitPermission]
    else:
        # Development: Open access
        self.authentication_classes = []
        self.permission_classes = [AllowAny]
```

#### What Was Removed:

- **`RequestTokenMiddleware`**: All middleware logic moved to DRF authentication
- **Custom Routing Logic**: Now handled by Django URL patterns and DRF views
- **Manual Token Validation**: Now handled by DRF authentication classes
- **Hardcoded Path Checking**: Replaced with proper view-level authentication

#### Migration Benefits:

1. **Code Quality**:
   - Cleaner, more maintainable codebase
   - Follows Django/DRF best practices
   - Better error handling and debugging

2. **Testability**:
   - Easier to unit test authentication logic
   - DRF test utilities for API testing
   - Isolated authentication components

3. **Flexibility**:
   - Easy to add new authentication methods
   - Configurable per-view authentication
   - Support for different permission levels

4. **Performance**:
   - More efficient than middleware processing
   - Only authenticates relevant requests
   - Better caching of authentication results

### Migration Guide

#### For Existing Users

If you're upgrading from a previous version that used `RequestTokenMiddleware`, here's what changed:

##### What Remains the Same:
- **API Endpoints**: All endpoints work exactly the same
- **Authentication Headers**: Same headers (`X-Request-Token`, `Authorization: Bearer`)
- **Token Management**: Same token generation and management features
- **Daily Limits**: Same daily request limit functionality
- **User Experience**: No changes to how you use the API

##### What Changed (Internal):
- **Middleware Removed**: `RequestTokenMiddleware` no longer exists
- **DRF Integration**: Now uses Django REST Framework authentication classes
- **Better Error Handling**: More consistent error responses
- **Improved Testing**: Better test coverage and utilities

##### No Action Required:
- **Existing Tokens**: All existing request tokens continue to work
- **Client Code**: No changes needed to your API client code
- **Configuration**: Same environment variables and settings

#### For Developers

If you were customizing the authentication logic:

##### Before (Middleware Approach):
```python
# users/middleware.py - REMOVED
class RequestTokenMiddleware:
    def __call__(self, request):
        # Custom authentication logic in middleware
        pass
```

##### After (DRF Approach):
```python
# users/authentication.py - NEW
class RequestTokenAuthentication(authentication.BaseAuthentication):
    def authenticate(self, request):
        # Authentication logic in DRF class
        return (user, token)

# users/permissions.py - NEW  
class DailyLimitPermission(permissions.BasePermission):
    def has_permission(self, request, view):
        # Permission logic in DRF class
        return True
```

##### Benefits for Developers:
- **Testable**: Easier to unit test authentication logic
- **Modular**: Clean separation between authentication and permissions
- **Extensible**: Easy to add new authentication methods
- **Standard**: Follows Django/DRF best practices
- **Debuggable**: Better error messages and debugging tools

#### Deployment Notes

##### Production Deployment:
1. **Update Code**: Pull the latest code with DRF authentication
2. **Run Migrations**: `python manage.py migrate` (if any new migrations)
3. **Restart Service**: Restart your Django application
4. **Test**: Verify authentication works with existing tokens

##### No Database Changes:
- No database migrations required for this refactoring
- All existing user accounts and tokens remain valid
- No downtime required for the upgrade

##### Environment Variables:
All existing environment variables remain the same:
- `POLYGON_API_KEY`
- `SECRET_KEY` 
- `DEBUG`
- `ALLOWED_HOSTS`
- `ENV`

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

## Authentication Flow

The service uses a two-step authentication process with Django REST Framework:

### 1. JWT Authentication (User Management)
- **Purpose**: User registration, login, and profile management
- **Endpoints**: `/api/*` routes
- **Method**: Bearer token in `Authorization` header
- **Token Lifetime**: 60 minutes (configurable)
- **Handled By**: `JWTAuthentication` class (DRF Simple JWT)

### 2. Request Token Authentication (API Access)
- **Purpose**: Accessing Polygon.io data via proxy endpoints
- **Endpoints**: `/v1/*` routes (proxy endpoints)
- **Method**: Custom token in `X-Request-Token` header
- **Token Lifetime**: 30 days (configurable, with auto-renewal options)
- **Handled By**: `RequestTokenAuthentication` class (custom DRF authentication)

### Authentication Architecture

#### Production Environment (`ENV != "local"`):
```python
# PolygonProxyView authentication configuration
authentication_classes = [JWTAuthentication, RequestTokenAuthentication]
permission_classes = [IsAuthenticated, DailyLimitPermission]
```

- **Dual Authentication**: Supports both JWT and request tokens
- **Daily Limits**: Enforced via `DailyLimitPermission`
- **User Context**: Both authentication methods provide user context

#### Development Environment (`ENV == "local"`):
```python
# PolygonProxyView authentication configuration  
authentication_classes = []
permission_classes = [AllowAny]
```

- **Open Access**: No authentication required for development
- **Easy Testing**: Simplifies local development and testing

### DRF Authentication Process

1. **Request Reception**:
   ```
   Client Request → Django URLs → PolygonProxyView
   ```

2. **Authentication Phase**:
   ```
   DRF Authentication Classes:
   ├── JWTAuthentication.authenticate(request)
   └── RequestTokenAuthentication.authenticate(request)
   ```

3. **Permission Check**:
   ```
   DRF Permission Classes:
   ├── IsAuthenticated.has_permission()
   └── DailyLimitPermission.has_permission()
   ```

4. **Request Processing**:
   ```
   Authentication Success → Proxy to Polygon.io → Return Response
   ```

### Authentication Headers

#### For JWT Authentication:
```http
Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...
```

#### For Request Token Authentication:
```http
X-Request-Token: 550e8400-e29b-41d4-a716-446655440000
```

### Getting Started

1. Register a new user:
```bash
# Request
curl -X POST http://localhost:8000/api/register/ \
  -H "Content-Type: application/json" \
  -d '{
    "email": "your.email@example.com",
    "password": "your_password",
    "password2": "your_password",
    "first_name": "John",
    "last_name": "Doe"
  }'

# Response
{
    "id": 1,
    "email": "your.email@example.com",
    "first_name": "John",
    "last_name": "Doe",
    "request_token": "550e8400-e29b-41d4-a716-446655440000",
    "daily_request_limit": 100,
    "daily_requests_made": 0,
    "last_request_date": null
}
```

2. Get JWT token:
```bash
# Request
curl -X POST http://localhost:8000/api/token/ \
  -H "Content-Type: application/json" \
  -d '{
    "email": "your.email@example.com",
    "password": "your_password"
  }'

# Response
{
    "access": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
    "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
}
```

3. Get your profile and request token:
```bash
# Request
curl -X GET http://localhost:8000/api/profile/ \
  -H "Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."

# Response
{
    "id": 1,
    "email": "your.email@example.com",
    "first_name": "John",
    "last_name": "Doe",
    "request_token": "550e8400-e29b-41d4-a716-446655440000",
    "daily_request_limit": 100,
    "daily_requests_made": 0,
    "last_request_date": null
}
```

4. Use the request token for API calls:
```bash
# Request
curl -X GET http://localhost:8000/v1/stocks/AAPL \
  -H "X-Request-Token: 550e8400-e29b-41d4-a716-446655440000"

# Response
{
    "status": "OK",
    "results": {
        "ticker": "AAPL",
        "name": "Apple Inc.",
        "market": "stocks",
        "locale": "us",
        "primary_exchange": "NASDAQ",
        "type": "CS",
        "active": true,
        "currency_name": "usd",
        "cik": "0000320193",
        "composite_figi": "BBG000B9XRY4",
        "share_class_figi": "BBG001S5N8V8",
        "market_cap": 2952828995600
    },
    "request_id": "6a7e466b6837652eca4def2f7b7adc56"
}
```

5. Check your daily usage:
```bash
# Request
curl -X GET http://localhost:8000/api/profile/ \
  -H "Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."

# Response
{
    "id": 1,
    "email": "your.email@example.com",
    "first_name": "John",
    "last_name": "Doe",
    "request_token": "550e8400-e29b-41d4-a716-446655440000",
    "daily_request_limit": 100,
    "daily_requests_made": 1,
    "last_request_date": "2024-03-20"
}
```

6. Regenerate request token if needed:
```bash
# Request
curl -X POST http://localhost:8000/api/regenerate-token/ \
  -H "Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."

# Response
{
    "request_token": "661f9511-f3ab-52e5-b827-557766551111"
}
```

### Error Responses

1. Invalid Request Token:
```json
{
    "error": "Invalid request token",
    "status": 401
}
```

2. Daily Limit Exceeded:
```json
{
    "error": "Daily request limit exceeded",
    "status": 429
}
```

3. Expired JWT Token:
```json
{
    "detail": "Token has expired",
    "code": "token_not_valid",
    "status": 401
}
```

4. Missing Request Token:
```json
{
    "error": "Request token is required",
    "status": 401
}
```

### Advanced Authentication Flow

1. **Initial Registration**:
   ```mermaid
   sequenceDiagram
       Client->>Server: POST /api/register/
       Server->>Server: Create user & generate token
       Server->>Client: Return user details & token
   ```

2. **Token Authentication**:
   ```mermaid
   sequenceDiagram
       Client->>Server: POST /api/token/
       Server->>Server: Validate credentials
       Server->>Client: Return JWT tokens
   ```

3. **API Access**:
   ```mermaid
   sequenceDiagram
       Client->>Server: GET /v1/* with request token
       Server->>Server: Validate token & limits
       Server->>Polygon: Forward request
       Polygon->>Server: Return data
       Server->>Client: Return response
   ```

4. **Token Renewal**:
   ```mermaid
   sequenceDiagram
       Client->>Server: POST /api/regenerate-token/
       Server->>Server: Generate new token
       Server->>Server: Update history
       Server->>Client: Return new token
   ```

### Token Management Features

The service includes advanced token management capabilities:

1. **Token Expiration**:
   - Configurable validity period (default 30 days)
   - Automatic expiration checking
   - Optional auto-renewal
   - Graceful expiration handling

2. **Token History**:
   - Tracks previous tokens
   - Stores creation and expiration dates
   - Maintains history of last 5 tokens
   - Audit trail for security

3. **Token Settings**:
   - Auto-renewal configuration
   - Customizable validity period
   - Option to save or discard old tokens
   - Per-user configuration

#### Token Management Examples

1. Generate new token with custom settings:
```bash
# Request
curl -X POST http://localhost:8000/api/regenerate-token/ \
  -H "Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..." \
  -H "Content-Type: application/json" \
  -d '{
    "save_old": true,
    "auto_renew": true,
    "validity_days": 60
  }'

# Response
{
    "request_token": "661f9511-f3ab-52e5-b827-557766551111",
    "created": "2024-03-20T10:30:00Z",
    "expires": "2024-05-19T10:30:00Z",
    "auto_renew": true,
    "validity_days": 60,
    "previous_tokens": [
        {
            "token": "550e8400-e29b-41d4-a716-446655440000",
            "created": "2024-02-20T10:30:00Z",
            "expired": "2024-03-20T10:30:00Z"
        }
    ]
}
```

2. View token history:
```bash
# Request
curl -X GET http://localhost:8000/api/token-history/ \
  -H "Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."

# Response
{
  "tokens": [
    {
      "token": "tk_123abc...",
      "created_at": "2024-03-15T10:00:00Z",
      "expires_at": "2024-04-14T10:00:00Z",
      "is_active": true,
      "daily_requests_remaining": 85
    },
    {
      "token": "tk_456def...",
      "created_at": "2024-02-15T10:00:00Z",
      "expires_at": "2024-03-14T10:00:00Z",
      "is_active": false,
      "daily_requests_remaining": 0
    }
  ]
}
```

3. Update token settings:
```bash
# Request
curl -X PATCH http://localhost:8000/api/profile/ \
  -H "Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..." \
  -H "Content-Type: application/json" \
  -d '{
    "auto_renew_token": true,
    "token_validity_days": 60,
    "keep_token_history": true
  }'

# Response
{
  "message": "Profile settings updated successfully",
  "settings": {
    "auto_renew_token": true,
    "token_validity_days": 60,
    "keep_token_history": true
  }
}
```

### Advanced Error Handling

The system provides clear error messages for various scenarios:

1. Token Expiration:
```json
{
  "error": "Token expired",
  "message": "Your token has expired. Please regenerate or enable auto-renewal.",
  "code": "token_expired"
}
```

2. Daily Limit Exceeded:
```json
{
  "error": "Daily limit exceeded",
  "message": "You have reached your daily request limit. Limit will reset at 2024-03-16T00:00:00Z",
  "code": "daily_limit_exceeded"
}
```

3. Invalid Token:
```json
{
  "error": "Invalid token",
  "message": "The provided token is invalid or has been revoked",
  "code": "invalid_token"
}
```

4. Invalid Token Settings:
```json
{
  "error": "Invalid token settings",
  "details": {
    "validity_days": ["Ensure this value is less than or equal to 365."]
  },
  "status": 400
}
```

5. Token History Not Found:
```json
{
  "error": "Token history not available",
  "message": "No token history found for this user",
  "code": "history_not_found"
}
```

### Best Practices

1. Token Management:
   - Enable auto-renewal for uninterrupted service
   - Keep token history for audit purposes
   - Monitor daily usage patterns
   - Set appropriate validity periods

2. Security:
   - Store tokens securely
   - Never share tokens
   - Rotate tokens periodically
   - Monitor for unusual activity

3. Rate Limiting:
   - Track daily usage
   - Plan for limit increases
   - Handle rate limit errors gracefully
   - Implement request queuing if needed

## Available Endpoints

All endpoints use the `/v1/` prefix and are automatically mapped to the appropriate Polygon.io API version internally.

### Authentication Endpoints

```bash
POST /api/register/            # Register new user
POST /api/token/              # Get JWT token
POST /api/token/refresh/      # Refresh JWT token
GET  /api/profile/            # Get user profile and request token
POST /api/regenerate-token/   # Generate new request token
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
   - JWT token required for `/api/` endpoints
   - Request token required for `/v1/` endpoints
   - Each user has a daily request limit
   - Request tokens can be regenerated at any time

3. **Response Format**: The proxy service maintains Polygon.io's original response structure.

4. **Version Mapping**: All endpoints use `/v1/` prefix which maps internally to:
   - v3: Most modern endpoints (default)
   - v2: Aggregates, snapshots, and some reference data
   - v1: Legacy endpoints (open-close, meta/symbols, etc.)

5. **Rate Limiting**: 
   - Default 100 requests per day per user
   - Limits reset at midnight UTC
   - Can be modified per user through admin interface

## Error Handling

The proxy service handles various error scenarios:
- 504: Gateway Timeout (when Polygon.io request times out)
- 502: Bad Gateway (when unable to reach Polygon.io)
- 500: Internal Server Error (for unexpected errors)
- 429: Too Many Requests (when daily limit is exceeded)
- 404: Not Found (when endpoint doesn't exist)
- 401: Unauthorized (when token is invalid or missing)

## Security

- JWT Authentication for user management
- Request Token authentication for API access
- Daily request limits per user
- API keys are never exposed to clients
- Secure headers configuration
- Environment-based authentication

## Testing the Authentication System

### Unit Tests

The project includes comprehensive tests for the new DRF authentication system:

```bash
# Run all authentication tests
python manage.py test users.tests

# Run specific test classes
python manage.py test users.tests.RequestTokenAuthenticationTest
python manage.py test users.tests.DailyLimitPermissionTest
python manage.py test users.tests.AuthenticationIntegrationTest
```

### Test Coverage

1. **RequestTokenAuthentication Tests**:
   - Valid token authentication
   - Invalid token handling
   - Token expiration validation
   - Missing token scenarios

2. **DailyLimitPermission Tests**:
   - Daily request counting
   - Limit enforcement
   - Counter reset logic
   - Rate limiting responses

3. **Integration Tests**:
   - End-to-end authentication flow
   - Multiple authentication methods
   - Permission class interaction
   - Frontend/API endpoint separation

### Manual Testing

#### 1. Test Request Token Authentication:
```bash
# Create a user and get request token
curl -X POST http://localhost:8000/api/register/ \
  -H "Content-Type: application/json" \
  -d '{"email": "test@example.com", "password": "testpass123", "password2": "testpass123"}'

# Test API access with request token
curl -X GET http://localhost:8000/v1/stocks/tickers/AAPL/ \
  -H "X-Request-Token: YOUR_REQUEST_TOKEN"
```

#### 2. Test JWT Authentication:
```bash
# Get JWT token
curl -X POST http://localhost:8000/api/token/ \
  -H "Content-Type: application/json" \
  -d '{"email": "test@example.com", "password": "testpass123"}'

# Test user management with JWT
curl -X GET http://localhost:8000/api/profile/ \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

#### 3. Test Daily Limits:
```bash
# Make multiple requests to test daily limits
for i in {1..5}; do
  curl -X GET http://localhost:8000/v1/stocks/tickers/AAPL/ \
    -H "X-Request-Token: YOUR_REQUEST_TOKEN"
done
```

#### 4. Test Authentication Errors:
```bash
# Test invalid request token
curl -X GET http://localhost:8000/v1/stocks/tickers/AAPL/ \
  -H "X-Request-Token: invalid-token"

# Test missing authentication
curl -X GET http://localhost:8000/v1/stocks/tickers/AAPL/

# Test expired JWT
curl -X GET http://localhost:8000/api/profile/ \
  -H "Authorization: Bearer expired_jwt_token"
```

### Authentication Development

#### Adding New Authentication Methods:

1. **Create Authentication Class** (`users/authentication.py`):
```python
from rest_framework import authentication
from rest_framework import exceptions

class CustomAuthentication(authentication.BaseAuthentication):
    def authenticate(self, request):
        # Your authentication logic here
        return (user, token)
```

2. **Add to Settings** (`proxy_project/settings.py`):
```python
REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": (
        "rest_framework_simplejwt.authentication.JWTAuthentication",
        "users.authentication.RequestTokenAuthentication",
        "users.authentication.CustomAuthentication",  # New auth class
    ),
}
```

3. **Update View Configuration** (`proxy_app/views.py`):
```python
def _set_authentication(self):
    if settings.ENV != "local":
        self.authentication_classes = [
            JWTAuthentication, 
            RequestTokenAuthentication,
            CustomAuthentication  # Add new auth class
        ]
```

#### Adding New Permission Classes:

1. **Create Permission Class** (`users/permissions.py`):
```python
from rest_framework import permissions

class CustomPermission(permissions.BasePermission):
    def has_permission(self, request, view):
        # Your permission logic here
        return True
```

2. **Use in Views**:
```python
class PolygonProxyView(APIView):
    permission_classes = [IsAuthenticated, DailyLimitPermission, CustomPermission]
```

## License

This project is licensed under the MIT License - see the LICENSE file for details.

### Additional Examples

#### Stock Market Data

1. Get Daily OHLC Data:
```bash
# Request
curl -X GET "http://localhost:8000/v1/aggs/ticker/AAPL/range/1/day/2024-01-01/2024-03-20" \
  -H "X-Request-Token: 550e8400-e29b-41d4-a716-446655440000"

# Response
{
    "ticker": "AAPL",
    "queryCount": 55,
    "resultsCount": 55,
    "adjusted": true,
    "results": [
        {
            "v": 77922437,
            "vw": 185.8751,
            "o": 184.22,
            "c": 185.92,
            "h": 186.74,
            "l": 184.18,
            "t": 1704067200000,
            "n": 703219
        }
    ],
    "status": "OK",
    "request_id": "6a7e466b6837652eca4def2f7b7adc56"
}
```

2. Get Real-time Quote:
```bash
# Request
curl -X GET "http://localhost:8000/v1/last/trade/AAPL" \
  -H "X-Request-Token: 550e8400-e29b-41d4-a716-446655440000"

# Response
{
    "status": "OK",
    "results": {
        "T": "AAPL",
        "p": 185.92,
        "s": 100,
        "t": 1710979199999,
        "c": ["@", "T"],
        "i": "12345"
    }
}
```

#### Forex Data

1. Currency Conversion:
```bash
# Request
curl -X GET "http://localhost:8000/v1/conversion/EUR/USD?amount=100" \
  -H "X-Request-Token: 550e8400-e29b-41d4-a716-446655440000"

# Response
{
    "status": "OK",
    "results": {
        "from": "EUR",
        "to": "USD",
        "initialAmount": 100,
        "converted": 108.75,
        "rate": 1.0875,
        "lastUpdated": "2024-03-20T15:30:00Z"
    }
}
```

#### Crypto Data

1. Get Crypto OHLC:
```bash
# Request
curl -X GET "http://localhost:8000/v1/aggs/ticker/X:BTCUSD/range/1/day/2024-03-19/2024-03-20" \
  -H "X-Request-Token: 550e8400-e29b-41d4-a716-446655440000"

# Response
{
    "ticker": "X:BTCUSD",
    "queryCount": 2,
    "resultsCount": 2,
    "adjusted": true,
    "results": [
        {
            "v": 25361.42,
            "vw": 63521.8909,
            "o": 62891.23,
            "c": 64234.56,
            "h": 64890.12,
            "l": 62780.34,
            "t": 1710806400000,
            "n": 482910
        }
    ],
    "status": "OK"
}
```

#### Technical Indicators

1. Get RSI for Stock:
```bash
# Request
curl -X GET "http://localhost:8000/v1/indicators/rsi/AAPL?timespan=day&window=14&series_type=close" \
  -H "X-Request-Token: 550e8400-e29b-41d4-a716-446655440000"

# Response
{
    "status": "OK",
    "results": {
        "underlying": {
            "aggregates": [
                {
                    "T": "AAPL",
                    "v": 77922437,
                    "vw": 185.8751,
                    "o": 184.22,
                    "c": 185.92,
                    "h": 186.74,
                    "l": 184.18,
                    "t": 1704067200000
                }
            ]
        },
        "values": [
            {
                "timestamp": 1704067200000,
                "value": 65.42
            }
        ]
    }
}
```

#### Additional Error Scenarios

1. Rate Limit Warning (90% of daily limit):
```json
{
    "status": "OK",
    "results": { ... },
    "warning": {
        "message": "You have used 90% of your daily request limit",
        "requests_remaining": 10
    }
}
```

2. Invalid Endpoint:
```json
{
    "error": "Not Found",
    "message": "The requested endpoint does not exist",
    "status": 404
}
```

3. Invalid Query Parameters:
```json
{
    "error": "Bad Request",
    "message": "Invalid date format. Expected format: YYYY-MM-DD",
    "status": 400
}
```

4. Polygon.io Service Error:
```json
{
    "error": "Bad Gateway",
    "message": "Failed to proxy request to Polygon.io",
    "status": 502
}
```

#### JWT Token Management

1. Refresh JWT Token:
```bash
# Request
curl -X POST http://localhost:8000/api/token/refresh/ \
  -H "Content-Type: application/json" \
  -d '{
    "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
  }'

# Response
{
    "access": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
    "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
}
```

2. Update User Profile:
```bash
# Request
curl -X PATCH http://localhost:8000/api/profile/ \
  -H "Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..." \
  -H "Content-Type: application/json" \
  -d '{
    "first_name": "John Updated",
    "last_name": "Doe Updated"
  }'

# Response
{
    "id": 1,
    "email": "your.email@example.com",
    "first_name": "John Updated",
    "last_name": "Doe Updated",
    "request_token": "550e8400-e29b-41d4-a716-446655440000",
    "daily_request_limit": 100,
    "daily_requests_made": 5,
    "last_request_date": "2024-03-20"
}
```

### Token Management Features

The service includes advanced token management capabilities:

1. **Token Expiration**:
   - Configurable validity period (default 30 days)
   - Automatic expiration checking
   - Optional auto-renewal
   - Graceful expiration handling

2. **Token History**:
   - Tracks previous tokens
   - Stores creation and expiration dates
   - Maintains history of last 5 tokens
   - Audit trail for security

3. **Token Settings**:
   - Auto-renewal configuration
   - Customizable validity period
   - Option to save or discard old tokens
   - Per-user configuration

#### Token Management Examples

1. Generate new token with custom settings:
```bash
# Request
curl -X POST http://localhost:8000/api/regenerate-token/ \
  -H "Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..." \
  -H "Content-Type: application/json" \
  -d '{
    "save_old": true,
    "auto_renew": true,
    "validity_days": 60
  }'

# Response
{
    "request_token": "661f9511-f3ab-52e5-b827-557766551111",
    "created": "2024-03-20T10:30:00Z",
    "expires": "2024-05-19T10:30:00Z",
    "auto_renew": true,
    "validity_days": 60,
    "previous_tokens": [
        {
            "token": "550e8400-e29b-41d4-a716-446655440000",
            "created": "2024-02-20T10:30:00Z",
            "expired": "2024-03-20T10:30:00Z"
        }
    ]
}
```

2. View token history:
```bash
# Request
curl -X GET http://localhost:8000/api/token-history/ \
  -H "Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."

# Response
{
    "tokens": [
        {
            "token": "tk_123abc...",
            "created_at": "2024-03-15T10:00:00Z",
            "expires_at": "2024-04-14T10:00:00Z",
            "is_active": true,
            "daily_requests_remaining": 85
        },
        {
            "token": "tk_456def...",
            "created_at": "2024-02-15T10:00:00Z",
            "expires_at": "2024-03-14T10:00:00Z",
            "is_active": false,
            "daily_requests_remaining": 0
        }
    ]
}
```

3. Update token settings:
```bash
# Request
curl -X PATCH http://localhost:8000/api/profile/ \
  -H "Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..." \
  -H "Content-Type: application/json" \
  -d '{
    "auto_renew_token": true,
    "token_validity_days": 60,
    "keep_token_history": true
  }'

# Response
{
    "message": "Profile settings updated successfully",
    "settings": {
        "auto_renew_token": true,
        "token_validity_days": 60,
        "keep_token_history": true
    }
}
```

### API Endpoints Reference

#### Authentication Endpoints

1. `/api/register/`
   - Method: POST
   - Purpose: Create new user account
   - Returns: User details and initial request token

2. `/api/token/`
   - Method: POST
   - Purpose: Get JWT authentication tokens
   - Returns: Access and refresh tokens

3. `/api/token/refresh/`
   - Method: POST
   - Purpose: Refresh JWT token
   - Returns: New access token

#### Token Management Endpoints

1. `/api/regenerate-token/`
   - Method: POST
   - Purpose: Generate new request token
   - Configurable settings for validity and auto-renewal

2. `/api/token-history/`
   - Method: GET
   - Purpose: View token history
   - Shows last 5 tokens with details

3. `/api/profile/`
   - Method: GET/PATCH
   - Purpose: View/update token settings
   - Manage auto-renewal and validity period

#### Polygon.io Proxy Endpoints

All Polygon.io endpoints are accessible through `/v1/*` with your request token:

1. Stock Data:
   ```bash
   curl -X GET "http://localhost:8000/v1/stocks/AAPL/trades" \
     -H "X-Request-Token: your_request_token"
   ```

2. Crypto Data:
   ```bash
   curl -X GET "http://localhost:8000/v1/crypto/BTC/USD/trades" \
     -H "X-Request-Token: your_request_token"
   ```

3. Forex Data:
   ```bash
   curl -X GET "http://localhost:8000/v1/forex/EUR/USD/trades" \
     -H "X-Request-Token: your_request_token"
   ```

### Best Practices

1. Token Management:
   - Enable auto-renewal for uninterrupted service
   - Keep token history for audit purposes
   - Monitor daily usage patterns
   - Set appropriate validity periods

2. Security:
   - Store tokens securely
   - Never share tokens
   - Rotate tokens periodically
   - Monitor for unusual activity

3. Rate Limiting:
   - Track daily usage
   - Plan for limit increases
   - Handle rate limit errors gracefully
   - Implement request queuing if needed