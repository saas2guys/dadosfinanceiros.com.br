from django.core.management.base import BaseCommand
from decimal import Decimal

from users.models import Plan, Feature


class Command(BaseCommand):
    help = 'Create plans with their specific features'

    def add_arguments(self, parser):
        parser.add_argument(
            '--delete-existing',
            action='store_true',
            help='Delete existing plans and features before creating new ones',
        )

    def handle(self, *args, **options):

        all_features = [
            'Unlimited API calls',
            'Real-time data',
            'US, Brazil, and +25 other stock exchanges',
            'Forex',
            'Crypto',
            '5 years of historical data',
            'Unlimited file downloads',
            'WebSockets',
            'Snapshot',
            '30 years of historical data',
            '47 markets',
            'Global coverage',
            '13F Institutional Holdings',
            'ETF and mutual fund holdings',
            'Bulk and batch delivery',
        ]


        plans_config = {
            'Basic': {
                'price_monthly': Decimal('29.00'),
                'price_yearly': Decimal('290.00'),
                'description': 'Essential features for individual developers and small projects',
                'features': [
                    'Unlimited API calls',
                    'Real-time data',
                    'US, Brazil, and +25 other stock exchanges',
                    'Forex',
                    'Crypto',
                    '5 years of historical data',
                    'Unlimited file downloads',
                    'WebSockets',
                    'Snapshot',
                ],
                'daily_request_limit': 10000,
                'hourly_request_limit': 1000,
                'monthly_request_limit': 300000,
                'burst_limit': 100,
                'is_free': False,
                'is_metered': False,
            },
            'Pro': {
                'price_monthly': Decimal('57.00'),
                'price_yearly': Decimal('570.00'),
                'description': 'Advanced features for growing businesses and professional traders',
                'features': [
                    'Unlimited API calls',
                    'Real-time data',
                    'US, Brazil, and +25 other stock exchanges',
                    'Forex',
                    'Crypto',
                    '5 years of historical data',
                    'Unlimited file downloads',
                    'WebSockets',
                    'Snapshot',
                    '30 years of historical data',
                    '47 markets',
                ],
                'daily_request_limit': 50000,
                'hourly_request_limit': 5000,
                'monthly_request_limit': 1500000,
                'burst_limit': 500,
                'is_free': False,
                'is_metered': False,
            },
            'Premium': {
                'price_monthly': Decimal('148.00'),
                'price_yearly': Decimal('1480.00'),
                'description': 'Complete access to all features for enterprise and institutional use',
                'features': all_features,
                'daily_request_limit': 0,
                'hourly_request_limit': 0,
                'monthly_request_limit': 0,
                'burst_limit': 0,
                'is_free': False,
                'is_metered': False,
            },
            'Free': {
                'price_monthly': Decimal('0.00'),
                'price_yearly': Decimal('0.00'),
                'description': 'Limited access for testing and evaluation',
                'features': [
                    'Real-time data',
                    'US, Brazil, and +25 other stock exchanges',
                    'Snapshot',
                ],
                'daily_request_limit': 100,
                'hourly_request_limit': 10,
                'monthly_request_limit': 3000,
                'burst_limit': 20,
                'is_free': True,
                'is_metered': False,
            }
        }

        if options['delete_existing']:
            Plan.objects.all().delete()
            Feature.objects.all().delete()
            self.stdout.write('Deleted existing plans and features.')

        feature_objects = {}
        for feature_name in all_features:
            feature, created = Feature.objects.get_or_create(
                name=feature_name,
                defaults={
                    'description': f'Access to {feature_name.lower()}',
                    'is_active': True
                }
            )
            feature_objects[feature_name] = feature

        for plan_name, config in plans_config.items():
            plan, created = Plan.objects.get_or_create(
                name=plan_name,
                defaults={
                    'description': config['description'],
                    'price_monthly': config['price_monthly'],
                    'price_yearly': config['price_yearly'],
                    'daily_request_limit': config['daily_request_limit'],
                    'hourly_request_limit': config['hourly_request_limit'],
                    'monthly_request_limit': config['monthly_request_limit'],
                    'burst_limit': config['burst_limit'],
                    'is_active': True,
                    'is_free': config['is_free'],
                    'is_metered': config['is_metered'],
                }
            )

            if not created:
                plan.description = config['description']
                plan.price_monthly = config['price_monthly']
                plan.price_yearly = config['price_yearly']
                plan.daily_request_limit = config['daily_request_limit']
                plan.hourly_request_limit = config['hourly_request_limit']
                plan.monthly_request_limit = config['monthly_request_limit']
                plan.burst_limit = config['burst_limit']
                plan.is_free = config['is_free']
                plan.is_metered = config['is_metered']
                plan.save()

            plan.features.clear()
            plan_features = [feature_objects[name] for name in config['features']]
            plan.features.add(*plan_features)

        self.stdout.write(
            self.style.SUCCESS(
                f'Successfully created {len(all_features)} features and {len(plans_config)} plans.'
            )
        )
