# Django Polygon.io Proxy Service

A simple and efficient Django REST API proxy service that forwards all HTTP requests to Polygon.io API with JWT authentication and request token validation.

## 🚀 NEW: Automated DNS Management with Terraform

This repository now includes **automated DNS management** for DigitalOcean App Platform deployments using Terraform and GitHub Actions. This system automatically manages DNS records for multiple domains with high availability and load balancing.

### 🎯 What the DNS Automation Does

- **Manages 4 domains**: `financialdata.online`, `financialdata.digital`, `dadosfinanceiros.com`, `dadosfinanceiros.com.br`
- **High Availability**: Uses DigitalOcean's static ingress IPs with redundancy
- **IPv6 Support**: Full IPv4 and IPv6 DNS records for modern browsers
- **Auto-deployment**: Changes deploy automatically when you push code
- **Production Ready**: Based on DigitalOcean's official App Platform documentation

### 📋 Quick Implementation Guide

#### Step 1: Set Up GitHub Secrets

1. Go to your repository: [Settings → Secrets](https://github.com/saas2guys/dadosfinanceiros.com.br/settings/secrets/actions)
2. Add these repository secrets:

```
DO_TOKEN = dop_v1_YOUR_DIGITALOCEAN_TOKEN_HERE
APP_DOMAIN = dadosfinanceiros-com-br-vsxtw.ondigitalocean.app
```

#### Step 2: Commit and Push the Terraform Files

The Terraform files are already created in your repository:

```bash
# All files are ready - just commit and push
git add .
git commit -m "Add Terraform DNS automation"
git push origin main
```

#### Step 3: Monitor the Automation

1. **GitHub Actions**: Check the [Actions tab](https://github.com/saas2guys/dadosfinanceiros.com.br/actions) for deployment status
2. **DigitalOcean DNS**: Check [Networking → Domains](https://cloud.digitalocean.com/networking/domains) for created records

#### Step 4: Add Domains to App Platform

After DNS records are created, add domains to your [App Platform app](https://cloud.digitalocean.com/apps/bbce29b0-3bff-4306-a11b-e6a539beef04):

1. **Settings** → **Domains** → **Edit**
2. Add each domain:
   - `financialdata.online`
   - `www.financialdata.online`
   - `financialdata.digital`
   - `www.financialdata.digital`
   - `dadosfinanceiros.com`
   - `www.dadosfinanceiros.com`
   - `dadosfinanceiros.com.br`
   - `www.dadosfinanceiros.com.br`

### 🔄 How the Automation Works

```mermaid
sequenceDiagram
    participant Dev as Developer
    participant Git as GitHub Repo
    participant GHA as GitHub Actions
    participant TF as Terraform
    participant DO as DigitalOcean API
    participant DNS as DO DNS Servers
    participant User as End User
    participant App as DO App Platform

    Note over Dev, App: Development & DNS Configuration Flow

    %% Development Phase
    Dev->>Git: 1. Push DNS changes to main.tf
    Note over Dev, Git: Changes to domains/records configuration

    %% CI/CD Pipeline Trigger
    Git->>GHA: 2. Webhook trigger on push to main
    Note over GHA: Workflow: terraform.yml starts

    %% GitHub Actions Workflow
    GHA->>GHA: 3. Setup Terraform environment
    GHA->>TF: 4. terraform init
    TF-->>GHA: Initialize working directory

    GHA->>TF: 5. terraform validate
    TF-->>GHA: Configuration valid

    GHA->>TF: 6. terraform plan
    Note over TF: Compare current state vs desired state
    TF->>DO: 7. Query current DNS records
    DO-->>TF: Current DNS configuration
    TF-->>GHA: Show planned changes

    GHA->>TF: 8. terraform apply (if main branch)
    Note over TF: Apply DNS changes

    %% Terraform applies changes to DigitalOcean
    TF->>DO: 9. Create/Update DNS records
    Note over DO: API calls for each domain/record
    
    loop For each domain
        TF->>DO: Create domain (if not exists)
        TF->>DO: Create/Update A records (@, www)
        TF->>DO: Create/Update API subdomain
        TF->>DO: Create/Update MX records
        TF->>DO: Create/Update TXT records (SPF, DMARC)
        TF->>DO: Create/Update AAAA records (IPv6)
    end

    DO-->>TF: Confirm DNS changes applied
    TF-->>GHA: Apply complete, output domain info
    
    %% DNS Propagation
    DO->>DNS: 10. Update authoritative DNS servers
    Note over DNS: DNS records propagated globally

    GHA-->>Dev: 11. Workflow completion notification
    Note over Dev: Email/Slack notification of success/failure

    Note over Dev, App: User Access Flow

    %% User tries to access the application
    User->>DNS: 12. DNS query for financialdata.online
    DNS-->>User: Return IP address from A record

    User->>App: 13. HTTP request to resolved IP
    Note over App: DigitalOcean App Platform serves application
    App-->>User: Application response

    %% API Access Flow
    User->>DNS: 14. DNS query for api.dadosfinanceiros.com
    DNS-->>User: Return same IP address
    User->>App: 15. API request to resolved IP
    App-->>User: API response

    Note over Dev, App: Multiple Domain Access

    %% Other domains follow same pattern
    par All domains resolve to same server
        User->>DNS: Query financialdata.digital
        DNS-->>User: Same IP address
    and
        User->>DNS: Query dadosfinanceiros.com
        DNS-->>User: Same IP address  
    and
        User->>DNS: Query dadosfinanceiros.com.br
        DNS-->>User: Same IP address
    end

    %% Email flow (using MX records)
    Note over User, App: Email Flow
    User->>DNS: 16. MX query for dadosfinanceiros.com
    DNS-->>User: Return mail.dadosfinanceiros.com
    User->>App: 17. Connect to mail server
    App-->>User: Email service response

    %% Monitoring and Updates
    Note over Dev, App: Ongoing Maintenance
    
    rect rgb(240, 248, 255)
        Note over Dev: Developer makes DNS changes
        Dev->>Git: Update TTL, add new subdomain, etc.
        Git->>GHA: Trigger automation
        GHA->>TF: Apply changes
        TF->>DO: Update DNS records
        DO->>DNS: Propagate changes
    end

    %% Error Handling Flow
    rect rgb(255, 240, 240)
        Note over GHA, DO: Error Scenario
        alt Terraform Apply Fails
            TF->>DO: Invalid API call
            DO-->>TF: Error response
            TF-->>GHA: Apply failed
            GHA-->>Dev: Failure notification
            Note over Dev: Fix configuration and retry
        end
    end
```

### 📋 Detailed Step-by-Step Explanation

#### 🚀 **Development & Configuration Phase**

**Step 1: Developer Push**
```bash
# Developer modifies DNS configuration
vim terraform/main.tf  # Add new domain or modify records
git add terraform/
git commit -m "Add new subdomain for API v2"
git push origin main   # This triggers the automation
```
- **What happens**: Developer edits Terraform configuration files
- **Triggers**: Any change to files in `terraform/` directory
- **Files involved**: `main.tf`, `variables.tf`, or new `.tf` files
- **Best practices**: Use descriptive commit messages for DNS changes

**Step 2: GitHub Webhook Trigger**
```yaml
# .github/workflows/terraform.yml
on:
  push:
    branches: [ main ]
    paths: [ 'terraform/**' ]  # Only triggers on terraform changes
```
- **What happens**: GitHub detects push to main branch affecting terraform files
- **Trigger condition**: Changes in `terraform/` directory only
- **Performance**: Avoids unnecessary runs when only app code changes
- **Security**: Only runs on main branch for production safety

#### ⚙️ **GitHub Actions Workflow Execution**

**Step 3: Environment Setup**
```bash
# GitHub Actions runner executes:
- uses: actions/checkout@v4           # Download repository code
- uses: hashicorp/setup-terraform@v3  # Install Terraform CLI
  with:
    terraform_version: "1.5.7"       # Specific version for consistency
```
- **What happens**: Clean Ubuntu environment prepared with tools
- **Security**: Secrets loaded from GitHub repository settings
- **Consistency**: Same Terraform version used every time

**Step 4: Terraform Initialization**
```bash
terraform init
```
- **What happens**: Downloads DigitalOcean provider plugins
- **State management**: Configures remote state storage (if configured)
- **Provider verification**: Validates provider signature and version
- **Dependencies**: Downloads required modules and providers

**Step 5: Configuration Validation**
```bash
terraform validate
```
- **What happens**: Syntax and logic validation of `.tf` files
- **Checks performed**:
  - Valid HCL syntax
  - Required variables defined
  - Resource dependencies correct
  - Provider configuration valid
- **Benefits**: Catches errors before expensive API calls

**Step 6-7: Planning Phase**
```bash
terraform plan -input=false
```
- **What happens**: Terraform queries current state vs desired state
- **API calls made**:
  - `GET /v2/domains` - List existing domains
  - `GET /v2/domains/{domain}/records` - Current DNS records
- **Output**: Detailed plan showing additions, changes, deletions
- **Safety**: No changes made yet, only planning

**Step 8: Apply Changes (Production Only)**
```bash
terraform apply -auto-approve -input=false
```
- **Conditions**: Only runs on main branch pushes (not PRs)
- **What happens**: Executes the planned changes
- **Safety features**:
  - Automatic approval for main branch
  - Manual approval required for PRs
  - Rollback possible via Git revert

#### 🌐 **DNS Infrastructure Changes**

**Step 9: Domain and Record Creation**
For each of the 4 domains, Terraform makes these API calls:

```bash
# Domain Creation (if new)
POST /v2/domains
{
  "name": "financialdata.online",
  "ip_address": "162.159.140.98"
}

# A Records (IPv4)
POST /v2/domains/financialdata.online/records
{
  "type": "A",
  "name": "@",      # Root domain
  "data": "162.159.140.98",
  "ttl": 300
}

POST /v2/domains/financialdata.online/records
{
  "type": "A",
  "name": "www",    # www subdomain
  "data": "162.159.140.98",
  "ttl": 300
}

# AAAA Records (IPv6)
POST /v2/domains/financialdata.online/records
{
  "type": "AAAA",
  "name": "@",
  "data": "2606:4700:7::60",
  "ttl": 300
}

# API Subdomain (for API access)
POST /v2/domains/financialdata.online/records
{
  "type": "A",
  "name": "api",
  "data": "162.159.140.98",
  "ttl": 300
}
```

**Records Created for Each Domain**:
- **Root domain** (`@`): A and AAAA records
- **www subdomain**: A and AAAA records  
- **API subdomain**: A record for API access
- **Redundancy**: Multiple IP addresses for high availability

**Step 10: DNS Propagation**
```bash
# DigitalOcean authoritative servers update
ns1.digitalocean.com  # Primary nameserver
ns2.digitalocean.com  # Secondary nameserver  
ns3.digitalocean.com  # Tertiary nameserver
```
- **Timeline**: Immediate on DigitalOcean servers
- **Global propagation**: 5 minutes to 48 hours depending on TTL
- **TTL impact**: 300-second TTL means faster updates
- **Verification**: Can check with `dig @ns1.digitalocean.com domain.com`

#### 👥 **End User Experience**

**Step 12-13: Website Access**
```bash
# User types: https://financialdata.online
1. Browser DNS query → 162.159.140.98
2. Browser HTTPS request → App Platform
3. App Platform routes → Django application
4. Django responds → User sees website
```

**Step 14-15: API Access**
```bash
# API client makes request
curl -X GET https://api.dadosfinanceiros.com/v1/stocks/AAPL \
  -H "X-Request-Token: your_token"

# Flow:
1. DNS resolves api.dadosfinanceiros.com → 162.159.140.98
2. HTTPS request to App Platform
3. App Platform SSL termination
4. Route to Django API endpoint
5. JWT/Token authentication
6. Proxy request to Polygon.io
7. Return financial data
```

**Step 16: Multiple Domain Support**
All domains resolve to the same IP addresses:
- **financialdata.online** → 162.159.140.98, 172.66.0.96
- **financialdata.digital** → Same IPs
- **dadosfinanceiros.com** → Same IPs
- **dadosfinanceiros.com.br** → Same IPs

**Benefits**:
- **Brand flexibility**: Multiple branded access points
- **Geographic preferences**: Local domain extensions
- **Redundancy**: If one domain has issues, others work
- **SEO**: Different domains for different markets

#### 📧 **Email Integration (Optional)**

**Step 17: MX Records for Email**
```bash
# MX record creation (if configured)
POST /v2/domains/dadosfinanceiros.com/records
{
  "type": "MX",
  "name": "@",
  "data": "mail.dadosfinanceiros.com.",
  "priority": 10,
  "ttl": 300
}
```
- **Purpose**: Enable email for your domains
- **Configuration**: Can point to Google Workspace, Office 365, or custom mail server
- **Security**: SPF, DKIM, and DMARC records for email authentication

#### 🔄 **Ongoing Maintenance**

**Continuous Updates**:
```bash
# Developer workflow for updates
1. Edit terraform/main.tf           # Add new subdomain
2. git commit -m "Add blog subdomain"
3. git push origin main             # Triggers automation
4. Monitor GitHub Actions           # Watch deployment
5. Verify DNS changes              # Test new subdomain
```

**Common Changes**:
- **New subdomains**: api.domain.com, blog.domain.com
- **TTL adjustments**: Faster or slower DNS updates
- **IP address changes**: Point to different servers
- **Record modifications**: Update existing DNS records

#### ❌ **Error Handling & Recovery**

**Common Error Scenarios**:

1. **API Token Issues**:
```bash
Error: DigitalOcean API Error: 401 Unauthorized
Solution: Check DO_TOKEN secret in GitHub
```

2. **Domain Already Exists**:
```bash
Error: Domain already exists in DigitalOcean
Solution: Import existing domain or use different name
```

3. **Invalid Configuration**:
```bash
Error: Invalid IP address format
Solution: Fix IP format in main.tf and push again
```

**Recovery Process**:
1. **GitHub Actions fails** → Developer gets notification
2. **Review error logs** → Identify root cause
3. **Fix configuration** → Edit Terraform files
4. **Push fix** → Automation retries automatically
5. **Verify success** → Check DNS resolution

#### 🔧 **Monitoring & Verification**

**Automated Verification**:
```bash
# DNS resolution check
dig financialdata.online A +short
# Expected: 162.159.140.98

# IPv6 check  
dig financialdata.online AAAA +short
# Expected: 2606:4700:7::60

# Multiple domain check
for domain in financialdata.online financialdata.digital dadosfinanceiros.com dadosfinanceiros.com.br; do
  echo "Testing $domain:"
  dig $domain A +short
done
```

**Application Health Check**:
```bash
# Verify application responds on all domains
curl -I https://financialdata.online/api/health/
curl -I https://www.dadosfinanceiros.com.br/v1/stocks/AAPL
```

**Performance Monitoring**:
- **DNS resolution time**: Monitor with tools like dig
- **HTTPS response time**: Monitor application performance
- **Global accessibility**: Check from different geographic locations
- **Certificate validity**: Monitor SSL certificate expiration
```

# Django REST Framework Authentication System
# Custom Authentication and Permission Classes
# Clean Separation of Concerns

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

### 🤖 **NEW: Automated IP Detection**

Instead of hardcoding DigitalOcean App Platform IPs, the system now **automatically detects** them using multiple methods:

#### **🔄 How IP Automation Works**

```mermaid
graph TD
    A[Terraform Starts] --> B{DNS Method Enabled?}
    B -->|Yes| C[Resolve app domain via DNS]
    B -->|No| D[Use Static IPs]
    C --> E{IPs Found?}
    E -->|Yes| F[Use Detected IPs]
    E -->|No| G[Try External Script]
    G --> H{Script Success?}
    H -->|Yes| F
    H -->|No| I[Try API Method]
    I --> J{API Success?}
    J -->|Yes| F
    J -->|No| K[Fallback to Static IPs]
    F --> L[Create DNS Records]
    D --> L
    K --> L
    L --> M[Output Detection Results]
```

#### **✅ Automatic Detection Results**

Your current app domain **automatically resolves** to:
```bash
# IPv4 Addresses (detected live)
dadosfinanceiros-com-br-vsxtw.ondigitalocean.app → 162.159.140.98, 172.66.0.96

# IPv6 Addresses (detected live)  
dadosfinanceiros-com-br-vsxtw.ondigitalocean.app → 2606:4700:7::60, 2a06:98c1:58::60
```

#### **🎯 IP Automation Benefits**

- **🔄 Always Current**: IPs detected in real-time on every deployment
- **🛡️ Zero Maintenance**: No manual updates when DigitalOcean changes IPs  
- **🔗 Multiple Methods**: DNS → Script → API → Static fallbacks
- **📊 Transparent**: See which detection method was used
- **⚡ Performance**: Cached during Terraform execution

#### **📋 Configuration Options**

```hcl
# terraform.tfvars
app_domain = "dadosfinanceiros-com-br-vsxtw.ondigitalocean.app"  # ✅ Already set
enable_ip_automation = true   # ✅ Enabled by default

# Optional: For API-based detection
app_id = "bbce29b0-3bff-4306-a11b-e6a539beef04"  # Your app ID
```

#### **🧪 Test IP Detection**

```bash
# Test DNS resolution manually
dig dadosfinanceiros-com-br-vsxtw.ondigitalocean.app A +short
# Returns: 162.159.140.98, 172.66.0.96

# Test the automation script
echo '{"app_domain":"dadosfinanceiros-com-br-vsxtw.ondigitalocean.app","do_token":""}' | \
  ./terraform/scripts/get-app-ips.sh

# View detection results after terraform apply
terraform output detected_ips
```

**📚 [Complete IP Automation Guide](docs/ip-automation.md)** - Detailed documentation with all methods and troubleshooting.