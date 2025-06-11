# 🤖 IP Automation for DigitalOcean App Platform

This guide explains how to automate the fetching of DigitalOcean App Platform IP addresses instead of hardcoding them in your Terraform configuration.

## 🎯 **Why Automate IP Fetching?**

### **Current Problem**
```hcl
# Hardcoded IPs in main.tf
locals {
  app_ipv4_primary = "162.159.140.98"    # What if this changes?
  app_ipv4_secondary = "172.66.0.96"     # Manual updates required
  app_ipv6_primary = "2606:4700:7::60"   # No validation
  app_ipv6_secondary = "2a06:98c1:58::60" # Risk of outdated IPs
}
```

### **Automated Solution Benefits**
✅ **Always Current**: IPs are fetched in real-time  
✅ **Zero Maintenance**: No manual updates needed  
✅ **Multiple Fallbacks**: Several methods with graceful degradation  
✅ **Validation**: Verify IPs before using them  
✅ **Transparency**: See which method was used in outputs  

## 🔧 **Available Automation Methods**

### **Method 1: DNS Resolution (Recommended)**

**How it works**: Resolves your App Platform domain to get current IPs

```hcl
# DNS resolution to get current App Platform IPs
data "dns_a_record_set" "app_ipv4" {
  count = var.app_domain != "" ? 1 : 0
  host  = var.app_domain
}

data "dns_aaaa_record_set" "app_ipv6" {
  count = var.app_domain != "" ? 1 : 0
  host  = var.app_domain
}

locals {
  # Use resolved IPs or fallback to static IPs
  app_ipv4_primary = length(local.resolved_ipv4_addresses) > 0 ? 
    local.resolved_ipv4_addresses[0] : "162.159.140.98"
}
```

**Configuration**:
```hcl
# terraform.tfvars
app_domain = "your-app.ondigitalocean.app"
enable_ip_automation = true
```

**Pros**:
- ✅ Simple and reliable
- ✅ Works with any domain
- ✅ Fast execution
- ✅ No API dependencies

**Cons**:
- ❌ Requires app domain to be set
- ❌ DNS propagation delays

### **Method 2: DigitalOcean API**

**How it works**: Queries DO API for app details, then resolves the live URL

```hcl
data "http" "digitalocean_app_ips" {
  url = "https://api.digitalocean.com/v2/apps/${var.app_id}"
  request_headers = {
    Authorization = "Bearer ${var.do_token}"
    Content-Type  = "application/json"
  }
}
```

**Configuration**:
```hcl
# terraform.tfvars
app_id = "bbce29b0-3bff-4306-a11b-e6a539beef04"
do_token = "dop_v1_..."
enable_ip_automation = true
```

**Pros**:
- ✅ Gets data directly from source
- ✅ Works even if domain changes
- ✅ Can fetch additional app metadata

**Cons**:
- ❌ Requires API token
- ❌ API rate limits
- ❌ More complex

### **Method 3: External Shell Script**

**How it works**: Runs a bash script that uses multiple methods

```bash
#!/bin/bash
# get-app-ips.sh
eval "$(jq -r '@sh "APP_DOMAIN=\(.app_domain)"')"

# Try dig first, fallback to nslookup
if command -v dig >/dev/null 2>&1; then
    ipv4_ips=($(dig +short A "$APP_DOMAIN"))
else
    # nslookup fallback
fi

echo "{"
echo "  \"ipv4_primary\": \"${ipv4_ips[0]:-162.159.140.98}\","
echo "}"
```

**Configuration**:
```hcl
data "external" "app_ips" {
  program = ["bash", "${path.module}/scripts/get-app-ips.sh"]
  query = {
    app_domain = var.app_domain
    do_token   = var.do_token
  }
}
```

**Pros**:
- ✅ Maximum flexibility
- ✅ Can combine multiple methods
- ✅ Custom logic possible
- ✅ Good error handling

**Cons**:
- ❌ Requires shell/bash
- ❌ More complex to maintain
- ❌ Platform dependent

### **Method 4: Static IP Ranges API**

**How it works**: Queries DigitalOcean's official IP ranges

```hcl
data "http" "do_ip_ranges" {
  url = "https://api.digitalocean.com/v2/apps/ips"
  request_headers = {
    Authorization = "Bearer ${var.do_token}"
  }
}
```

**Note**: This is future-proofing as DO may provide an official IP ranges endpoint.

## 📦 **Implementation Guide**

### **Step 1: Choose Your Method**

For most users, **Method 1 (DNS Resolution)** is recommended:

