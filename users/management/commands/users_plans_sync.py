from django.core.management.base import BaseCommand, CommandError
from django.conf import settings

from users.management.plan_feature_config import FEATURES, PLANS
from users.models import Feature, Plan


class Command(BaseCommand):
    help = 'Synchronize features, plans, and their relationships to exactly match the product matrix.'

    def handle(self, *args, **options):
        env = getattr(settings, 'ENV', 'local')
        if env not in ('dev', 'local', 'development'):
            raise CommandError(f'This command is restricted to development environments. Current ENV={env}')

        if not FEATURES or not PLANS:
            self.stdout.write(self.style.ERROR('Configuration is empty. Nothing to do.'))
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
            feature_map[name] = feature

        if not feature_map:
            self.stdout.write(self.style.ERROR('Could not create or fetch features.'))
            return

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

        # Assign exact feature sets to each plan
        for plan_name, cfg in PLANS.items():
            plan = plan_objects[plan_name]
            names = list(cfg.get('features') or [])
            if not names:
                plan.features.clear()
                continue
            plan.features.set([feature_map[n] for n in names])

        self.stdout.write(self.style.SUCCESS('Plans and features synchronized.'))


