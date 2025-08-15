# Stripe Integration Guide

This project integrates **Stripe** for subscription management, payments, and plan upgrades.  
It uses the Stripe Checkout flow and listens to **webhooks** to keep the user's subscription status in sync.

---

## Prerequisites

1. **Stripe account** – Create one at [https://dashboard.stripe.com/register](https://dashboard.stripe.com/register)
2. **Stripe API keys** – Available in the [Stripe Dashboard → Developers → API keys](https://dashboard.stripe.com/apikeys)
3. **Stripe CLI** – For local webhook testing:  
   [Install here](https://stripe.com/docs/stripe-cli)

---

## Environment Variables

Add the following to your `.env` file:

```env
# Stripe API
STRIPE_SECRET_KEY=sk_test_...
STRIPE_WEBHOOK_SECRET=whsec_...
```

## Running Locally
1. **Start your Django server**
```bash
python manage.py runserver
```
2. **Forward Stripe events locally** - In another terminal, run:
```bash
stripe listen --forward-to 127.0.0.1:8000/stripe/webhook/
```
This will:
Listen for events from Stripe
Forward them to your local webhook endpoint (/stripe/webhook/)
Print event logs in your terminal

## Linking Stripe Plans to Django Model
Our Plan model in Django contains fields to store Stripe IDs for both products and prices:
```python
class Plan(models.Model):
    ...
    stripe_plan_id = models.CharField(max_length=255, blank=True, null=True)  # Product ID from Stripe
    stripe_price_id = models.CharField(max_length=255, blank=True, null=True)  # Monthly price ID
    stripe_yearly_price_id = models.CharField(max_length=255, blank=True, null=True)  # Yearly price ID
    ...
```
1. **Create Products in Stripe** -Go to Stripe Dashboard → Products and create one product per plan you offer.
Example product IDs from Stripe:
```
prod_abcdeFgHiJKlmN
```
2. **Create Prices for Each Product**
- Monthly billing price
- Yearly billing price
3. **Copy the IDs from Stripe**
```
stripe_plan_id → The product ID from Stripe (e.g., prod_abcdeFgHiJKlmN)
stripe_price_id → The monthly price ID (e.g., price_123...)
stripe_yearly_price_id → The yearly price ID (e.g., price_456...)
```