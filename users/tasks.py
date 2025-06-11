"""
Background tasks for rate limiting, usage tracking, and billing.
These tasks maintain database performance and provide usage analytics.
"""
import logging
import stripe
from datetime import datetime, timedelta
from django.core.cache import caches
from django.core.management import call_command
from django.db import transaction
from django.db.models import Count, Avg, Q, Sum
from django.utils import timezone
from django.conf import settings

from .models import (
    RateLimitCounter, APIUsage, UsageSummary, User, 
    PaymentFailure, SubscriptionStatus
)

logger = logging.getLogger(__name__)

# Set up Stripe
stripe.api_key = settings.STRIPE_SECRET_KEY


def cleanup_rate_limit_counters():
    """Remove old rate limit counters to prevent database bloat"""
    try:
        cutoff_time = timezone.now() - timedelta(days=7)
        
        deleted_count = RateLimitCounter.objects.filter(
            window_start__lt=cutoff_time
        ).delete()[0]
        
        logger.info(f"Cleaned up {deleted_count} old rate limit counters")
        
        # Also clean Django's cache table if using database cache
        cache = caches['rate_limit']
        if hasattr(cache, '_cache') and hasattr(cache._cache, 'clear'):
            cache.clear()
        
        return deleted_count
        
    except Exception as e:
        logger.error(f"Error cleaning up rate limit counters: {e}")
        return 0


def cleanup_api_usage_data():
    """Clean up old API usage data based on retention policy"""
    try:
        # Keep detailed usage data for 90 days
        cutoff_date = timezone.now().date() - timedelta(days=90)
        
        deleted_usage = APIUsage.objects.filter(date__lt=cutoff_date).delete()[0]
        
        # Keep usage summaries for 1 year
        summary_cutoff = timezone.now().date() - timedelta(days=365)
        deleted_summaries = UsageSummary.objects.filter(date__lt=summary_cutoff).delete()[0]
        
        logger.info(f"Cleaned up {deleted_usage} usage records and {deleted_summaries} summary records")
        
        return deleted_usage + deleted_summaries
        
    except Exception as e:
        logger.error(f"Error cleaning up usage data: {e}")
        return 0


def update_hourly_usage_summaries():
    """Create hourly usage summaries for fast dashboard queries"""
    try:
        now = timezone.now()
        last_hour = now.replace(minute=0, second=0, microsecond=0) - timedelta(hours=1)
        
        # Process hourly aggregation
        hourly_usage = APIUsage.objects.filter(
            timestamp__gte=last_hour,
            timestamp__lt=last_hour + timedelta(hours=1)
        ).values('user', 'ip_address', 'date').annotate(
            total_requests=Count('id'),
            successful_requests=Count('id', filter=Q(response_status__lt=400)),
            failed_requests=Count('id', filter=Q(response_status__gte=400)),
            avg_response_time=Avg('response_time_ms')
        )
        
        summary_count = 0
        for usage in hourly_usage:
            summary, created = UsageSummary.objects.update_or_create(
                user_id=usage['user'] if usage['user'] else None,
                ip_address=usage['ip_address'] if not usage['user'] else None,
                date=usage['date'],
                hour=last_hour.hour,
                defaults={
                    'total_requests': usage['total_requests'],
                    'successful_requests': usage['successful_requests'],
                    'failed_requests': usage['failed_requests'],
                    'avg_response_time': usage['avg_response_time'] or 0
                }
            )
            summary_count += 1
        
        logger.info(f"Updated {summary_count} hourly usage summaries for {last_hour}")
        return summary_count
        
    except Exception as e:
        logger.error(f"Error updating hourly summaries: {e}")
        return 0


def update_daily_usage_summaries():
    """Create daily usage summaries for billing and analytics"""
    try:
        yesterday = timezone.now().date() - timedelta(days=1)
        
        # Aggregate daily usage from hourly summaries (more efficient)
        daily_usage = UsageSummary.objects.filter(
            date=yesterday,
            hour__isnull=False  # Only hourly summaries
        ).values('user', 'ip_address', 'date').annotate(
            total_requests=Sum('total_requests'),
            successful_requests=Sum('successful_requests'),
            failed_requests=Sum('failed_requests'),
            avg_response_time=Avg('avg_response_time')
        )
        
        summary_count = 0
        for usage in daily_usage:
            summary, created = UsageSummary.objects.update_or_create(
                user_id=usage['user'] if usage['user'] else None,
                ip_address=usage['ip_address'] if not usage['user'] else None,
                date=usage['date'],
                hour=None,  # Daily summary
                defaults={
                    'total_requests': usage['total_requests'],
                    'successful_requests': usage['successful_requests'],
                    'failed_requests': usage['failed_requests'],
                    'avg_response_time': usage['avg_response_time'] or 0
                }
            )
            summary_count += 1
        
        logger.info(f"Updated {summary_count} daily usage summaries for {yesterday}")
        return summary_count
        
    except Exception as e:
        logger.error(f"Error updating daily summaries: {e}")
        return 0


