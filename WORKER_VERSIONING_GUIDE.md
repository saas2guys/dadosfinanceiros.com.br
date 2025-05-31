# Cloudflare Worker Versioning Guide

This guide explains how to implement versioned deployments for your Cloudflare Worker, supporting multiple environments and easy rollbacks.

## 🏗️ Architecture Overview

### **Environment Structure**
```
Development → Staging → Production
     ↓           ↓          ↓
   dev-*    staging-*    v1.x.x
```

### **Domain Configuration**
- **Development**: `cache-dev.financialdata.online`
- **Staging**: `cache-staging.financialdata.online`  
- **Production**: `cache.financialdata.online`

### **Version Naming Convention**
- **Production**: `v1.0.0`, `v1.1.0`, `v2.0.0` (Semantic Versioning)
- **Staging**: `staging-20241201-abc123` (Date + Git commit)
- **Development**: `dev-main-abc123` (Branch + Git commit)

## 📁 Configuration Files

### **Environment-Specific Configs**

1. **`wrangler.dev.jsonc`** - Development environment
2. **`wrangler.staging.jsonc`** - Staging environment  
3. **`wrangler.production.jsonc`** - Production environment
4. **`wrangler.jsonc`** - Default/local development

Each config includes:
- Environment-specific worker name
- Version variables
- Custom domain routing
- Environment-specific settings

## 🚀 Deployment Commands

### **Quick Commands**
```bash
# Development deployment
npm run deploy:dev

# Staging deployment  
npm run deploy:staging

# Production deployment
npm run deploy:production

# Auto-versioned production deployment
npm run deploy:version
```

### **Advanced Deployment**
```bash
# Deploy specific version to staging
./deploy-versioned.sh -e staging -v v1.2.3

# Deploy to production with auto-versioning and message
./deploy-versioned.sh -e production -a -m "New feature release"

# Deploy development with custom version
./deploy-versioned.sh -e dev -v dev-feature-xyz
```

## 🔄 Version Management

### **Semantic Versioning (Production)**
- **MAJOR** (v2.0.0): Breaking changes
- **MINOR** (v1.1.0): New features, backward compatible
- **PATCH** (v1.0.1): Bug fixes, backward compatible

### **Auto-Versioning**
The deployment script can automatically generate versions:

**Production**: Uses latest git tag or creates new one
```bash
./deploy-versioned.sh -e production -a
```

**Staging**: Uses timestamp + git commit
```bash
# Generates: staging-20241201-1430-abc123
./deploy-versioned.sh -e staging -a
```

**Development**: Uses branch + git commit
```bash
# Generates: dev-main-abc123
./deploy-versioned.sh -e dev -a
```

## 🔙 Rollback Process

### **Quick Rollback**
```bash
# List available versions
./rollback.sh -l

# Rollback production to specific version
./rollback.sh -e production -v v1.0.0

# Rollback staging
./rollback.sh -e staging -v staging-20241130-1200-xyz789
```

### **Rollback Process**
1. **Confirmation**: Production rollbacks require confirmation
2. **Git Checkout**: Automatically checks out target version (if git tag exists)
3. **Config Update**: Updates version in configuration file
4. **Deploy**: Deploys the rollback version
5. **Test**: Runs health check
6. **Tag**: Creates rollback tracking tag

## 🏷️ Git Tagging Strategy

### **Production Tags**
```bash
# Create release tag
git tag -a v1.0.0 -m "Production release v1.0.0"
git push origin v1.0.0

# Deploy tagged version
./deploy-versioned.sh -e production -v v1.0.0
```

### **Automatic Tagging**
Production deployments with auto-versioning create git tags:
```bash
# This creates and pushes a git tag
./deploy-versioned.sh -e production -a -m "Feature release"
```

## 🔍 Version Tracking

### **Health Endpoint**
Each worker exposes version information:
```bash
curl https://cache.financialdata.online/health
```

Response:
```json
{
  "status": "ok",
  "version": "v1.0.0",
  "environment": "production",
  "timestamp": "2024-12-01T15:30:00.000Z",
  "backend": "https://api.financialdata.online"
}
```

