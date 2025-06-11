# Production Deployment Guide for financialdata.online

This guide provides step-by-step instructions for deploying your Django application to production with proper CSRF token support and security configurations.

## CSRF Token Issues - Solutions Implemented

### 1. Domain Configuration
- **Fixed**: `ALLOWED_HOSTS` now properly configured for your domain
- **Fixed**: `CSRF_TRUSTED_ORIGINS` configured for HTTPS domains
- **Fixed**: `CSRF_COOKIE_DOMAIN` set to `.financialdata.online`

### 2. Security Settings
The following security settings have been configured for production:

```python
# HTTPS and Cookie Security
SECURE_SSL_REDIRECT = True
CSRF_COOKIE_SECURE = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_HTTPONLY = True
SESSION_COOKIE_HTTPONLY = True

# HSTS Configuration
SECURE_HSTS_SECONDS = 31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True
```

### 3. CORS Configuration
CORS settings have been updated to work properly with your domain:

```python
CORS_ALLOWED_ORIGINS = [
    'https://financialdata.online',
    'https://www.financialdata.online',
    'https://api.financialdata.online',
]
```

## Pre-deployment Requirements

1. **Server Setup**
   - Ubuntu 20.04+ or similar Linux distribution
   - Python 3.8+
   - PostgreSQL or MySQL database
   - Nginx web server
   - SSL certificate for your domain

2. **Environment Variables**
   Create these environment variables on your server:

   ```bash
   export DEBUG=False
   export ENV=production
   export SECRET_KEY="your-super-secret-production-key-here"
   export DATABASE_URL="postgresql://username:password@localhost:5432/financialdata"
   export REDIS_URL="redis://localhost:6379"
   ```

## Step-by-Step Deployment

### 1. Clone and Setup Project

```bash
# Clone your repository
git clone https://github.com/yourusername/proxy_project.git
cd proxy_project

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Database Setup

```bash
# Create PostgreSQL database
sudo -u postgres psql
CREATE DATABASE dadosfinanceiros;
CREATE USER dbuser WITH PASSWORD 'your_password';
GRANT ALL PRIVILEGES ON DATABASE dadosfinanceiros TO dbuser;
\q

# Run migrations
python manage.py migrate
python manage.py collectstatic --noinput
```

### 3. Create Superuser

```bash
python manage.py createsuperuser
```

### 4. Configure Nginx

```bash
# Copy the sample nginx configuration
sudo cp nginx.conf.sample /etc/nginx/sites-available/financialdata.online

# Update the configuration with your actual paths
sudo nano /etc/nginx/sites-available/financialdata.online

# Enable the site
sudo ln -s /etc/nginx/sites-available/financialdata.online /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

### 5. SSL Certificate Setup

Using Certbot (Let's Encrypt):

```bash
# Install Certbot
sudo apt install certbot python3-certbot-nginx

# Obtain SSL certificate
sudo certbot --nginx -d financialdata.online -d www.financialdata.online

# Test auto-renewal
sudo certbot renew --dry-run
```

### 6. Create Systemd Service

Create `/etc/systemd/system/financialdata.service`:

```ini
[Unit]
Description=Dados Financeiros Django Application
After=network.target

[Service]
Type=exec
User=www-data
Group=www-data
WorkingDirectory=/path/to/your/project
Environment=PATH=/path/to/your/project/venv/bin
Environment=DEBUG=False
Environment=SECRET_KEY=your-secret-key
Environment=DATABASE_URL=postgresql://username:password@localhost:5432/dadosfinanceiros
ExecStart=/path/to/your/project/venv/bin/gunicorn proxy_project.wsgi:application --bind 127.0.0.1:8000 --workers 3
Restart=always

[Install]
WantedBy=multi-user.target
```

```bash
# Enable and start the service
sudo systemctl daemon-reload
sudo systemctl enable dadosfinanceiros
sudo systemctl start dadosfinanceiros
sudo systemctl status dadosfinanceiros
```

## Testing CSRF Protection

### 1. Test Frontend Forms

Visit your site and test the following:
- User registration: `https://financialdata.online/register/`
- User login: `https://financialdata.online/login/`
- Language selector in navigation
- Token regeneration in user profile

### 2. Test API Endpoints

```bash
# Test that CSRF is working for API endpoints that require it
curl -X POST https://financialdata.online/api/register/ \
     -H "Content-Type: application/json" \
     -H "X-CSRFToken: your-csrf-token" \
     -d '{"email": "test@example.com", "password": "testpass123"}'
```

## Troubleshooting CSRF Issues

### Common Issues and Solutions

1. **"CSRF token missing or incorrect"**
   - Ensure all forms include `{% csrf_token %}`
   - Check that CSRF_TRUSTED_ORIGINS includes your domain
   - Verify cookies are being set with the correct domain

2. **"CSRF verification failed. Request aborted."**
   - Check that `CSRF_COOKIE_SECURE = True` matches your HTTPS setup
   - Ensure your domain is in CSRF_TRUSTED_ORIGINS
   - Verify that cookies are not being blocked by browser

3. **Cross-origin requests failing**
   - Update CORS_ALLOWED_ORIGINS with your domain
   - Ensure X-CSRFToken header is included in CORS_ALLOW_HEADERS

### Debug CSRF Issues

Add this to your settings temporarily to debug:

```python
# Add to settings.py for debugging (remove in production)
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
        },
    },
    'loggers': {
        'django.middleware.csrf': {
            'handlers': ['console'],
            'level': 'DEBUG',
        },
    },
}
```

## Performance and Security Checklist

- [ ] SSL certificate installed and working
- [ ] HTTPS redirect configured
- [ ] HSTS headers enabled
- [ ] CSRF protection working on all forms
- [ ] CORS properly configured
- [ ] Static files served efficiently
- [ ] Database properly secured
- [ ] Environment variables set correctly
- [ ] Regular backups configured
- [ ] Monitoring and logging set up

## Monitoring

Monitor these endpoints:
- `https://financialdata.online/health/` - Application health
- `https://financialdata.online/admin/` - Django admin (ensure login works)
- API endpoints with proper token authentication

## Support

If you encounter CSRF token issues after following this guide:

1. Check the browser developer tools for any CSRF-related errors
2. Verify environment variables are set correctly
3. Check Django logs for CSRF middleware messages
4. Ensure your domain DNS is properly configured

The configurations implemented should resolve common CSRF token problems in production environments. 