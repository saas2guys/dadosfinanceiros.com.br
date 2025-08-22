import logging

from django.core.management.base import BaseCommand, CommandError
from django.conf import settings

from users.management.plan_feature_config import FEATURES, PLANS
from users.models import Feature, Plan


class Command(BaseCommand):
    help = 'Synchronize features, plans, and their relationships to exactly match the product matrix.'

    def handle(self, *args, **options):
        logger = logging.getLogger('users_plans_sync')
        logger.info('Starting users_plans_sync command')

        env = getattr(settings, 'ENV', 'local')
        logger.info('Detected environment: %s', env)
        if env not in ('dev', 'local', 'development'):
            raise CommandError(f'This command is restricted to development environments. Current ENV={env}')

        if not FEATURES or not PLANS:
            self.stdout.write(self.style.ERROR('Configuration is empty. Nothing to do.'))
            logger.error('Configuration empty: FEATURES or PLANS are missing')
            return

        # Ensure features exist and are active, build name->Feature map
        existing_features = {f.name: f for f in Feature.objects.filter(name__in=FEATURES)}
        feature_map = {}
        for name in FEATURES:
            feature = existing_features.get(name)
            if feature is None:
                feature = Feature.objects.create(
                    name=name,
                    description=f'Access to {name.lower()}',
                    is_active=True,
                )
                feature_map[name] = feature
                logger.info('Created feature: %s', name)
                continue

            must_update = False
            if not feature.is_active:
                feature.is_active = True
                must_update = True
            if not feature.description:
                feature.description = f'Access to {name.lower()}'
                must_update = True
            if must_update:
                feature.save(update_fields=['is_active', 'description'])
                logger.info('Updated feature: %s', name)
            feature_map[name] = feature

        if not feature_map:
            self.stdout.write(self.style.ERROR('Could not create or fetch features.'))
            logger.error('Failed to create or fetch any features')
            return

        logger.info('Features ensured')

        # Upsert plans (without M2M features yet)
        plan_objects = {}
        for plan_name, cfg in PLANS.items():
            plan, created = Plan.objects.get_or_create(
                name=plan_name,
                defaults={
                    'description': cfg['description'],
                    'price_monthly': cfg['price_monthly'],
                    'price_yearly': cfg['price_yearly'],
                    'daily_request_limit': cfg['daily_request_limit'],
                    'hourly_request_limit': cfg['hourly_request_limit'],
                    'monthly_request_limit': cfg['monthly_request_limit'],
                    'burst_limit': cfg['burst_limit'],
                    'is_active': True,
                    'is_free': cfg['is_free'],
                    'is_metered': cfg['is_metered'],
                },
            )

            if not created:
                changed_fields = []
                mapping = {
                    'description': cfg['description'],
                    'price_monthly': cfg['price_monthly'],
                    'price_yearly': cfg['price_yearly'],
                    'daily_request_limit': cfg['daily_request_limit'],
                    'hourly_request_limit': cfg['hourly_request_limit'],
                    'monthly_request_limit': cfg['monthly_request_limit'],
                    'burst_limit': cfg['burst_limit'],
                    'is_active': True,
                    'is_free': cfg['is_free'],
                    'is_metered': cfg['is_metered'],
                }
                for field, value in mapping.items():
                    if getattr(plan, field) == value:
                        continue
                    setattr(plan, field, value)
                    changed_fields.append(field)
                if changed_fields:
                    plan.save(update_fields=changed_fields)

            plan_objects[plan_name] = plan
            logger.info('Plan %s %s', plan_name, 'created' if created else 'updated')

        # Assign exact feature sets to each plan
        for plan_name, cfg in PLANS.items():
            plan = plan_objects[plan_name]
            names = list(cfg.get('features') or [])
            if not names:
                plan.features.clear()
                logger.info('Cleared features for plan: %s', plan_name)
                continue
            plan.features.set([feature_map[n] for n in names])
            logger.info('Assigned features to plan: %s', plan_name)

        self.stdout.write(self.style.SUCCESS('Plans and features synchronized.'))
        logger.info('Completed users_plans_sync command')


