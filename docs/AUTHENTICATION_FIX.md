# Authentication Fix for Registration Endpoint

## Issue
The registration endpoint `https://financialdata.online/register/` was requiring authentication, preventing new users from registering.

## Root Cause
In production (`ENV != "local"`), the default DRF permission class was set to `IsAuthenticated`:

```python
# proxy_project/settings.py
REST_FRAMEWORK = {
    "DEFAULT_PERMISSION_CLASSES": [
        (
            "rest_framework.permissions.AllowAny"
            if ENV == "local"
            else "rest_framework.permissions.IsAuthenticated"  # This caused the issue
        ),
    ],
}
```

The `register_user` function-based view used the `@api_view` decorator but didn't have explicit permission settings, so it inherited the default `IsAuthenticated` permission.

## Solution
Added explicit `AllowAny` permission to the registration endpoint:

```python
# users/views.py
@api_view(["GET", "POST"])
@permission_classes([permissions.AllowAny])  # Added this line
def register_user(request):
    # ... registration logic
```

## Verification
- ✅ Web registration: `GET /register/` returns 200 (accessible)
- ✅ API registration: `POST /api/register/` returns 400 for incomplete data (accessible, not 401/403)

## Other Public Endpoints
The following endpoints are correctly configured to allow anonymous access:

### Authentication Endpoints
- `POST /api/token/` - JWT token obtain (login)
- `POST /api/token/refresh/` - JWT token refresh
- `POST /api/token/verify/` - JWT token verification

### Registration Endpoints
- `GET|POST /register/` - Web registration form
- `POST /api/register/` - API registration

### Public Information
- `GET /api/plans/` - List available subscription plans
- `GET /static/...` - Static files (handled by WhiteNoise)

## Protected Endpoints
All other endpoints correctly require authentication:

### User Management
- `GET|PATCH /api/profile/` - User profile
- `POST /api/regenerate-token/` - Token regeneration
- `GET /api/token-history/` - Token history

### Subscription Management
- `GET /api/subscription/` - User subscription info
- `POST /api/create-checkout-session/` - Create payment session
- All subscription management endpoints

### API Proxy
- `GET /v1/*` - All Polygon.io API proxy endpoints

## Best Practices Applied

1. **Explicit Permissions**: All function-based views now have explicit `@permission_classes` decorators
2. **Secure by Default**: Default permission is `IsAuthenticated` in production
3. **Minimal Public Access**: Only essential endpoints allow anonymous access
4. **Consistent Pattern**: Class-based views use `permission_classes` attribute, function-based views use decorator

## Testing
```bash
# Test registration accessibility (should return 200)
curl -I http://localhost:8000/register/

# Test API registration accessibility (should return 400 for incomplete data, not 401)
curl -X POST http://localhost:8000/api/register/ \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com"}'

# Test protected endpoint (should return 401 without auth)
curl -I http://localhost:8000/api/profile/
``` 