def process_usage_billing():
    """Process usage-based billing for metered subscriptions"""
    try:
        yesterday = timezone.now().date() - timedelta(days=1)
        
        # Get users with metered subscriptions
        metered_users = User.objects.filter(
            subscription_status__in=[SubscriptionStatus.ACTIVE, SubscriptionStatus.TRIALING],
            current_plan__is_metered=True,
            stripe_subscription_id__isnull=False
        ).select_related('current_plan')
        
        processed_count = 0
        
        for user in metered_users:
            try:
                # Get daily usage summary
                try:
                    usage_summary = UsageSummary.objects.get(
                        user=user,
                        date=yesterday,
                        hour=None  # Daily summary
                    )
                    total_calls = usage_summary.total_requests
                except UsageSummary.DoesNotExist:
                    # Fallback to raw usage data
                    total_calls = APIUsage.objects.filter(
                        user=user,
                        date=yesterday
                    ).count()
                
                if total_calls > 0:
                    # Report to Stripe for metered billing
                    if user.stripe_subscription_id:
                        # Get the subscription and find the metered item
                        subscription = stripe.Subscription.retrieve(user.stripe_subscription_id)
                        
                        for item in subscription['items']['data']:
                            price = item['price']
                            if price.get('billing_scheme') == 'per_unit':
                                # This is a metered item
                                stripe.SubscriptionItem.create_usage_record(
                                    item['id'],
                                    quantity=total_calls,
                                    timestamp=int(yesterday.strftime('%s')),
                                    action='set'  # Use 'set' to replace, 'increment' to add
                                )
                                logger.info(f"Reported {total_calls} usage for user {user.id} to Stripe")
                                break
                
                processed_count += 1
                
            except stripe.error.StripeError as e:
                logger.error(f"Stripe error for user {user.id}: {e}")
            except Exception as e:
                logger.error(f"Error processing billing for user {user.id}: {e}")
        
        logger.info(f"Processed usage billing for {processed_count} metered users")
        return processed_count
        
    except Exception as e:
        logger.error(f"Error in process_usage_billing: {e}")
        return 0


def refresh_user_limits_cache():
    """Refresh cached limits for all active users"""
    try:
        active_users = User.objects.filter(
            subscription_status__in=[SubscriptionStatus.ACTIVE, SubscriptionStatus.TRIALING]
        ).select_related('current_plan')
        
        refreshed_count = 0
        
        for user in active_users:
            try:
                user.refresh_limits_cache()
                refreshed_count += 1
            except Exception as e:
                logger.error(f"Error refreshing limits for user {user.id}: {e}")
        
        logger.info(f"Refreshed limits cache for {refreshed_count} users")
        return refreshed_count
        
    except Exception as e:
        logger.error(f"Error refreshing user limits cache: {e}")
        return 0


def cleanup_payment_failures():
    """Clean up old payment failure records"""
    try:
        # Remove payment failure records older than 30 days
        cutoff_date = timezone.now() - timedelta(days=30)
        
        deleted_count = PaymentFailure.objects.filter(
            failed_at__lt=cutoff_date,
            restrictions_applied=False
        ).delete()[0]
        
        logger.info(f"Cleaned up {deleted_count} old payment failure records")
        return deleted_count
        
    except Exception as e:
        logger.error(f"Error cleaning up payment failures: {e}")
        return 0


def generate_usage_analytics_report():
    """Generate analytics report for the previous day"""
    try:
        yesterday = timezone.now().date() - timedelta(days=1)
        
        # Get overall statistics
        total_requests = APIUsage.objects.filter(date=yesterday).count()
        unique_users = APIUsage.objects.filter(date=yesterday).values('user').distinct().count()
        unique_ips = APIUsage.objects.filter(date=yesterday, user__isnull=True).values('ip_address').distinct().count()
        
        # Get top endpoints
        top_endpoints = APIUsage.objects.filter(date=yesterday).values('endpoint').annotate(
            request_count=Count('id')
        ).order_by('-request_count')[:10]
        
        # Get error rate
        error_count = APIUsage.objects.filter(date=yesterday, response_status__gte=400).count()
        error_rate = (error_count / total_requests * 100) if total_requests > 0 else 0
        
        # Calculate average response time
        avg_response_time = APIUsage.objects.filter(date=yesterday).aggregate(
            avg_time=Avg('response_time_ms')
        )['avg_time'] or 0
        
        report = {
            'date': yesterday.isoformat(),
            'total_requests': total_requests,
            'unique_users': unique_users,
            'unique_ips': unique_ips,
            'error_rate': round(error_rate, 2),
            'avg_response_time_ms': round(avg_response_time, 2),
            'top_endpoints': list(top_endpoints),
        }
        
        logger.info(f"Generated usage analytics report for {yesterday}: {report}")
        return report
        
    except Exception as e:
        logger.error(f"Error generating analytics report: {e}")
        return {}