```hcl
# terraform.tfvars
app_domain = "your-app.ondigitalocean.app"
enable_ip_automation = true
```

### **Step 2: Update Variables**

```hcl
# variables.tf
variable "enable_ip_automation" {
  description = "Enable automated IP fetching"
  type        = bool
  default     = true
}

variable "app_domain" {
  description = "Your App Platform domain"
  type        = string
  default     = ""
}
```

### **Step 3: Configure Data Sources**

```hcl
# main.tf
data "dns_a_record_set" "app_ipv4" {
  count = var.app_domain != "" ? 1 : 0
  host  = var.app_domain
}

locals {
  resolved_ipv4_addresses = var.app_domain != "" ? 
    data.dns_a_record_set.app_ipv4[0].addrs : []
    
  app_ipv4_primary = length(local.resolved_ipv4_addresses) > 0 ? 
    local.resolved_ipv4_addresses[0] : "162.159.140.98"
}
```

### **Step 4: Add Validation Output**

```hcl
output "detected_ips" {
  value = {
    method_used = var.enable_ip_automation ? "automated" : "static"
    ipv4_primary   = local.app_ipv4_primary
    ipv4_secondary = local.app_ipv4_secondary
    source_domain  = var.app_domain
  }
}
```

## 🧪 **Testing Your Automation**

### **1. Test DNS Resolution Manually**

```bash
# Test IPv4 resolution
dig your-app.ondigitalocean.app A +short

# Test IPv6 resolution  
dig your-app.ondigitalocean.app AAAA +short

# Expected output:
# 162.159.140.98
# 172.66.0.96
```

### **2. Test Shell Script**

```bash
# Make script executable
chmod +x terraform/scripts/get-app-ips.sh

# Test script directly
echo '{"app_domain":"your-app.ondigitalocean.app","do_token":""}' | \
  ./terraform/scripts/get-app-ips.sh

# Expected output:
# {
#   "ipv4_primary": "162.159.140.98",
#   "method": "dns",
#   "domain": "your-app.ondigitalocean.app"
# }
```

### **3. Test Terraform Execution**

```bash
# Initialize and validate
cd terraform/
terraform init
terraform validate

# Plan to see what will be detected
terraform plan

# Apply and check outputs
terraform apply
terraform output detected_ips
```

### **4. Verify DNS Records**

```bash
# After terraform apply, verify DNS records
dig financialdata.online A +short
dig www.financialdata.online A +short

# Should return the auto-detected IPs
```

## ⚡ **Quick Start Examples**

### **Basic DNS Resolution Setup**

```hcl
# terraform.tfvars
do_token = "dop_v1_your_token"
app_domain = "your-app-abc123.ondigitalocean.app"
enable_ip_automation = true
```

```bash
terraform apply
# ✅ IPs automatically detected and used
```

### **API + DNS Hybrid Setup**

```hcl
# terraform.tfvars
do_token = "dop_v1_your_token"
app_id = "your-app-id"
app_domain = "your-app.ondigitalocean.app"  # fallback
enable_ip_automation = true
```

### **Disable Automation (Static IPs)**

```hcl
# terraform.tfvars
enable_ip_automation = false
# Uses hardcoded static IPs as fallback
```

## 🚀 **NEW: Native DigitalOcean IP Automation**

Instead of using external bash scripts, the system now uses the **native DigitalOcean Terraform provider** to automate IP detection. This is more reliable, faster, and has no external dependencies.

## 🎯 **Native Terraform Approach**

### **Method 1: DigitalOcean App Data Source (Recommended)**

**How it works**: Uses the official DigitalOcean Terraform provider to fetch app details directly

```hcl
# Native DigitalOcean app data source
data "digitalocean_app" "main_app" {
  count = var.app_id != "" && var.enable_ip_automation ? 1 : 0
  id    = var.app_id
}

# DNS resolution for the app's live URL
data "dns_a_record_set" "app_live_url_ipv4" {
  count = var.app_id != "" && length(data.digitalocean_app.main_app) > 0 ? 1 : 0
  host  = replace(data.digitalocean_app.main_app[0].live_url, "https://", "")
}

locals {
  # Smart IP detection with fallbacks
  app_ipv4_primary = length(local.app_data_ipv4_addresses) > 0 ? 
    local.app_data_ipv4_addresses[0] : "162.159.140.98"
}
```

**Configuration**:
```hcl
# terraform.tfvars (RECOMMENDED)
app_id = "bbce29b0-3bff-4306-a11b-e6a539beef04"  # Your app ID
enable_ip_automation = true
```

