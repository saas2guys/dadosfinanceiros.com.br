# Terraform DNS Management Setup

## Overview
This project uses Terraform to manage DNS records for our domains on DigitalOcean, optimized for DigitalOcean App Platform deployments.

## Domains Managed
- `financialdata.online`
- `financialdata.digital`
- `dadosfinanceiros.com`
- `dadosfinanceiros.com.br`

## DigitalOcean App Platform Integration

This configuration is specifically designed for DigitalOcean App Platform applications. Instead of using individual server IPs, we use DigitalOcean's shared static ingress IPs that are designed for App Platform:

- **Primary IPv4**: `162.159.140.98`
- **Secondary IPv4**: `172.66.0.96`
- **Primary IPv6**: `2606:4700:7::60`
- **Secondary IPv6**: `2a06:98c1:58::60`

These IPs provide load balancing and high availability for your App Platform applications. Reference: [DigitalOcean App Platform Static IPs](https://docs.digitalocean.com/products/app-platform/how-to/add-ip-address/)

## DNS Configuration

For each domain, the following records are created:

### A Records (IPv4)
- **Apex domain** (`@`): Points to both primary and secondary IPs for redundancy
- **www subdomain**: Points to both primary and secondary IPs for redundancy

### AAAA Records (IPv6)
- **Apex domain** (`@`): Points to both primary and secondary IPv6 addresses
- **www subdomain**: Points to both primary and secondary IPv6 addresses

### TTL Configuration
- All records use a **300-second TTL** (5 minutes) for faster propagation during updates

## GitHub Secrets Required

The following secrets must be configured in your GitHub repository:

1. **`DO_TOKEN`**: Your DigitalOcean API token
   - Go to: [DigitalOcean API Tokens](https://cloud.digitalocean.com/account/api/tokens)
   - Create a new token with **read and write** permissions
   - Copy the token value

2. **`APP_DOMAIN`**: Your DigitalOcean App Platform domain (optional)
   - Format: `your-app-name-abc123.ondigitalocean.app`
   - Used as a fallback for CNAME records if needed

### Setting Up GitHub Secrets

1. Go to your repository: https://github.com/saas2guys/dadosfinanceiros.com.br
2. Navigate to: **Settings** → **Secrets and variables** → **Actions**
3. Click **"New repository secret"** for each:
   - **Name**: `DO_TOKEN`, **Value**: `dop_v1_a679a980ac1921aaacd5d9a0422922ef51f180a5a349e4923c0637680242713c`
   - **Name**: `APP_DOMAIN`, **Value**: `dadosfinanceiros-com-br-bbce29b0.ondigitalocean.app` (adjust as needed)

## Local Development

### Prerequisites
- [Terraform](https://www.terraform.io/downloads.html) installed (version 1.0+)
- DigitalOcean API token

### Setup Steps

1. **Copy the example configuration**:
   ```bash
   cd terraform
   cp terraform.tfvars.example terraform.tfvars
   ```

2. **Edit `terraform.tfvars`** with your actual values:
   ```hcl
   do_token = "dop_v1_a679a980ac1921aaacd5d9a0422922ef51f180a5a349e4923c0637680242713c"
   app_domain = "dadosfinanceiros-com-br-bbce29b0.ondigitalocean.app"
   ```

3. **Initialize and apply**:
   ```bash
   terraform init
   terraform plan
   terraform apply
   ```

## GitHub Actions Automation

The automation runs automatically when:

- **Push to main branch**: Changes in `terraform/` directory trigger automatic apply
- **Pull requests**: Shows a plan preview as a comment
- **Manual trigger**: Use the "Actions" tab to run manually

### Workflow Features

- ✅ **Format checking**: Ensures code follows Terraform standards
- ✅ **Validation**: Checks configuration syntax
- ✅ **Plan preview**: Shows what changes will be made
- ✅ **Automatic apply**: Only on main branch pushes
- ✅ **Pull request comments**: Shows plans for review

## Domain Setup Requirements

### For New Domains

If your domains are **not yet registered** or **not pointing to DigitalOcean**:

1. **Register domains** through your preferred registrar
2. **Update nameservers** to point to DigitalOcean:
   - `ns1.digitalocean.com`
   - `ns2.digitalocean.com`
   - `ns3.digitalocean.com`

### For Existing Domains

If domains are registered elsewhere but you want to use DigitalOcean DNS:

1. **Keep your current registrar**
2. **Update nameservers** to DigitalOcean's nameservers (above)
3. **Wait for propagation** (up to 48 hours)

## App Platform Domain Configuration

After the DNS records are created, you need to add the domains to your App Platform app:

1. **Go to your app**: https://cloud.digitalocean.com/apps/bbce29b0-3bff-4306-a11b-e6a539beef04
2. **Settings tab** → **Domains** section → **Edit**
3. **Add each domain**:
   - `financialdata.online`
   - `www.financialdata.online`
   - `financialdata.digital`
   - `www.financialdata.digital`
   - `dadosfinanceiros.com`
   - `www.dadosfinanceiros.com`
   - `dadosfinanceiros.com.br`
   - `www.dadosfinanceiros.com.br`

4. **Choose "Point to DigitalOcean"** (not delegate) since we're managing DNS with Terraform

## Verification Steps

### 1. Check GitHub Actions
- Go to: **Actions** tab in your repository
- Verify the workflow runs successfully
- Review any error messages

### 2. Test DNS Resolution
```bash
# Test A records
dig financialdata.online A
dig www.financialdata.online A

# Test AAAA records (IPv6)
dig financialdata.online AAAA
dig www.financialdata.online AAAA

# Expected IPs:
# A records: 162.159.140.98, 172.66.0.96
# AAAA records: 2606:4700:7::60, 2a06:98c1:58::60
```

### 3. Check DigitalOcean Console
- **Networking** → **Domains**
- Verify all 4 domains are listed
- Check that records match the configuration

### 4. Test Website Access
- Visit each domain in a browser
- Check both apex and www versions
- Verify SSL certificates are issued (may take a few minutes)

## Ongoing Usage

### Making DNS Changes
1. **Edit** `terraform/main.tf`
2. **Commit and push** to main branch
3. **Monitor** GitHub Actions for automatic deployment

### Adding New Domains
1. **Add domain resources** to `terraform/main.tf`
2. **Follow the same pattern** as existing domains
3. **Add the domain** to your App Platform app settings

### Manual Execution
- Use **"Run workflow"** button in GitHub Actions
- Or run locally with `terraform apply`

## Troubleshooting

### Common Issues

**❌ DigitalOcean API Authentication Failed**
- Check that `DO_TOKEN` secret is correctly set
- Verify token has read/write permissions
- Ensure token hasn't expired

**❌ Domain Already Exists**
- Domain might already exist in DigitalOcean
- Check the DigitalOcean console
- Import existing domain: `terraform import digitalocean_domain.example example.com`

**❌ DNS Not Resolving**
- Wait for propagation (up to 48 hours for nameserver changes)
- Check nameservers: `dig NS example.com`
- Verify domain is added to App Platform app

**❌ SSL Certificate Issues**
- Add domain to App Platform app first
- Wait for DigitalOcean to issue certificates (automatic)
- Check App Platform app settings for certificate status

### Getting Help

1. **Check GitHub Actions logs** for detailed error messages
2. **Review DigitalOcean console** for domain/DNS status
3. **Test DNS resolution** with `dig` or online tools
4. **Check App Platform app** domain configuration

## Security Best Practices

- ✅ **Never commit** `terraform.tfvars` to git
- ✅ **Use GitHub Secrets** for sensitive values
- ✅ **Regularly rotate** API tokens
- ✅ **Monitor** GitHub Actions logs for exposed secrets
- ✅ **Limit API token** permissions to DNS management only

## Cost Information

- **DNS hosting**: Free for DigitalOcean customers
- **Domain registration**: Separate cost (if using DigitalOcean Domains)
- **App Platform**: Existing cost, no additional charges for DNS

## Advanced Configuration

### Custom TTL Values
Edit the `ttl` values in `main.tf`:
```hcl
resource "digitalocean_record" "example" {
  # ... other configuration ...
  ttl = 3600  # 1 hour instead of 5 minutes
}
```

### Additional Record Types
Add other DNS record types as needed:
```hcl
# MX Record for email
resource "digitalocean_record" "mail" {
  domain   = digitalocean_domain.example.name
  type     = "MX"
  name     = "@"
  value    = "mail.example.com."
  priority = 10
  ttl      = 300
}
```

### CNAME Alternative
If you prefer CNAME records (for subdomains only):
```hcl
resource "digitalocean_record" "www_cname" {
  domain = digitalocean_domain.example.name
  type   = "CNAME"
  name   = "www"
  value  = "your-app.ondigitalocean.app."
  ttl    = 300
}
```

---

*Last updated: January 2025*
*For issues or questions, check the repository's Issues tab.* 