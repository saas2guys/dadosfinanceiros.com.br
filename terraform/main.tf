terraform {
  required_version = ">= 1.0"
  required_providers {
    digitalocean = {
      source  = "digitalocean/digitalocean"
      version = "~> 2.0"
    }
    dns = {
      source  = "hashicorp/dns"
      version = "~> 3.0"
    }
  }
}

# Configure the DigitalOcean Provider
provider "digitalocean" {
  token = var.do_token
}

# Simple DNS resolution for the provided app domain or use static IPs
data "dns_a_record_set" "app_ipv4" {
  count = var.app_domain != "" ? 1 : 0
  host  = var.app_domain
}

data "dns_aaaa_record_set" "app_ipv6" {
  count = var.app_domain != "" ? 1 : 0
  host  = var.app_domain
}

# IP resolution with fallback to static IPs
locals {
  # Get IPs from DNS resolution or use static fallbacks
  resolved_ipv4_addresses = var.app_domain != "" && length(data.dns_a_record_set.app_ipv4) > 0 ? data.dns_a_record_set.app_ipv4[0].addrs : []
  resolved_ipv6_addresses = var.app_domain != "" && length(data.dns_aaaa_record_set.app_ipv6) > 0 ? data.dns_aaaa_record_set.app_ipv6[0].addrs : []
  
  # Final IP assignment with fallbacks to DigitalOcean's documented static IPs
  app_ipv4_primary   = length(local.resolved_ipv4_addresses) > 0 ? local.resolved_ipv4_addresses[0] : "162.159.140.98"
  app_ipv4_secondary = length(local.resolved_ipv4_addresses) > 1 ? local.resolved_ipv4_addresses[1] : "172.66.0.96"
  app_ipv6_primary   = length(local.resolved_ipv6_addresses) > 0 ? local.resolved_ipv6_addresses[0] : "2606:4700:7::60"
  app_ipv6_secondary = length(local.resolved_ipv6_addresses) > 1 ? local.resolved_ipv6_addresses[1] : "2a06:98c1:58::60"
  
  # Detection method for transparency
  detection_method = length(local.resolved_ipv4_addresses) > 0 ? "dns_resolution" : "static_fallback"
  
  # Source domain used
  source_domain = var.app_domain
}

# ===== financialdata.online =====
resource "digitalocean_domain" "dadosfinanceiros_com" {
  name       = "financialdata.online"
  ip_address = local.app_ipv4_primary
}

# A Records for financialdata.online
resource "digitalocean_record" "financialdata_online_a_secondary" {
  domain = digitalocean_domain.dadosfinanceiros_com.name
  type   = "A"
  name   = "@"
  value  = local.app_ipv4_secondary
  ttl    = 300
}

resource "digitalocean_record" "financialdata_online_www" {
  domain = digitalocean_domain.dadosfinanceiros_com.name
  type   = "A"
  name   = "www"
  value  = local.app_ipv4_primary
  ttl    = 300
}

resource "digitalocean_record" "financialdata_online_www_secondary" {
  domain = digitalocean_domain.dadosfinanceiros_com.name
  type   = "A"
  name   = "www"
  value  = local.app_ipv4_secondary
  ttl    = 300
}

# AAAA Records for financialdata.online (IPv6)
resource "digitalocean_record" "financialdata_online_aaaa" {
  domain = digitalocean_domain.dadosfinanceiros_com.name
  type   = "AAAA"
  name   = "@"
  value  = local.app_ipv6_primary
  ttl    = 300
}

resource "digitalocean_record" "financialdata_online_aaaa_secondary" {
  domain = digitalocean_domain.dadosfinanceiros_com.name
  type   = "AAAA"
  name   = "@"
  value  = local.app_ipv6_secondary
  ttl    = 300
}

resource "digitalocean_record" "financialdata_online_www_aaaa" {
  domain = digitalocean_domain.dadosfinanceiros_com.name
  type   = "AAAA"
  name   = "www"
  value  = local.app_ipv6_primary
  ttl    = 300
}

resource "digitalocean_record" "financialdata_online_www_aaaa_secondary" {
  domain = digitalocean_domain.dadosfinanceiros_com.name
  type   = "AAAA"
  name   = "www"
  value  = local.app_ipv6_secondary
  ttl    = 300
}

# ===== financialdata.digital =====
resource "digitalocean_domain" "financialdata_digital" {
  name       = "financialdata.digital"
  ip_address = local.app_ipv4_primary
}

# A Records for financialdata.digital
resource "digitalocean_record" "financialdata_digital_a_secondary" {
  domain = digitalocean_domain.financialdata_digital.name
  type   = "A"
  name   = "@"
  value  = local.app_ipv4_secondary
  ttl    = 300
}

resource "digitalocean_record" "financialdata_digital_www" {
  domain = digitalocean_domain.financialdata_digital.name
  type   = "A"
  name   = "www"
  value  = local.app_ipv4_primary
  ttl    = 300
}

resource "digitalocean_record" "financialdata_digital_www_secondary" {
  domain = digitalocean_domain.financialdata_digital.name
  type   = "A"
  name   = "www"
  value  = local.app_ipv4_secondary
  ttl    = 300
}

# AAAA Records for financialdata.digital (IPv6)
resource "digitalocean_record" "financialdata_digital_aaaa" {
  domain = digitalocean_domain.financialdata_digital.name
  type   = "AAAA"
  name   = "@"
  value  = local.app_ipv6_primary
  ttl    = 300
}

