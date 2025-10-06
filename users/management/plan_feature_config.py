from decimal import Decimal

# Centralized configuration of features and plans so multiple commands can use
# the exact same source of truth.

FEATURES = [
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


PLANS = {
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
        'features': FEATURES,
        'daily_request_limit': 0,
        'hourly_request_limit': 0,
        'monthly_request_limit': 0,
        'burst_limit': 0,
        'is_free': False,
        'is_metered': False,
    },
}
