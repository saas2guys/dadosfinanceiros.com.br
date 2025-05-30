# 🚀 Automated DNS Management with Terraform

This repository now includes automated DNS management for your DigitalOcean App Platform application using Terraform and GitHub Actions.

## 📋 Quick Start

### 1. Set GitHub Secrets

Go to your repository settings and add these secrets:

- **`DO_TOKEN`**: `asdasdasdasdasd`
- **`APP_DOMAIN`**: `dadosfinanceiros-com-br-bbce29b0.ondigitalocean.app` (optional)

**Steps:**
1. Go to [Repository Settings](https://github.com/saas2guys/dadosfinanceiros.com.br/settings/secrets/actions)
2. Click "New repository secret"
3. Add both secrets above

### 2. Push to Main Branch

The automation will automatically:
✅ Create DNS records for all 4 domains  
✅ Configure load balancing with redundant IPs  
✅ Set up both IPv4 and IPv6 records  
✅ Use optimized TTL settings  

### 3. Add Domains to App Platform

After DNS records are created:
1. Go to your [App Platform app](https://cloud.digitalocean.com/apps/bbce29b0-3bff-4306-a11b-e6a539beef04)
2. **Settings** → **Domains** → **Edit**
3. Add each domain:
   - `financialdata.online`
   - `www.financialdata.online`
   - `financialdata.digital`
   - `www.financialdata.digital`
   - `dadosfinanceiros.com`
   - `www.dadosfinanceiros.com`
   - `dadosfinanceiros.com.br`
   - `www.dadosfinanceiros.com.br`

## 🎯 What This Setup Does

### Domains Managed
- **financialdata.online** + www
- **financialdata.digital** + www  
- **dadosfinanceiros.com** + www
- **dadosfinanceiros.com.br** + www

### DNS Configuration
- **A Records**: Point to DigitalOcean App Platform static IPs
- **AAAA Records**: IPv6 support for modern browsers
- **Redundancy**: Multiple IPs for high availability
- **Fast TTL**: 5-minute cache for quick updates

### Automation Features
- 🤖 **Auto-apply** on main branch pushes
- 👀 **Plan preview** on pull requests  
- 🔧 **Manual triggers** via GitHub Actions
- 📝 **Detailed logging** for troubleshooting

## 📁 File Structure

```
.github/workflows/terraform.yml    # GitHub Actions workflow
terraform/
├── main.tf                       # DNS resources configuration
├── variables.tf                  # Variable definitions
├── terraform.tfvars.example     # Configuration template
└── .gitignore                   # Ignore sensitive files
docs/terraform-setup.md          # Detailed documentation
```

## 🔍 Verification

After setup, verify everything works:

```bash
# Test DNS resolution
dig financialdata.online A
dig www.financialdata.online A

# Expected IPs: 162.159.140.98, 172.66.0.96
```

## 📖 Documentation

For detailed instructions and troubleshooting, see:
**[docs/terraform-setup.md](docs/terraform-setup.md)**

## 🚨 Important Notes

- **Never commit** `terraform.tfvars` (contains your API token)
- **Wait for DNS propagation** (up to 48 hours for nameserver changes)
- **Add domains to App Platform** after DNS records are created
- **Monitor GitHub Actions** for deployment status

## 🛠️ Local Development

If you want to run Terraform locally:

```bash
cd terraform
cp terraform.tfvars.example terraform.tfvars
# Edit terraform.tfvars with your values
terraform init
terraform plan
terraform apply
```

## 🔗 Quick Links

- [GitHub Actions](https://github.com/saas2guys/dadosfinanceiros.com.br/actions)
- [App Platform App](https://cloud.digitalocean.com/apps/bbce29b0-3bff-4306-a11b-e6a539beef04)
- [DigitalOcean DNS Console](https://cloud.digitalocean.com/networking/domains)
- [Repository Secrets](https://github.com/saas2guys/dadosfinanceiros.com.br/settings/secrets/actions)

---

*🎉 Your DNS is now fully automated! Push changes to the `terraform/` directory to update your DNS configuration.* 