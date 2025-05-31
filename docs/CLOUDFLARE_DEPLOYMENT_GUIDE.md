# Cloudflare Worker Deployment Guide for financialdata.online

This guide will walk you through deploying your cache worker to Cloudflare and configuring it for the `financialdata.online` domain.

## Prerequisites

1. **Cloudflare Account**: Sign up at [cloudflare.com](https://cloudflare.com)
2. **Domain in Cloudflare**: Add `financialdata.online` to your Cloudflare account
3. **Wrangler CLI**: Should already be installed (comes with the project)
4. **Django Backend**: Ensure your Django app is deployed and accessible at `https://api.financialdata.online`

## Step 1: Cloudflare Setup

### 1.1 Add Domain to Cloudflare
1. Log into [Cloudflare Dashboard](https://dash.cloudflare.com)
2. Click "Add a Site"
3. Enter `financialdata.online`
4. Choose the Free plan (or higher)
5. Update your domain's nameservers to Cloudflare's nameservers

### 1.2 Get Your Account ID and Zone ID
1. In Cloudflare Dashboard, select your domain
2. In the right sidebar, copy your **Zone ID**
3. Go to "My Profile" → "API Tokens" → copy your **Account ID**

## Step 2: Configure Wrangler

### 2.1 Update wrangler.jsonc for Production

```bash
cd workers/cache-worker
```

Edit `wrangler.jsonc`:

```json
{
	"$schema": "node_modules/wrangler/config-schema.json",
	"name": "financialdata-cache-worker",
	"main": "src/index.js",
	"compatibility_date": "2025-05-31",
	"account_id": "YOUR_ACCOUNT_ID_HERE",
	"observability": {
		"enabled": true
	},
	"placement": { 
		"mode": "smart" 
	},
	"routes": [
		{
			"pattern": "cache.financialdata.online/*",
			"custom_domain": true
		}
	]
}
```

### 2.2 Authenticate Wrangler

```bash
# Login to Cloudflare via Wrangler
npx wrangler login

# Verify authentication
npx wrangler whoami
```

## Step 3: Configure Environment Variables

### 3.1 Set Production Environment Variables

Instead of putting sensitive data in `wrangler.jsonc`, use Wrangler secrets:

```bash
# Set your Polygon API key (if needed by worker)
npx wrangler secret put POLYGON_API_KEY
# Enter your actual Polygon API key when prompted

# You can also set other environment variables
npx wrangler secret put BACKEND_URL
# Enter: https://api.financialdata.online
```

### 3.2 Update Worker Code for Environment Variables

Edit `src/index.js` to use environment variables:

```javascript
const BACKEND = env.BACKEND_URL || 'https://api.financialdata.online'

export default {
  async fetch(request, env, ctx) {
    const BACKEND = env.BACKEND_URL || 'https://api.financialdata.online'
    // ... rest of your code
  }
}
```

## Step 4: Deploy the Worker

### 4.1 Deploy to Cloudflare

```bash
# Deploy the worker
npx wrangler deploy

# You should see output like:
# ✨ Success! Deployed financialdata-cache-worker
#   https://financialdata-cache-worker.your-subdomain.workers.dev
```

### 4.2 Test the Deployed Worker

```bash
# Test the health endpoint
curl https://financialdata-cache-worker.your-subdomain.workers.dev/health

# Test an API endpoint
curl "https://financialdata-cache-worker.your-subdomain.workers.dev/v1/reference/tickers/types"
```

## Step 5: Configure Custom Domain

### 5.1 Set Up Custom Domain in Cloudflare Dashboard

1. Go to [Cloudflare Dashboard](https://dash.cloudflare.com)
2. Select your `financialdata.online` domain
3. Go to **Workers & Pages** → **Overview**
4. Click on your worker (`financialdata-cache-worker`)
5. Go to **Settings** → **Triggers**
6. Click **Add Custom Domain**
7. Enter: `cache.financialdata.online`
8. Click **Add Custom Domain**

### 5.2 Alternative: Use Routes

Or configure routes in `wrangler.jsonc`:

```json
{
	"routes": [
		{
			"pattern": "cache.financialdata.online/*",
			"zone_id": "YOUR_ZONE_ID_HERE"
		}
	]
}
```

Then redeploy:

```bash
npx wrangler deploy
```

## Step 6: DNS Configuration

### 6.1 Add DNS Records

In Cloudflare Dashboard → DNS → Records:

1. **A Record for cache subdomain**:
   - **Type**: A
   - **Name**: `cache`
   - **IPv4 address**: `192.0.2.1` (placeholder - Cloudflare will handle routing)
   - **Proxy status**: ☁️ Proxied (Orange cloud)

2. **CNAME for API** (if not already configured):
   - **Type**: CNAME
   - **Name**: `api`
   - **Target**: Your Django hosting provider (e.g., `your-app.herokuapp.com`)
   - **Proxy status**: ☁️ Proxied

## Step 7: Update Django Backend

### 7.1 Update ALLOWED_HOSTS

In your Django `settings.py`:

```python
ALLOWED_HOSTS = [
    "financialdata.online",
    "api.financialdata.online",
    "cache.financialdata.online",
    # ... other domains
]

CSRF_TRUSTED_ORIGINS = [
    "https://financialdata.online",
    "https://api.financialdata.online", 
    "https://cache.financialdata.online",
]
```

### 7.2 Update CORS Settings

```python
CORS_ALLOWED_ORIGINS = [
    "https://financialdata.online",
    "https://cache.financialdata.online",
]

# Or for development
CORS_ALLOW_ALL_ORIGINS = True  # Only for development
```

## Step 8: Production Configuration

### 8.1 Update Worker for Production

Edit `src/index.js` to use the production backend:

```javascript
const BACKEND = 'https://api.financialdata.online'

// Ensure proper error handling for production
async function proxy(request, env) {
  const url = new URL(request.url)
  const BACKEND = env.BACKEND_URL || 'https://api.financialdata.online'

  try {
    const response = await fetch(BACKEND + url.pathname + url.search, {
      method: request.method,
      headers: {
        ...request.headers,
        // Remove any localhost headers
        'host': 'api.financialdata.online'
      },
      body: request.body
    })

    return new Response(response.body, {
      status: response.status,
      headers: {
        ...Object.fromEntries(response.headers),
        'access-control-allow-origin': '*',
        'cache-control': response.headers.get('cache-control') || 'no-cache'
      }
    })
  } catch (error) {
    console.error('Proxy error:', error)
    return Response.json({error: 'Service temporarily unavailable'}, {
      status: 502,
      headers: {'access-control-allow-origin': '*'}
    })
  }
}
```

### 8.2 Deploy Final Version

```bash
npx wrangler deploy
```

## Step 9: Testing & Verification

### 9.1 Test All Endpoints

```bash
# Test health endpoint
curl https://cache.financialdata.online/health

# Test API proxy
curl "https://cache.financialdata.online/v1/reference/tickers/types"

# Test caching (run twice, second should be faster)
curl -w "Time: %{time_total}s\n" "https://cache.financialdata.online/v1/reference/tickers/types"
curl -w "Time: %{time_total}s\n" "https://cache.financialdata.online/v1/reference/tickers/types"

# Test cache headers
curl -I "https://cache.financialdata.online/v1/reference/tickers/types"
```

### 9.2 Monitor Performance

In Cloudflare Dashboard:
1. Go to **Analytics & Logs** → **Workers Analytics**
2. Monitor request volume, response times, and error rates
3. Check **Real User Monitoring** for performance insights

## Step 10: Environment-Specific Configuration

### 10.1 Multiple Environments

You can configure different environments:

```bash
# Deploy to staging
npx wrangler deploy --name financialdata-cache-staging

# Deploy to production  
npx wrangler deploy --name financialdata-cache-production
```

### 10.2 Environment-Specific Wrangler Config

Create `wrangler.production.jsonc`:

```json
{
	"name": "financialdata-cache-production",
	"main": "src/index.js",
	"compatibility_date": "2025-05-31",
	"account_id": "YOUR_ACCOUNT_ID",
	"routes": [
		{
			"pattern": "cache.financialdata.online/*",
			"zone_id": "YOUR_ZONE_ID"
		}
	],
	"placement": { "mode": "smart" },
	"observability": { "enabled": true }
}
```

Deploy with specific config:

```bash
npx wrangler deploy --config wrangler.production.jsonc
```

## Step 11: Monitoring & Maintenance

### 11.1 Set Up Alerts

1. Go to **Notifications** in Cloudflare Dashboard
2. Create alerts for:
   - Worker errors exceed threshold
   - High response times
   - Unusual traffic patterns

### 11.2 Review Analytics

Regularly check:
- Cache hit rates
- Response times
- Error rates
- Traffic patterns

## Troubleshooting

### Common Issues

1. **504 Gateway Timeout**: Check if Django backend is accessible
2. **CORS Errors**: Verify CORS settings in Django
3. **SSL Issues**: Ensure all URLs use HTTPS
4. **DNS Issues**: Verify DNS records are properly configured

### Debug Commands

```bash
# View worker logs
npx wrangler tail

# Test specific routes
npx wrangler dev --remote

# Check worker configuration
npx wrangler status
```

## Security Considerations

1. **Use Secrets**: Never put API keys in code or config files
2. **Rate Limiting**: Consider implementing rate limiting in the worker
3. **HTTPS Only**: Ensure all traffic uses HTTPS
4. **Monitor Access**: Set up monitoring for unusual access patterns

## Performance Optimization

1. **Cache Headers**: Fine-tune cache TTL based on data freshness requirements
2. **Smart Placement**: Use smart placement for optimal routing
3. **Compression**: Enable compression for large responses
4. **Monitoring**: Use Cloudflare Analytics to identify optimization opportunities

Your cache worker will now be accessible at `https://cache.financialdata.online` and will intelligently cache responses from your Django API while providing global edge performance! 