### **Response Headers**
Every API response includes version headers:
```
x-worker-version: v1.0.0
x-worker-environment: production
```

## 🔧 Configuration Management

### **Environment Variables**
Each environment supports specific variables:

**Development**:
```json
{
  "vars": {
    "ENVIRONMENT": "development",
    "VERSION": "dev-latest",
    "BACKEND_URL": "http://localhost:8000"
  }
}
```

**Production**:
```json
{
  "vars": {
    "ENVIRONMENT": "production", 
    "VERSION": "v1.0.0",
    "BACKEND_URL": "https://api.financialdata.online"
  }
}
```

### **Secrets Management**
Use Wrangler secrets for sensitive data:
```bash
# Set secrets per environment
npx wrangler secret put POLYGON_API_KEY --config wrangler.production.jsonc
npx wrangler secret put POLYGON_API_KEY --config wrangler.staging.jsonc
```

## 🚦 Deployment Pipeline

### **Recommended Workflow**

1. **Development**
   ```bash
   # Feature development
   npm run deploy:dev
   # Test at cache-dev.financialdata.online
   ```

2. **Staging**
   ```bash
   # Deploy to staging for QA
   ./deploy-versioned.sh -e staging -a
   # Test at cache-staging.financialdata.online
   ```

3. **Production**
   ```bash
   # Deploy to production
   ./deploy-versioned.sh -e production -v v1.1.0 -m "New feature release"
   # Live at cache.financialdata.online
   ```

### **CI/CD Integration**

Example GitHub Actions workflow:

```yaml
name: Deploy Worker
on:
  push:
    branches: [main]
    tags: ['v*']

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Deploy to Staging
        if: github.ref == 'refs/heads/main'
        run: ./deploy-versioned.sh -e staging -a
        
      - name: Deploy to Production  
        if: startsWith(github.ref, 'refs/tags/v')
        run: ./deploy-versioned.sh -e production -v ${GITHUB_REF#refs/tags/}
```

## 🛠️ Troubleshooting

### **Common Issues**

**Version Conflict**:
```bash
# If deployment fails due to version conflict
./rollback.sh -e production -v previous-working-version
```

**Config Errors**:
```bash
# Validate configuration
npx wrangler deploy --dry-run --config wrangler.production.jsonc
```

**Authentication Issues**:
```bash
# Re-authenticate
npx wrangler login
npx wrangler whoami
```

### **Monitoring**

**Check Deployment Status**:
```bash
# View worker status
npx wrangler status

# View worker logs
npx wrangler tail --config wrangler.production.jsonc
```

**Health Monitoring**:
```bash
# Monitor all environments
curl https://cache-dev.financialdata.online/health
curl https://cache-staging.financialdata.online/health  
curl https://cache.financialdata.online/health
```

## 📊 Benefits of This Versioning Strategy

### **🔐 Safety**
- **Environment Isolation**: Separate configs prevent accidental production deployments
- **Rollback Capability**: Quick rollback to any previous version
- **Confirmation Prompts**: Production deployments require confirmation

### **📈 Scalability**  
- **Multiple Environments**: Support for dev, staging, and production
- **Git Integration**: Automatic tagging and version tracking
- **CI/CD Ready**: Easy integration with automated pipelines

### **🔍 Observability**
- **Version Tracking**: Every request includes version information
- **Health Endpoints**: Easy monitoring and debugging
- **Deployment History**: Full audit trail via git tags

### **🚀 Development Speed**
- **Quick Deployments**: Simple commands for any environment
- **Auto-Versioning**: No manual version management needed
- **Easy Testing**: Dedicated environments for testing

## 🎯 Best Practices

1. **Always test in development first**
2. **Use staging for QA and integration testing**
3. **Tag production releases with semantic versions**
4. **Keep rollback capability ready**
5. **Monitor health endpoints after deployments**
6. **Use descriptive deployment messages**
7. **Maintain environment-specific configurations**

Your Cloudflare Worker now has enterprise-grade versioning and deployment capabilities! 🚀 