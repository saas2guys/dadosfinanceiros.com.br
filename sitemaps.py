from django.contrib.sitemaps import Sitemap
from django.urls import reverse


class StaticViewSitemap(Sitemap):
    priority = 0.5
    changefreq = 'weekly'

    def items(self):
        return [
            'home',
            'stock_market_api',
            'forex_api',
            'crypto_api',
            'faq', 
            'blog',
            'api_comparison',
            'plans',
            'waiting_list',
            'login',
        ]

    def location(self, item):
        return reverse(item)


class HighPrioritySitemap(Sitemap):
    priority = 1.0
    changefreq = 'daily'

    def items(self):
        return ['home']

    def location(self, item):
        return reverse(item)


class FinancialDataSitemap(Sitemap):
    priority = 0.8
    changefreq = 'weekly'

    def items(self):
        return [
            'stock_market_api',
            'forex_api', 
            'crypto_api',
            'api_comparison',
            'plans',
            'faq',
        ]

    def location(self, item):
        return reverse(item)


class ContentSitemap(Sitemap):
    priority = 0.7
    changefreq = 'weekly'

    def items(self):
        return [
            'blog',
            'faq',
            'api_comparison',
        ]

    def location(self, item):
        return reverse(item)


class UserPagesSitemap(Sitemap):
    priority = 0.3
    changefreq = 'monthly'

    def items(self):
        return [
            'waiting_list',
            'login',
        ]

    def location(self, item):
        return reverse(item)


# Export all sitemaps
sitemaps = {
    'high-priority': HighPrioritySitemap,
    'financial-data': FinancialDataSitemap,
    'content': ContentSitemap,
    'user-pages': UserPagesSitemap,
    'static': StaticViewSitemap,
} 