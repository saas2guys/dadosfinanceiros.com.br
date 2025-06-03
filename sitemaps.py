from django.contrib.sitemaps import Sitemap
from django.urls import reverse


class StaticViewSitemap(Sitemap):
    priority = 0.5
    changefreq = 'weekly'

    def items(self):
        return [
            'home',
            'stock_market_api',
            'faq', 
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
            'plans',
            'faq',
        ]

    def location(self, item):
        return reverse(item)


sitemaps = {
    'static': StaticViewSitemap,
    'high_priority': HighPrioritySitemap,
    'financial_data': FinancialDataSitemap,
} 