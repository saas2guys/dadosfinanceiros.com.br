"""
Management command to set up database-based rate limiting system.
This command initializes the cache table and sets up default plans.
"""
from django.core.management.base import BaseCommand
from django.core.management import call_command
from django.core.cache import caches
from users.models import Plan, User, SubscriptionStatus


class Command(BaseCommand):
    help = 'Set up database-based rate limiting system'

    def add_arguments(self, parser):
        parser.add_argument(
            '--create-cache-table',
            action='store_true',
            help='Create the database cache table for rate limiting',
        )
        parser.add_argument(
            '--create-default-plans',
            action='store_true',
            help='Create default subscription plans',
        )
        parser.add_argument(
            '--migrate-users',
            action='store_true',
            help='Migrate existing users to use cached limits',
        )
        parser.add_argument(
            '--all',
            action='store_true',
            help='Run all setup tasks',
        )

    def handle(self, *args, **options):
        if options['all']:
            options['create_cache_table'] = True
            options['create_default_plans'] = True
            options['migrate_users'] = True

        self.stdout.write(
            self.style.SUCCESS('Setting up database-based rate limiting system...')
        )

        if options['create_cache_table']:
            self.create_cache_table()

        if options['create_default_plans']:
            self.create_default_plans()

        if options['migrate_users']:
            self.migrate_users()

        self.stdout.write(
            self.style.SUCCESS('Rate limiting setup completed successfully!')
        )

    def create_cache_table(self):
        """Create the database cache table"""
        self.stdout.write('Creating database cache table...')
        try:
            call_command('createcachetable', 'rate_limit_cache', verbosity=0)
            self.stdout.write(
                self.style.SUCCESS('✓ Database cache table created')
            )
        except Exception as e:
            self.stdout.write(
                self.style.WARNING(f'Cache table may already exist: {e}')
            )

    def create_default_plans(self):
        """Create default subscription plans with rate limits"""
        self.stdout.write('Creating default subscription plans...')
        
        default_plans = [
            {
                'name': 'Basic',
                'description': 'Plano básico com acesso essencial',
                'price_monthly': 29.00,
                'daily_request_limit': 10000,  # Limite generoso para começar
                'hourly_request_limit': 1000,
                'monthly_request_limit': 300000,
                'burst_limit': 100,
                'features': [
                    'Chamadas de API ilimitadas',
                    'Dados em tempo real',
                    'Ações dos EUA, Brasil e + 25 Bolsas',
                    'Forex',
                    'Criptos',
                    'Dados históricos de 5 anos',
                    'Downloads de arquivos ilimitados',
                    'WebSockets',
                    'Instantâneo',
                ],
            },
            {
                'name': 'Pró',
                'description': 'Para investidores e desenvolvedores sérios',
                'price_monthly': 57.00,
                'daily_request_limit': 50000,
                'hourly_request_limit': 5000,
                'monthly_request_limit': 1500000,
                'burst_limit': 500,
                'features': [
                    'Todos os recursos do plano Basic',
                    'Dados históricos de 30 anos',
                    '47 mercados',
                ],
            },
            {
                'name': 'Premium',
                'description': 'Acesso completo para profissionais e empresas',
                'price_monthly': 148.00,
                'daily_request_limit': 200000,
                'hourly_request_limit': 20000,
                'monthly_request_limit': 6000000,
                'burst_limit': 2000,
                'features': [
                    'Todos os recursos do plano Pró',
                    'Cobertura global',
                    '13F Holdings Institucionais*',
                    'Participações em ETFs e fundos mútuos',
                    'Entrega em grandes quantidades e em lotes',
                ],
            },
        ]

        created_count = 0
        for plan_data in default_plans:
            plan, created = Plan.objects.get_or_create(
                name=plan_data['name'],
                defaults=plan_data
            )
            if created:
                created_count += 1
                self.stdout.write(f'  ✓ Created plan: {plan.name}')
            else:
                self.stdout.write(f'  - Plan already exists: {plan.name}')

        self.stdout.write(
            self.style.SUCCESS(f'✓ {created_count} new plans created')
        )

    def migrate_users(self):
        """Migrate existing users to use cached limits"""
        self.stdout.write('Migrating existing users to cached limits...')
        
        # Get users without a current plan and assign free plan
        free_plan = Plan.objects.filter(is_free=True, is_active=True).first()
        if not free_plan:
            self.stdout.write(
                self.style.ERROR('No free plan found. Please run --create-default-plans first.')
            )
            return

        users_without_plan = User.objects.filter(current_plan__isnull=True)
        updated_count = 0

        for user in users_without_plan:
            user.current_plan = free_plan
            user.refresh_limits_cache()
            updated_count += 1

        if updated_count > 0:
            self.stdout.write(f'  ✓ Updated {updated_count} users with free plan')

        # Refresh cached limits for all users
        all_users = User.objects.select_related('current_plan').all()
        refresh_count = 0

        for user in all_users:
            if user.current_plan:
                user.refresh_limits_cache()
                refresh_count += 1

        self.stdout.write(
            self.style.SUCCESS(f'✓ Refreshed cached limits for {refresh_count} users')
        )

        # Update subscription statuses for active users
        active_users = User.objects.filter(
            current_plan__isnull=False,
            subscription_status=SubscriptionStatus.INACTIVE
        )
        
        for user in active_users:
            if user.current_plan.is_free:
                user.subscription_status = SubscriptionStatus.ACTIVE
                user.save(update_fields=['subscription_status'])

        self.stdout.write(
            self.style.SUCCESS(f'✓ Updated subscription status for {len(active_users)} users')
        ) 