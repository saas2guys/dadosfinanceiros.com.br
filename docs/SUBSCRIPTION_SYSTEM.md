# Subscription System Documentation

## Overview

This document describes the comprehensive subscription system implemented for the Polygon.io Proxy API. The system provides flexible plan management, Stripe payment integration, and usage-based access control.

## Architecture

### Models

#### Plan Model
- **Purpose**: Stores subscription plan configurations
- **Key Fields**:
  - `name`: Plan name (e.g., "Free", "Basic", "Premium")
  - `slug`: URL-friendly identifier
  - `daily_request_limit`: Maximum API requests per day
  - `price_monthly`: Monthly price in USD
  - `stripe_price_id`: Stripe price ID for payment processing
  - `features`: JSON field for additional plan features
  - `is_active`: Whether the plan is available for selection

#### User Model Updates
- **New Fields**:
  - `current_plan`: ForeignKey to Plan model
  - `subscription_status`: Current subscription state
  - `stripe_customer_id`: Stripe customer identifier
  - `stripe_subscription_id`: Stripe subscription identifier
  - `subscription_started_at`: When subscription began
  - `subscription_expires_at`: When subscription expires

### Default Plans

The system includes four default plans:

1. **Free Plan**
   - 100 requests/day
   - $0.00/month
   - Community support

2. **Basic Plan**
   - 1,000 requests/day
   - $9.99/month
   - Email support

3. **Premium Plan**
   - 10,000 requests/day
   - $29.99/month
   - Priority support

4. **Enterprise Plan**
   - 100,000 requests/day
   - $99.99/month
   - Dedicated support

## Features

### 1. Plan Management
- Database-driven plan configuration
- Easy plan updates without code deployment
- Feature-rich plan descriptions
- Active/inactive plan control

### 2. Stripe Integration
- Secure payment processing
- Subscription lifecycle management
- Webhook handling for real-time updates
- Customer portal integration

### 3. Usage Validation
- Real-time request limit checking
- Subscription status validation
- Automatic access control
- Usage tracking and reporting

### 4. User Experience
- Beautiful plan selection interface
- Subscription management dashboard
- Usage monitoring and alerts
- Easy upgrade/downgrade process

## API Endpoints

### Plan Management
- `GET /api/plans/` - List all available plans
- `GET /api/subscription/` - Get user's subscription details

### Subscription Management
- `POST /api/create-checkout-session/` - Create Stripe checkout session
- `POST /stripe/webhook/` - Handle Stripe webhooks

### Web Interface
- `/plans/` - Plan selection page
- `/subscription/success/` - Payment success page
- `/profile/` - User dashboard with subscription info

## Configuration

### Environment Variables

Add these to your environment:

```bash
# Stripe Configuration
STRIPE_PUBLISHABLE_KEY=pk_test_...
STRIPE_SECRET_KEY=sk_test_...
STRIPE_WEBHOOK_SECRET=whsec_...
STRIPE_LIVE_MODE=False
```

### Stripe Setup

1. **Create Products and Prices in Stripe Dashboard**:
   - Create products for Basic, Premium, and Enterprise plans
   - Set up recurring monthly prices
   - Copy the price IDs

2. **Update Plan Models**:
   ```python
   # Update the stripe_price_id for each plan
   basic_plan = Plan.objects.get(slug='basic')
   basic_plan.stripe_price_id = 'price_1234567890'
   basic_plan.save()
   ```

3. **Configure Webhooks**:
   - Add webhook endpoint: `https://yourdomain.com/stripe/webhook/`
   - Select events: `checkout.session.completed`, `customer.subscription.updated`, `customer.subscription.deleted`

## Usage Examples

### Check User Subscription Status

```python
from users.models import User

user = User.objects.get(email='user@example.com')

# Check if user can make a request
can_request, message = user.can_make_request()
if not can_request:
    print(f"Access denied: {message}")

# Get subscription details
print(f"Plan: {user.current_plan.name}")
print(f"Daily limit: {user.daily_request_limit}")
print(f"Requests made: {user.daily_requests_made}")
print(f"Status: {user.subscription_status}")
```

### Upgrade User Plan

```python
from users.models import User, Plan

user = User.objects.get(email='user@example.com')
premium_plan = Plan.objects.get(slug='premium')

# Upgrade user to premium plan
user.upgrade_to_plan(premium_plan)
print(f"Upgraded to {user.current_plan.name}")
```

