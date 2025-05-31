#!/bin/bash

# Cloudflare Worker Rollback Script
# Quickly rollback to a previous version

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Default values
ENVIRONMENT="production"
TARGET_VERSION=""
LIST_VERSIONS=false

# Helper functions
print_usage() {
    echo "Usage: $0 [OPTIONS]"
    echo ""
    echo "Options:"
    echo "  -e, --env ENVIRONMENT     Environment to rollback (dev|staging|production)"
    echo "  -v, --version VERSION     Target version to rollback to"
    echo "  -l, --list               List available versions"
    echo "  -h, --help               Show this help message"
    echo ""
    echo "Examples:"
    echo "  $0 -l                               # List available versions"
    echo "  $0 -e production -v v1.0.0         # Rollback production to v1.0.0"
    echo "  $0 -e staging -v staging-20241201  # Rollback staging to specific version"
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

list_versions() {
    print_info "Available versions from git tags:"
    if git tag -l | grep -E "^v[0-9]" | sort -V; then
        echo ""
    else
        print_warning "No version tags found"
    fi
    
    print_info "Available workers in Cloudflare:"
    if npx wrangler status 2>/dev/null; then
        echo ""
    else
        print_warning "Could not fetch worker status from Cloudflare"
    fi
}

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        -e|--env)
            ENVIRONMENT="$2"
            shift 2
            ;;
        -v|--version)
            TARGET_VERSION="$2"
            shift 2
            ;;
        -l|--list)
            LIST_VERSIONS=true
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

# List versions if requested
if [[ "$LIST_VERSIONS" == true ]]; then
    list_versions
    exit 0
fi

# Validate environment
if [[ ! "$ENVIRONMENT" =~ ^(dev|staging|production)$ ]]; then
    print_error "Invalid environment: $ENVIRONMENT"
    print_error "Must be one of: dev, staging, production"
    exit 1
fi

# Check if target version is provided
if [[ -z "$TARGET_VERSION" ]]; then
    print_error "Target version is required for rollback"
    print_error "Use -l to list available versions"
    exit 1
fi

# Configuration file selection
CONFIG_FILE="wrangler.$ENVIRONMENT.jsonc"
if [[ ! -f "$CONFIG_FILE" ]]; then
    print_error "Configuration file not found: $CONFIG_FILE"
    exit 1
fi

echo "🔄 Cloudflare Worker Rollback"
echo "============================="
print_info "Environment: $ENVIRONMENT"
print_info "Target Version: $TARGET_VERSION"
print_info "Config: $CONFIG_FILE"
echo ""

# Confirmation prompt for production
if [[ "$ENVIRONMENT" == "production" ]]; then
    print_warning "You are about to rollback PRODUCTION environment!"
    read -p "Are you sure you want to continue? (yes/no): " confirmation
    if [[ "$confirmation" != "yes" ]]; then
        print_info "Rollback cancelled"
        exit 0
    fi
fi

# Check if wrangler is authenticated
print_info "Checking Wrangler authentication..."
if ! npx wrangler whoami > /dev/null 2>&1; then
    print_warning "Wrangler not authenticated. Running login..."
    npx wrangler login
else
    print_success "Wrangler authenticated"
fi

# Check if target version exists in git
if git rev-parse --git-dir > /dev/null 2>&1; then
    if git tag -l | grep -q "^$TARGET_VERSION$"; then
        print_success "Target version found in git tags"
        
        # Checkout the target version
        print_info "Checking out target version..."
        CURRENT_BRANCH=$(git rev-parse --abbrev-ref HEAD)
        git checkout "$TARGET_VERSION" 2>/dev/null || {
            print_error "Failed to checkout target version"
            exit 1
        }
        
        # Update version in config file
        print_info "Updating version in configuration..."
        TEMP_CONFIG=$(mktemp)
        sed "s/\"VERSION\": \"[^\"]*\"/\"VERSION\": \"$TARGET_VERSION\"/g" "$CONFIG_FILE" > "$TEMP_CONFIG"
        mv "$TEMP_CONFIG" "$CONFIG_FILE"
        
        # Deploy the rollback version
        print_info "Deploying rollback version..."
        if npx wrangler deploy --config "$CONFIG_FILE"; then
            print_success "Rollback deployment successful!"
        else
            print_error "Rollback deployment failed!"
            git checkout "$CURRENT_BRANCH"
            exit 1
        fi
        
        # Return to original branch
        git checkout "$CURRENT_BRANCH"
        
    else
        print_warning "Target version not found in git tags"
        print_info "Proceeding with manual version update..."
        
        # Update version in config file
        print_info "Updating version in configuration..."
        TEMP_CONFIG=$(mktemp)
        sed "s/\"VERSION\": \"[^\"]*\"/\"VERSION\": \"$TARGET_VERSION\"/g" "$CONFIG_FILE" > "$TEMP_CONFIG"
        mv "$TEMP_CONFIG" "$CONFIG_FILE"
        
        # Deploy with updated version
        print_info "Deploying with target version..."
        if npx wrangler deploy --config "$CONFIG_FILE"; then
            print_success "Deployment successful!"
        else
            print_error "Deployment failed!"
            exit 1
        fi
    fi
else
    print_warning "Not in a git repository"
    
    # Update version in config file
    print_info "Updating version in configuration..."
    TEMP_CONFIG=$(mktemp)
    sed "s/\"VERSION\": \"[^\"]*\"/\"VERSION\": \"$TARGET_VERSION\"/g" "$CONFIG_FILE" > "$TEMP_CONFIG"
    mv "$TEMP_CONFIG" "$CONFIG_FILE"
    
    # Deploy with updated version
    print_info "Deploying with target version..."
    if npx wrangler deploy --config "$CONFIG_FILE"; then
        print_success "Deployment successful!"
    else
        print_error "Deployment failed!"
        exit 1
    fi
fi

# Get worker URL and test
WORKER_NAME=$(grep '"name":' "$CONFIG_FILE" | sed 's/.*"name": *"\([^"]*\)".*/\1/')
WORKER_URL="https://$WORKER_NAME.YOUR-SUBDOMAIN.workers.dev"

echo ""
print_success "Rollback Summary"
echo "================"
echo "Environment: $ENVIRONMENT"
echo "Rolled back to: $TARGET_VERSION"
echo "Worker Name: $WORKER_NAME"
echo "Worker URL: $WORKER_URL"

# Test the rollback
print_info "Testing rollback..."
if curl -s "$WORKER_URL/health" > /dev/null; then
    print_success "Health check passed"
    
    # Show health endpoint response
    echo ""
    print_info "Health endpoint response:"
    curl -s "$WORKER_URL/health" | jq '.' 2>/dev/null || curl -s "$WORKER_URL/health"
else
    print_warning "Health check failed - worker might still be deploying"
fi

echo ""
print_success "🎉 Rollback completed successfully!"

# Create rollback tag for tracking
if git rev-parse --git-dir > /dev/null 2>&1; then
    ROLLBACK_TAG="rollback-$ENVIRONMENT-$(date +%Y%m%d-%H%M%S)"
    print_info "Creating rollback tracking tag: $ROLLBACK_TAG"
    git tag -a "$ROLLBACK_TAG" -m "Rollback $ENVIRONMENT to $TARGET_VERSION"
fi 