resource "digitalocean_record" "financialdata_digital_aaaa_secondary" {
  domain = digitalocean_domain.financialdata_digital.name
  type   = "AAAA"
  name   = "@"
  value  = local.app_ipv6_secondary
  ttl    = 300
}

resource "digitalocean_record" "financialdata_digital_www_aaaa" {
  domain = digitalocean_domain.financialdata_digital.name
  type   = "AAAA"
  name   = "www"
  value  = local.app_ipv6_primary
  ttl    = 300
}

resource "digitalocean_record" "financialdata_digital_www_aaaa_secondary" {
  domain = digitalocean_domain.financialdata_digital.name
  type   = "AAAA"
  name   = "www"
  value  = local.app_ipv6_secondary
  ttl    = 300
}

# ===== dadosfinanceiros.com =====
resource "digitalocean_domain" "dadosfinanceiros_com" {
  name       = "dadosfinanceiros.com"
  ip_address = local.app_ipv4_primary
}

# A Records for dadosfinanceiros.com
resource "digitalocean_record" "financialdata_online_a_secondary" {
  domain = digitalocean_domain.dadosfinanceiros_com.name
  type   = "A"
  name   = "@"
  value  = local.app_ipv4_secondary
  ttl    = 300
}

resource "digitalocean_record" "financialdata_online_www" {
  domain = digitalocean_domain.dadosfinanceiros_com.name
  type   = "A"
  name   = "www"
  value  = local.app_ipv4_primary
  ttl    = 300
}

resource "digitalocean_record" "financialdata_online_www_secondary" {
  domain = digitalocean_domain.dadosfinanceiros_com.name
  type   = "A"
  name   = "www"
  value  = local.app_ipv4_secondary
  ttl    = 300
}

# AAAA Records for dadosfinanceiros.com (IPv6)
resource "digitalocean_record" "financialdata_online_aaaa" {
  domain = digitalocean_domain.dadosfinanceiros_com.name
  type   = "AAAA"
  name   = "@"
  value  = local.app_ipv6_primary
  ttl    = 300
}

resource "digitalocean_record" "financialdata_online_aaaa_secondary" {
  domain = digitalocean_domain.dadosfinanceiros_com.name
  type   = "AAAA"
  name   = "@"
  value  = local.app_ipv6_secondary
  ttl    = 300
}

resource "digitalocean_record" "financialdata_online_www_aaaa" {
  domain = digitalocean_domain.dadosfinanceiros_com.name
  type   = "AAAA"
  name   = "www"
  value  = local.app_ipv6_primary
  ttl    = 300
}

resource "digitalocean_record" "financialdata_online_www_aaaa_secondary" {
  domain = digitalocean_domain.dadosfinanceiros_com.name
  type   = "AAAA"
  name   = "www"
  value  = local.app_ipv6_secondary
  ttl    = 300
}

# ===== financialdata.online =====
resource "digitalocean_domain" "dadosfinanceiros_com" {
  name       = "financialdata.online"
  ip_address = local.app_ipv4_primary
}

# A Records for financialdata.online
resource "digitalocean_record" "financialdata_online_a_secondary" {
  domain = digitalocean_domain.dadosfinanceiros_com.name
  type   = "A"
  name   = "@"
  value  = local.app_ipv4_secondary
  ttl    = 300
}

resource "digitalocean_record" "financialdata_online_www" {
  domain = digitalocean_domain.dadosfinanceiros_com.name
  type   = "A"
  name   = "www"
  value  = local.app_ipv4_primary
  ttl    = 300
}

resource "digitalocean_record" "financialdata_online_www_secondary" {
  domain = digitalocean_domain.dadosfinanceiros_com.name
  type   = "A"
  name   = "www"
  value  = local.app_ipv4_secondary
  ttl    = 300
}

# AAAA Records for financialdata.online (IPv6)
resource "digitalocean_record" "financialdata_online_aaaa" {
  domain = digitalocean_domain.dadosfinanceiros_com.name
  type   = "AAAA"
  name   = "@"
  value  = local.app_ipv6_primary
  ttl    = 300
}

resource "digitalocean_record" "financialdata_online_aaaa_secondary" {
  domain = digitalocean_domain.dadosfinanceiros_com.name
  type   = "AAAA"
  name   = "@"
  value  = local.app_ipv6_secondary
  ttl    = 300
}

resource "digitalocean_record" "financialdata_online_www_aaaa" {
  domain = digitalocean_domain.dadosfinanceiros_com.name
  type   = "AAAA"
  name   = "www"
  value  = local.app_ipv6_primary
  ttl    = 300
}

resource "digitalocean_record" "financialdata_online_www_aaaa_secondary" {
  domain = digitalocean_domain.dadosfinanceiros_com.name
  type   = "AAAA"
  name   = "www"
  value  = local.app_ipv6_secondary
  ttl    = 300
}

# Output the detected IPs for verification
output "detected_ips" {
  value = {
    method_used    = local.detection_method
    ipv4_primary   = local.app_ipv4_primary
    ipv4_secondary = local.app_ipv4_secondary
    ipv6_primary   = local.app_ipv6_primary
    ipv6_secondary = local.app_ipv6_secondary
    source_domain  = local.source_domain
  }
  description = "Detected IP addresses for App Platform"
} 