### Create Custom Plan

```python
from users.models import Plan
from decimal import Decimal

custom_plan = Plan.objects.create(
    name='Custom Enterprise',
    slug='custom-enterprise',
    daily_request_limit=500000,
    price_monthly=Decimal('199.99'),
    features={
        'support': 'Dedicated Account Manager',
        'api_access': 'Enterprise Plus',
        'rate_limit': '500,000 requests/day',
        'custom_integrations': True,
        'sla': '99.9% uptime guarantee'
    },
    is_active=True
)
```

## Permission System

The system uses `DailyLimitPermission` to control API access:

```python
class DailyLimitPermission(BasePermission):
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return True
            
        can_request, message = request.user.can_make_request()
        if not can_request:
            request._permission_error = message
            return False
            
        # Increment usage counter
        request.user.daily_requests_made += 1
        request.user.save()
        return True
```

## Stripe Service Functions

### Key Methods

- `create_customer(user)` - Create Stripe customer
- `create_checkout_session(user, plan, success_url, cancel_url)` - Create payment session
- `handle_successful_payment(session)` - Process successful payment
- `cancel_subscription(subscription_id)` - Cancel subscription
- `reactivate_subscription(subscription_id)` - Reactivate subscription

## Frontend Integration

### Plan Selection

The plans page displays all available plans with:
- Plan features and pricing
- Current plan highlighting
- Upgrade/downgrade buttons
- Subscription management options

### User Dashboard

The profile page shows:
- Current subscription details
- Usage statistics with progress bars
- Plan features
- Subscription management actions

## Security Considerations

1. **Webhook Verification**: All Stripe webhooks are verified using the webhook secret
2. **CSRF Protection**: All forms include CSRF tokens
3. **Authentication**: Subscription management requires user authentication
4. **Input Validation**: All user inputs are validated and sanitized

## Testing

### Unit Tests

The system includes comprehensive tests for:
- Plan creation and management
- User subscription lifecycle
- Usage validation and limits
- Stripe integration (mocked)
- Permission system

### Manual Testing

1. **Plan Selection**: Visit `/plans/` to test plan selection
2. **Payment Flow**: Test Stripe checkout integration
3. **Usage Limits**: Test API access with different plans
4. **Subscription Management**: Test cancel/reactivate functionality

## Monitoring and Analytics

### Key Metrics to Track

1. **Subscription Metrics**:
   - New subscriptions per day/month
   - Churn rate
   - Revenue per plan
   - Upgrade/downgrade patterns

2. **Usage Metrics**:
   - API requests per plan
   - Usage patterns by time
   - Limit violations
   - User engagement

3. **Performance Metrics**:
   - Payment success rate
   - Webhook processing time
   - API response times
   - Error rates

## Troubleshooting

### Common Issues

1. **Webhook Failures**:
   - Check webhook secret configuration
   - Verify endpoint accessibility
   - Review Stripe dashboard for failed events

2. **Payment Issues**:
   - Verify Stripe keys are correct
   - Check plan price IDs match Stripe
   - Ensure webhook events are configured

3. **Usage Limit Issues**:
   - Check user's current plan
   - Verify subscription status
   - Review daily request counter reset

### Debug Commands

```bash
# Check user subscription status
python manage.py shell -c "
from users.models import User
user = User.objects.get(email='user@example.com')
print(f'Plan: {user.current_plan}')
print(f'Status: {user.subscription_status}')
print(f'Requests: {user.daily_requests_made}/{user.daily_request_limit}')
"

# Reset daily request counters
python manage.py shell -c "
from users.models import User
User.objects.all().update(daily_requests_made=0)
print('Reset all daily request counters')
"
```

## Future Enhancements

1. **Analytics Dashboard**: Admin interface for subscription analytics
2. **Usage Alerts**: Email notifications for usage limits
3. **Plan Recommendations**: AI-powered plan suggestions
4. **API Rate Limiting**: More sophisticated rate limiting
5. **Multi-currency Support**: Support for different currencies
6. **Team Plans**: Support for organization subscriptions
7. **Usage-based Billing**: Pay-per-request pricing models

## Support

For technical support or questions about the subscription system:
- Email: support@dadosfinanceiros.com.br
- Documentation: This file and inline code comments
- Stripe Documentation: https://stripe.com/docs 