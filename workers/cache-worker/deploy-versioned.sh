#!/bin/bash

# Versioned Cloudflare Worker Deployment Script
# Supports multiple environments and semantic versioning

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Default values
ENVIRONMENT="dev"
VERSION=""
DEPLOY_MESSAGE=""
AUTO_VERSION=false

# Helper functions
print_usage() {
    echo "Usage: $0 [OPTIONS]"
    echo ""
    echo "Options:"
    echo "  -e, --env ENVIRONMENT     Environment to deploy to (dev|staging|production)"
    echo "  -v, --version VERSION     Specific version to deploy (e.g., v1.2.3)"
    echo "  -m, --message MESSAGE     Deployment message"
    echo "  -a, --auto-version        Auto-generate version from git"
    echo "  -h, --help               Show this help message"
    echo ""
    echo "Examples:"
    echo "  $0 -e dev                           # Deploy to development"
    echo "  $0 -e staging -v v1.2.3            # Deploy specific version to staging"
    echo "  $0 -e production -a                # Deploy to production with auto-version"
    echo "  $0 -e production -v v1.0.0 -m \"Initial release\""
}

print_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        -e|--env)
            ENVIRONMENT="$2"
            shift 2
            ;;
        -v|--version)
            VERSION="$2"
            shift 2
            ;;
        -m|--message)
            DEPLOY_MESSAGE="$2"
            shift 2
            ;;
        -a|--auto-version)
            AUTO_VERSION=true
            shift
            ;;
        -h|--help)
            print_usage
            exit 0
            ;;
        *)
            print_error "Unknown option $1"
            print_usage
            exit 1
            ;;
    esac
done

# Validate environment
if [[ ! "$ENVIRONMENT" =~ ^(dev|staging|production)$ ]]; then
    print_error "Invalid environment: $ENVIRONMENT"
    print_error "Must be one of: dev, staging, production"
    exit 1
fi

# Generate version if auto-version is enabled
if [[ "$AUTO_VERSION" == true ]]; then
    if git rev-parse --git-dir > /dev/null 2>&1; then
        GIT_COMMIT=$(git rev-parse --short HEAD)
        GIT_BRANCH=$(git rev-parse --abbrev-ref HEAD)
        TIMESTAMP=$(date +%Y%m%d-%H%M%S)
        
        case $ENVIRONMENT in
            "production")
                # For production, use latest git tag or create one
                LATEST_TAG=$(git describe --tags --abbrev=0 2>/dev/null || echo "v0.0.0")
                VERSION="$LATEST_TAG"
                ;;
            "staging")
                VERSION="staging-$TIMESTAMP-$GIT_COMMIT"
                ;;
            "dev")
                VERSION="dev-$GIT_BRANCH-$GIT_COMMIT"
                ;;
        esac
    else
        print_warning "Not in a git repository, using timestamp for version"
        VERSION="$ENVIRONMENT-$(date +%Y%m%d-%H%M%S)"
    fi
fi

# Set default version if not provided
if [[ -z "$VERSION" ]]; then
    case $ENVIRONMENT in
        "production")
            VERSION="v1.0.0"
            ;;
        "staging")
            VERSION="staging-latest"
            ;;
        "dev")
            VERSION="dev-latest"
            ;;
    esac
fi

# Configuration file selection
CONFIG_FILE="wrangler.$ENVIRONMENT.jsonc"
if [[ ! -f "$CONFIG_FILE" ]]; then
    print_error "Configuration file not found: $CONFIG_FILE"
    exit 1
fi

echo "🚀 Cloudflare Worker Versioned Deployment"
echo "==========================================="
print_info "Environment: $ENVIRONMENT"
print_info "Version: $VERSION"
print_info "Config: $CONFIG_FILE"
if [[ -n "$DEPLOY_MESSAGE" ]]; then
    print_info "Message: $DEPLOY_MESSAGE"
fi
echo ""

# Check if wrangler is authenticated
print_info "Checking Wrangler authentication..."
if ! npx wrangler whoami > /dev/null 2>&1; then
    print_warning "Wrangler not authenticated. Running login..."
    npx wrangler login
else
    print_success "Wrangler authenticated"
fi

# Update version in config file
print_info "Updating version in configuration..."
TEMP_CONFIG=$(mktemp)
sed "s/\"VERSION\": \"[^\"]*\"/\"VERSION\": \"$VERSION\"/g" "$CONFIG_FILE" > "$TEMP_CONFIG"
mv "$TEMP_CONFIG" "$CONFIG_FILE"

# Deploy the worker
print_info "Deploying worker to Cloudflare..."
if npx wrangler deploy --config "$CONFIG_FILE"; then
    print_success "Deployment successful!"
else
    print_error "Deployment failed!"
    exit 1
fi

# Get worker URL
WORKER_NAME=$(grep '"name":' "$CONFIG_FILE" | sed 's/.*"name": *"\([^"]*\)".*/\1/')
WORKER_URL="https://$WORKER_NAME.YOUR-SUBDOMAIN.workers.dev"

echo ""
print_success "Deployment Summary"
echo "=================="
echo "Environment: $ENVIRONMENT"
echo "Version: $VERSION"
echo "Worker Name: $WORKER_NAME"
echo "Worker URL: $WORKER_URL"

# Test the deployment
print_info "Testing deployment..."
if curl -s "$WORKER_URL/health" > /dev/null; then
    print_success "Health check passed"
    
    # Show health endpoint response
    echo ""
    print_info "Health endpoint response:"
    curl -s "$WORKER_URL/health" | jq '.' 2>/dev/null || curl -s "$WORKER_URL/health"
else
    print_warning "Health check failed - worker might still be deploying"
fi

# Git tagging for production
if [[ "$ENVIRONMENT" == "production" && "$AUTO_VERSION" == true ]]; then
    print_info "Creating git tag for production deployment..."
    if git tag -a "$VERSION" -m "Production deployment: $VERSION${DEPLOY_MESSAGE:+ - $DEPLOY_MESSAGE}"; then
        print_success "Git tag created: $VERSION"
        print_info "Push tag with: git push origin $VERSION"
    else
        print_warning "Git tag creation failed (tag might already exist)"
    fi
fi

echo ""
print_success "🎉 Deployment completed successfully!"

# Environment-specific next steps
case $ENVIRONMENT in
    "dev")
        echo ""
        print_info "Development deployment ready for testing"
        ;;
    "staging")
        echo ""
        print_info "Staging deployment ready for QA testing"
        print_info "Promote to production with: $0 -e production -v $VERSION"
        ;;
    "production")
        echo ""
        print_success "🌍 Production deployment live!"
        if [[ -n "$DEPLOY_MESSAGE" ]]; then
            print_info "📝 Release notes: $DEPLOY_MESSAGE"
        fi
        ;;
esac 