variable "do_token" {
  description = "DigitalOcean API token"
  type        = string
  sensitive   = true
}

variable "app_domain" {
  description = "Your App Platform domain (e.g., financialdata-online-vsxtw.ondigitalocean.app)"
  type        = string
  default     = ""
} 