# Quick Deployment Steps for financialdata.online

## 🚀 Ready-to-Deploy Commands

### 1. Setup Cloudflare (One-time)
```bash
# Navigate to worker directory
cd workers/cache-worker

# Login to Cloudflare
npx wrangler login

# Check authentication
npx wrangler whoami
```

### 2. Get Your IDs from Cloudflare Dashboard
1. Go to [dash.cloudflare.com](https://dash.cloudflare.com)
2. Select `financialdata.online` domain
3. Copy **Zone ID** from the right sidebar
4. Go to "My Profile" → copy **Account ID**

### 3. Update wrangler.jsonc
Edit `workers/cache-worker/wrangler.jsonc` and add:

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
			"zone_id": "YOUR_ZONE_ID_HERE"
		}
	]
}
```

### 4. Deploy Worker
```bash
# Easy deployment
./deploy.sh

# Or manual deployment
npx wrangler deploy
```

### 5. Configure Custom Domain (Cloudflare Dashboard)
1. Go to **Workers & Pages** → **Overview**
2. Click on `financialdata-cache-worker`
3. Go to **Settings** → **Triggers**
4. Click **Add Custom Domain**
5. Enter: `cache.financialdata.online`
6. Click **Add Custom Domain**

### 6. Add DNS Record
In Cloudflare Dashboard → DNS → Records:
- **Type**: A
- **Name**: `cache`
- **IPv4**: `192.0.2.1` (placeholder)
- **Proxy**: ☁️ Enabled (Orange cloud)

### 7. Test Deployment
```bash
# Test worker subdomain
curl https://financialdata-cache-worker.YOUR-SUBDOMAIN.workers.dev/health

# Test custom domain (after DNS setup)
curl https://cache.financialdata.online/health
curl "https://cache.financialdata.online/v1/reference/tickers/types"
```

## 🔧 Configuration Files Updated

✅ **`src/index.js`** - Updated to use production API (`https://api.financialdata.online`)  
✅ **`wrangler.jsonc`** - Configured for `financialdata.online` domain  
✅ **`deploy.sh`** - Automated deployment script  

## 🎯 Expected Results

After deployment, your cache worker will be available at:
- **Worker URL**: `https://financialdata-cache-worker.YOUR-SUBDOMAIN.workers.dev`
- **Custom Domain**: `https://cache.financialdata.online`

The worker will:
- Cache API responses with intelligent TTL
- Proxy requests to `https://api.financialdata.online`
- Handle CORS for web applications
- Provide global edge performance

## 🚨 Important Notes

1. **Domain Setup**: Make sure `financialdata.online` is added to your Cloudflare account
2. **Django Backend**: Ensure your Django app is accessible at `https://api.financialdata.online`
3. **SSL**: All communication will be HTTPS
4. **Cache**: First requests will be slower (cache miss), subsequent requests will be fast (cache hit)

Your financial data API will now have global edge caching! 🌍⚡ 