def cleanup_expired_tokens():
    """Clean up expired user tokens"""
    try:
        from .models import TokenHistory
        
        # Clean up expired token history (keep for 90 days)
        cutoff_date = timezone.now() - timedelta(days=90)
        deleted_count = TokenHistory.objects.filter(
            created_at__lt=cutoff_date,
            is_active=False
        ).delete()[0]
        
        logger.info(f"Cleaned up {deleted_count} expired token records")
        return deleted_count
        
    except Exception as e:
        logger.error(f"Error cleaning up expired tokens: {e}")
        return 0


def monitor_subscription_health():
    """Monitor subscription health and identify issues"""
    try:
        # Check for subscriptions ending soon
        ending_soon = User.objects.filter(
            subscription_expires_at__lte=timezone.now() + timedelta(days=7),
            subscription_status=SubscriptionStatus.ACTIVE
        ).count()
        
        # Check for payment failures
        payment_failures = PaymentFailure.objects.filter(
            restrictions_applied=True,
            failed_at__gte=timezone.now() - timedelta(days=7)
        ).count()
        
        # Check for high usage users (over 80% of their daily limit)
        high_usage_users = User.objects.filter(
            subscription_status__in=[SubscriptionStatus.ACTIVE, SubscriptionStatus.TRIALING]
        ).extra(
            where=["daily_requests_made > (cached_daily_limit * 0.8)"]
        ).count()
        
        health_report = {
            'subscriptions_ending_soon': ending_soon,
            'recent_payment_failures': payment_failures,
            'high_usage_users': high_usage_users,
            'timestamp': timezone.now().isoformat()
        }
        
        logger.info(f"Subscription health report: {health_report}")
        
        # Alert if there are issues
        if ending_soon > 10 or payment_failures > 5:
            logger.warning(f"Subscription health alert: {health_report}")
        
        return health_report
        
    except Exception as e:
        logger.error(f"Error monitoring subscription health: {e}")
        return {}


# Main task runner functions (to be called by cron or task scheduler)
def run_hourly_tasks():
    """Run all hourly maintenance tasks"""
    logger.info("Starting hourly tasks")
    
    results = {
        'cleanup_counters': cleanup_rate_limit_counters(),
        'update_summaries': update_hourly_usage_summaries(),
        'refresh_limits': refresh_user_limits_cache(),
    }
    
    logger.info(f"Hourly tasks completed: {results}")
    return results


def run_daily_tasks():
    """Run all daily maintenance tasks"""
    logger.info("Starting daily tasks")
    
    results = {
        'cleanup_usage': cleanup_api_usage_data(),
        'daily_summaries': update_daily_usage_summaries(),
        'usage_billing': process_usage_billing(),
        'cleanup_payments': cleanup_payment_failures(),
        'cleanup_tokens': cleanup_expired_tokens(),
        'analytics_report': generate_usage_analytics_report(),
        'health_monitor': monitor_subscription_health(),
    }
    
    logger.info(f"Daily tasks completed: {results}")
    return results


def run_weekly_tasks():
    """Run all weekly maintenance tasks"""
    logger.info("Starting weekly tasks")
    
    results = {
        'database_maintenance': True,
    }
    
    # Run database maintenance
    try:
        # Clean up cache table
        call_command('clearcache')
        
        # Update database statistics (PostgreSQL specific)
        from django.db import connection
        if 'postgresql' in connection.vendor:
            with connection.cursor() as cursor:
                cursor.execute("ANALYZE;")
                logger.info("Database ANALYZE completed")
    
    except Exception as e:
        logger.error(f"Database maintenance error: {e}")
        results['database_maintenance'] = False
    
    logger.info(f"Weekly tasks completed: {results}")
    return results


# For manual execution
if __name__ == "__main__":
    # Example of running tasks manually
    print("Running hourly tasks...")
    print(run_hourly_tasks())
    
    print("\nRunning daily tasks...")
    print(run_daily_tasks()) 