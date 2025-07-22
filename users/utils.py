from django.core.cache import caches
from django.utils import timezone

def set_payment_failure_flags(user):
    """Set payment failure restrictions for a user"""
    user.payment_failed_at = timezone.now()
    user.payment_restrictions_applied = True
    user.save(update_fields=[
        'payment_failed_at',
        'payment_restrictions_applied',
    ])
    # Clear cached limits to force recalculation
    cache = caches['rate_limit']
    cache_key = f"user_limits:{user.id}"
    cache.delete(cache_key)

def clear_payment_failure_flags(user):
    """Clear payment failure restrictions for a user"""
    user.payment_restrictions_applied = False
    user.save(update_fields=[
        'payment_restrictions_applied',
    ])
    # Clear cached limits
    cache = caches['rate_limit']
    cache_key = f"user_limits:{user.id}"
    cache.delete(cache_key)
