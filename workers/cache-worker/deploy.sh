#!/bin/bash

# Cloudflare Worker Deployment Script for financialdata.online
# This script automates the deployment process

set -e

echo "🚀 Deploying Cloudflare Cache Worker for financialdata.online"
echo "============================================================"

# Check if wrangler is authenticated
echo "🔐 Checking Wrangler authentication..."
if ! npx wrangler whoami > /dev/null 2>&1; then
    echo "❌ Wrangler not authenticated. Running login..."
    npx wrangler login
else
    echo "✅ Wrangler already authenticated"
fi

# Check if required environment variables are set
echo "🔍 Checking environment setup..."

# Deploy the worker
echo "📦 Deploying worker to Cloudflare..."
npx wrangler deploy

echo ""
echo "✅ Deployment complete!"
echo ""
echo "📋 Next steps:"
echo "1. Go to Cloudflare Dashboard: https://dash.cloudflare.com"
echo "2. Select your financialdata.online domain"
echo "3. Go to Workers & Pages → Overview"
echo "4. Click on 'financialdata-cache-worker'"
echo "5. Go to Settings → Triggers → Add Custom Domain"
echo "6. Add: cache.financialdata.online"
echo ""
echo "🧪 Test your deployment:"
echo "curl https://financialdata-cache-worker.YOUR-SUBDOMAIN.workers.dev/health"
echo ""
echo "Once custom domain is configured:"
echo "curl https://cache.financialdata.online/health"
echo "curl https://cache.financialdata.online/v1/reference/tickers/types" 