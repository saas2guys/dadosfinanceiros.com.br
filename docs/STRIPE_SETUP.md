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

# App URLs
STRIPE_SUCCESS_URL=http://localhost:8080/payment/success/
STRIPE_CANCEL_URL=http://localhost:8080/payment/cancel/
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