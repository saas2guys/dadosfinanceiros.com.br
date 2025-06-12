# CSRF Debugging Guide for financialdata.online

## Recent Fixes Applied

### 1. Cookie Domain Configuration
Fixed the CSRF and session cookie domains to remove the leading dot:

```python
# Before (problematic)
CSRF_COOKIE_DOMAIN = ".financialdata.online"
SESSION_COOKIE_DOMAIN = ".financialdata.online"

# After (fixed)
CSRF_COOKIE_DOMAIN = "financialdata.online"
SESSION_COOKIE_DOMAIN = "financialdata.online"
```

### 2. CSRF Security Settings
Added proper CSRF security configuration:

```python
CSRF_COOKIE_SECURE = not DEBUG  # True in production
CSRF_COOKIE_HTTPONLY = False    # Allows JavaScript access when needed
```

### 3. Login Template Fixes
- Updated login template to use proper Django form structure
- Added proper error handling for CSRF validation failures
- Fixed Portuguese translations and modern UI design

### 4. Password Reset URLs
Added missing password reset URLs that were referenced in templates:

```python
path("password_reset/", auth_views.PasswordResetView.as_view(...), name="password_reset"),
path("password_reset/done/", auth_views.PasswordResetDoneView.as_view(...), name="password_reset_done"),
path("reset/<uidb64>/<token>/", auth_views.PasswordResetConfirmView.as_view(...), name="password_reset_confirm"),
path("reset/done/", auth_views.PasswordResetCompleteView.as_view(...), name="password_reset_complete"),
```

## How to Test CSRF Fix

### 1. Clear Browser Data
First, clear all cookies and site data for financialdata.online to ensure fresh state.

### 2. Test Login Process
1. Visit https://financialdata.online/login/
2. Open browser developer tools (F12)
3. Check the "Application" or "Storage" tab for cookies
4. Look for `csrftoken` cookie with domain `financialdata.online`

### 3. Browser Console Debugging
Add this to browser console to check CSRF token:

```javascript
// Check if CSRF token exists
document.querySelector('[name=csrfmiddlewaretoken]')?.value

// Check cookies
document.cookie.split(';').find(c => c.trim().startsWith('csrftoken='))
```

### 4. Check Network Tab
1. Open Network tab in developer tools
2. Submit login form
3. Look for the POST request to `/login/`
4. Check if `csrfmiddlewaretoken` is included in form data
5. Check response for any CSRF-related error messages

## Common CSRF Issues and Solutions

### Issue 1: "CSRF token missing or incorrect"
**Cause**: Cookie domain mismatch or missing token
**Solution**: 
- Clear browser cache/cookies
- Check CSRF_COOKIE_DOMAIN setting
- Verify `{% csrf_token %}` is in form

### Issue 2: "CSRF verification failed"
**Cause**: Cookie security settings mismatch
**Solution**:
- Ensure CSRF_COOKIE_SECURE matches HTTPS usage
- Check that cookies aren't blocked by browser

### Issue 3: Form submission returns 403
**Cause**: CSRF middleware rejecting request
**Solution**:
- Check CSRF_TRUSTED_ORIGINS includes your domain
- Verify middleware order in settings

## Production Deployment Steps

1. **Deploy the updated code** with the fixed settings
2. **Restart the Django application** to apply new settings
3. **Clear any cached static files** if using CDN
4. **Test immediately** after deployment

## Manual Testing Checklist

- [ ] Visit login page and verify it loads without errors
- [ ] Check that CSRF token cookie is set with correct domain
- [ ] Submit login form with valid credentials
- [ ] Verify successful login redirects to profile/home
- [ ] Test password reset link works
- [ ] Check registration form also works (already fixed)

## Emergency Rollback

If CSRF issues persist, temporarily add this to settings for debugging:

```python
# TEMPORARY DEBUG ONLY - Remove in production
CSRF_FAILURE_VIEW = 'django.views.csrf.csrf_failure'
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

This will provide detailed CSRF debugging information in the logs.

## Contact Support

If issues persist after following this guide:
1. Check Django application logs for CSRF-related errors
2. Verify DNS and SSL certificate are working correctly
3. Ensure environment variables are set properly in production
4. Test from different browsers/devices to isolate client-side issues 