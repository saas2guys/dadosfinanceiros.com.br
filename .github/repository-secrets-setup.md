# GitHub Secrets Setup Guide

## Required Secrets

The following GitHub repository secrets need to be configured for the Terraform automation to work:

### 1. DO_TOKEN
- **Value**: Your DigitalOcean API Token
- **Required**: Yes
- **Description**: Used to authenticate with DigitalOcean API for DNS management

### 2. APP_DOMAIN  
- **Value**: Your App Platform domain (optional)
- **Required**: No
- **Description**: Your DigitalOcean App Platform domain for CNAME fallback
- **Example**: `financialdata-online-bbce29b0.ondigitalocean.app`

## Setup Instructions

1. Go to: https://github.com/saas2guys/financialdata.online/settings/secrets/actions
2. Click "New repository secret"
3. Add each secret with the exact name and value above

## Security Notes

- These secrets are encrypted and only accessible by GitHub Actions
- Never commit sensitive values to the repository
- The DigitalOcean token should have limited permissions (DNS management only)

## After Setup

Once secrets are configured, push any changes to the `terraform/` directory to trigger the automated DNS management.