**Advantages**:
- ✅ **Pure Terraform**: No external scripts or dependencies
- ✅ **Always Current**: Gets live URL directly from DigitalOcean  
- ✅ **Reliable**: Uses official DigitalOcean provider
- ✅ **Rich Data**: Access to full app metadata
- ✅ **Error Handling**: Better Terraform-native error handling
- ✅ **Fast**: No external process execution

**Benefits Over Bash Scripts**:
- 🚫 No bash/jq/curl dependencies
- 🚫 No external script execution  
- 🚫 No shell command security concerns
- 🚫 Cross-platform compatibility issues
- ✅ Native Terraform state management
- ✅ Better error handling and debugging
- ✅ Faster execution

### **Method 2: Manual Domain DNS (Fallback)**

For cases where you don't have the app ID:

```hcl
# terraform.tfvars (FALLBACK)
app_domain = "your-app.ondigitalocean.app"
enable_ip_automation = true
```

## 📦 **Quick Implementation**

### **Step 1: Get Your App ID**

From your DigitalOcean App Platform URL:
```
https://cloud.digitalocean.com/apps/bbce29b0-3bff-4306-a11b-e6a539beef04
                                    ^-- This is your app_id
```

### **Step 2: Update Configuration**

```hcl
# terraform.tfvars
do_token = "your_digitalocean_token"
app_id = "bbce29b0-3bff-4306-a11b-e6a539beef04"
enable_ip_automation = true
```

### **Step 3: Deploy**

```bash
cd terraform/
terraform init  # Downloads DNS provider
terraform apply # Detects IPs automatically
```

### **Step 4: Verify Results**

```bash
# View detection summary
terraform output ip_detection_summary

# View app details
terraform output app_details

# Test the detected IPs
dig financialdata.online A +short
```

## 🧪 **Testing the Native Method**

### **1. Test App Data Source**

```bash
# Verify app data source works
terraform console
> data.digitalocean_app.main_app[0].live_url
> data.digitalocean_app.main_app[0].spec[0].name
```

### **2. Test IP Detection**

```bash
# Check detection method used
terraform output ip_detection_summary
# Expected: "digitalocean_app_data_source"

# Verify IPs detected
terraform output detected_ips
```

### **3. Verify DNS Records**

```bash
# Test all your domains resolve correctly
for domain in financialdata.online financialdata.digital financialdata.online financialdata.online; do
  echo "Testing $domain:"
  dig $domain A +short
done
```

## ⚡ **Performance Comparison**

| Method | Speed | Reliability | Dependencies | Maintenance |
|--------|-------|-------------|--------------|-------------|
| **Native DO Provider** | ⚡ Fastest | 🟢 Highest | None | 🟢 Zero |
| Bash Script | 🟡 Medium | 🟡 Medium | bash,jq,curl | 🔴 High |
| Static IPs | ⚡ Instant | 🟡 Medium | None | 🔴 Manual |

## 🔧 **Migration from Bash Scripts**

### **Before (Bash Script Method)**:
```hcl
# Complex external script approach
data "external" "app_ips" {
  program = ["bash", "${path.module}/scripts/get-app-ips.sh"]
  query = {
    app_domain = var.app_domain
    do_token   = var.do_token
  }
}
```

**Issues**:
- ❌ External dependencies (bash, jq, curl)
- ❌ Cross-platform compatibility issues  
- ❌ Security concerns with shell execution
- ❌ Complex error handling
- ❌ Slower execution

### **After (Native Method)**:
```hcl
# Clean native Terraform approach
data "digitalocean_app" "main_app" {
  count = var.app_id != "" ? 1 : 0
  id    = var.app_id
}
```

**Benefits**:
- ✅ Pure Terraform, no external dependencies
- ✅ Cross-platform compatible
- ✅ Secure, no shell execution
- ✅ Better error handling and debugging
- ✅ Faster execution

### **Migration Steps**:

1. **Get your app ID** from the DigitalOcean console
2. **Update terraform.tfvars** with your app_id
3. **Remove script dependencies** (optional, keeping for compatibility)
4. **Run terraform apply** to test new method
5. **Verify detection method** in outputs

## 🏗️ **Complete Example**

Here's a working example configuration:

```hcl
# terraform.tfvars
do_token = "dop_v1_your_token_here"
app_id = "bbce29b0-3bff-4306-a11b-e6a539beef04"
enable_ip_automation = true

# Optional fallback
app_domain = "your-app.ondigitalocean.app"
```

```bash
# Deploy
terraform init
terraform apply

# Verify
terraform output ip_detection_summary
# Should show: detection_method = "digitalocean_app_data_source"
```

## 🎉 **Results**

