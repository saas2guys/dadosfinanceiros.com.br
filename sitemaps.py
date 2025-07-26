from django.conf import settings
from django.contrib.sitemaps import Sitemap
from django.urls import reverse
from django.utils import timezone


class StaticViewSitemap(Sitemap):
    """Sitemap for static pages"""

    priority = 0.8
    changefreq = 'weekly'
    protocol = 'https'

    def items(self):
        """Return list of static page names"""
        return [
            'home',
            'faq',
            'blog',
            'api_comparison',
            'waiting_list',
            'waiting_list_success',
            'login',
            'register',
        ]

    def location(self, item):
        return reverse(item)

    def lastmod(self, item):
        return timezone.now()

    def get_urls(self, site=None, **kwargs):
        """Override to set correct domain"""
        urls = super().get_urls(site=site, **kwargs)
        for url in urls:
            url['location'] = url['location'].replace('localhost:8001', 'financialdata.online')
            url['location'] = url['location'].replace('localhost:8000', 'financialdata.online')
            url['location'] = url['location'].replace('127.0.0.1:8001', 'financialdata.online')
            url['location'] = url['location'].replace('127.0.0.1:8000', 'financialdata.online')
        return urls


class ProductPagesSitemap(Sitemap):
    """Sitemap for product/service pages"""

    priority = 1.0
    changefreq = 'monthly'
    protocol = 'https'

    def items(self):
        """Return list of product page names"""
        return [
            'stock_market_api',
            'options_api',
            'futures_api',
            'forex_api',
            'crypto_api',
            'fundamentals_api',
            'technical_analysis_api',
            'news_api',
            'earnings_api',
            'economic_indicators_api',
            'indices_api',
            'commodities_api',
        ]

    def location(self, item):
        return reverse(item)

    def lastmod(self, item):
        return timezone.now()

    def get_urls(self, site=None, **kwargs):
        """Override to set correct domain"""
        urls = super().get_urls(site=site, **kwargs)
        for url in urls:
            url['location'] = url['location'].replace('localhost:8001', 'financialdata.online')
            url['location'] = url['location'].replace('localhost:8000', 'financialdata.online')
            url['location'] = url['location'].replace('127.0.0.1:8001', 'financialdata.online')
            url['location'] = url['location'].replace('127.0.0.1:8000', 'financialdata.online')
        return urls


class SEOLandingPagesSitemap(Sitemap):
    """Sitemap for SEO landing pages"""

    priority = 0.7
    changefreq = 'monthly'
    protocol = 'https'

    def items(self):
        """Return list of SEO landing page patterns"""
        return [
            'stocks_api',
            'equity_data_api',
            'currency_api',
            'fx_api',
            'cryptocurrency_api',
            'bitcoin_api',
            'digital_assets_api',
            'derivatives_api',
            'index_api',
            'market_indices_api',
            'commodity_data_api',
            'economic_data_api',
            'macro_data_api',
            'financial_statements_api',
            'news_sentiment_api',
            'financial_news_api',
            'technical_indicators_api',
            'ta_api',
            'earnings_calendar_api',
            'earnings_data_api',
            'financial_api_comparison',
        ]

    def location(self, item):
        return reverse(item)

    def lastmod(self, item):
        return timezone.now()

    def get_urls(self, site=None, **kwargs):
        """Override to set correct domain"""
        urls = super().get_urls(site=site, **kwargs)
        for url in urls:
            url['location'] = url['location'].replace('localhost:8001', 'financialdata.online')
            url['location'] = url['location'].replace('localhost:8000', 'financialdata.online')
            url['location'] = url['location'].replace('127.0.0.1:8001', 'financialdata.online')
            url['location'] = url['location'].replace('127.0.0.1:8000', 'financialdata.online')
        return urls


class InternationalizedViewSitemap(Sitemap):
    """Sitemap for internationalized views (English and Portuguese)"""

    priority = 0.8
    changefreq = 'weekly'
    protocol = 'https'

    def items(self):
        """Return list of page names for both languages"""
        # Base pages available in both languages
        base_pages = [
            'home',
            'faq',
            'blog',
            'api_comparison',
            'waiting_list',
            'login',
            'register',
            'stock_market_api',
            'options_api',
            'futures_api',
            'forex_api',
            'crypto_api',
            'fundamentals_api',
            'technical_analysis_api',
            'news_api',
            'earnings_api',
            'economic_indicators_api',
            'indices_api',
            'commodities_api',
        ]

        # Generate language-specific URLs
        language_pages = []
        for lang_code in ['en', 'pt-br']:
            for page in base_pages:
                language_pages.append(f"{lang_code}:{page}")

        return language_pages

    def location(self, item):
        lang_code, page_name = item.split(':', 1)

        # Use the reverse function with language code
        from django.utils.translation import activate

        current_language = timezone.get_current_timezone()

        activate(lang_code.replace('-', '_'))
        url = reverse(page_name)

        # Prepend language code to URL
        if not url.startswith(f'/{lang_code}/'):
            url = f'/{lang_code}{url}'

        return url

    def priority(self, item):
        lang_code, page_name = item.split(':', 1)

        # Higher priority for English and main product pages
        if lang_code == 'en':
            if page_name in ['home', 'stock_market_api', 'options_api', 'fundamentals_api', 'crypto_api']:
                return 1.0
            return 0.8
        else:  # Portuguese
            if page_name in ['home', 'stock_market_api', 'options_api', 'fundamentals_api']:
                return 0.9
            return 0.7

    def lastmod(self, item):
        return timezone.now()

    def get_urls(self, site=None, **kwargs):
        """Override to set correct domain"""
        urls = super().get_urls(site=site, **kwargs)
        for url in urls:
            url['location'] = url['location'].replace('localhost:8001', 'financialdata.online')
            url['location'] = url['location'].replace('localhost:8000', 'financialdata.online')
            url['location'] = url['location'].replace('127.0.0.1:8001', 'financialdata.online')
            url['location'] = url['location'].replace('127.0.0.1:8000', 'financialdata.online')
        return urls


# Define the sitemaps dictionary
sitemaps = {
    'static': StaticViewSitemap,
    'products': ProductPagesSitemap,
    'seo': SEOLandingPagesSitemap,
    'i18n': InternationalizedViewSitemap,
}