With the native DigitalOcean approach, your Terraform configuration:

✅ **Fetches IPs directly** from DigitalOcean's API  
✅ **No external dependencies** required  
✅ **Works across all platforms** (Windows, Mac, Linux)  
✅ **Provides rich app metadata** for additional automation  
✅ **Executes faster** than script-based methods  
✅ **Better error handling** with clear Terraform messages  

The native approach is the **recommended method** for production deployments! 🚀

## 🔍 **Troubleshooting**

### **Problem: DNS Resolution Fails**

```bash
# Check if domain resolves
nslookup your-app.ondigitalocean.app

# Check if dig is installed
which dig
```

**Solutions**:
- Verify app domain is correct
- Ensure app is deployed and running
- Wait for DNS propagation (up to 48 hours)
- Use static IP fallback temporarily

### **Problem: API Authentication Fails**

```bash
# Test API access manually
curl -H "Authorization: Bearer $DO_TOKEN" \
  https://api.digitalocean.com/v2/apps/$APP_ID
```

**Solutions**:
- Verify DO_TOKEN is correct
- Check token permissions
- Ensure app_id is correct
- Use DNS method instead

### **Problem: Script Execution Fails**

```bash
# Check script permissions
ls -la terraform/scripts/get-app-ips.sh

# Test script dependencies
which jq bash curl dig
```

**Solutions**:
- Make script executable: `chmod +x get-app-ips.sh`
- Install missing dependencies
- Use simpler DNS method

## 📈 **Performance Comparison**

| Method | Speed | Reliability | Complexity | Dependencies |
|--------|-------|-------------|------------|--------------|
| DNS Resolution | ⚡ Fast | 🟢 High | 🟢 Low | dig/nslookup |
| DigitalOcean API | ⚡ Fast | 🟡 Medium | 🟡 Medium | curl, API token |
| External Script | 🟡 Medium | 🟢 High | 🔴 High | bash, jq, curl |
| Static IPs | ⚡ Instant | 🟡 Medium | 🟢 Low | None |

## 🚀 **Advanced Configuration**

### **Multiple Fallback Layers**

```hcl
locals {
  # Try methods in order of preference
  app_ipv4_primary = coalesce(
    try(local.external_ips.ipv4_primary, null),     # Script method
    try(local.resolved_ipv4_addresses[0], null),    # DNS method
    try(local.http_app_data.live_url_ip, null),     # API method
    "162.159.140.98"                                # Static fallback
  )
}
```

### **Custom Validation**

```hcl
# Validate detected IPs
locals {
  is_valid_ipv4 = can(regex("^(?:[0-9]{1,3}\\.){3}[0-9]{1,3}$", local.app_ipv4_primary))
  
  validated_ipv4_primary = local.is_valid_ipv4 ? 
    local.app_ipv4_primary : "162.159.140.98"
}
```

### **Conditional Automation**

```hcl
# Enable automation only for production
variable "environment" {
  description = "Environment (dev/staging/prod)"
  type        = string
  default     = "dev"
}

locals {
  enable_automation = var.environment == "prod" && var.enable_ip_automation
}
```

## 🔐 **Security Considerations**

1. **API Token Protection**:
   ```hcl
   variable "do_token" {
     sensitive = true  # Never log token
   }
   ```

2. **Validate External Scripts**:
   ```bash
   # Always verify script content
   cat terraform/scripts/get-app-ips.sh
   ```

3. **IP Validation**:
   ```hcl
   # Validate IP format before use
   validation {
     condition = can(regex("^(?:[0-9]{1,3}\\.){3}[0-9]{1,3}$", var.custom_ip))
     error_message = "Invalid IP address format."
   }
   ```

## 📋 **Migration Checklist**

- [ ] Choose automation method (DNS recommended)
- [ ] Update `variables.tf` with new variables
- [ ] Add data sources to `main.tf`
- [ ] Update `terraform.tfvars` with your app domain
- [ ] Test with `terraform plan`
- [ ] Apply changes with `terraform apply`
- [ ] Verify outputs with `terraform output detected_ips`
- [ ] Test DNS resolution of your domains
- [ ] Document the changes for your team

## 🎉 **Result**

After implementing IP automation, your Terraform configuration will:

✅ **Automatically detect current IPs** on every run  
✅ **Eliminate manual IP updates** when DigitalOcean changes IPs  
✅ **Provide multiple fallback methods** for reliability  
✅ **Show transparent reporting** of which method was used  
✅ **Maintain high availability** with graceful degradation  

Your DNS automation is now truly hands-off and production-ready! 🚀 