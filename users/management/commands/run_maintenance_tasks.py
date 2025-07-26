"""
Management command to run maintenance tasks for the rate limiting system.
This command can be scheduled as a cron job.
"""
from django.core.management.base import BaseCommand

from users.tasks import run_daily_tasks, run_hourly_tasks, run_weekly_tasks


class Command(BaseCommand):
    help = 'Run maintenance tasks for the rate limiting system'

    def add_arguments(self, parser):
        parser.add_argument(
            'task_type',
            choices=['hourly', 'daily', 'weekly'],
            help='Type of maintenance tasks to run',
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be done without actually doing it',
        )

    def handle(self, *args, **options):
        task_type = options['task_type']
        dry_run = options['dry_run']

        if dry_run:
            self.stdout.write(self.style.WARNING(f'DRY RUN: Would run {task_type} maintenance tasks'))
            return

        self.stdout.write(self.style.SUCCESS(f'Running {task_type} maintenance tasks...'))

        try:
            if task_type == 'hourly':
                results = run_hourly_tasks()
            elif task_type == 'daily':
                results = run_daily_tasks()
            elif task_type == 'weekly':
                results = run_weekly_tasks()

            self.stdout.write(self.style.SUCCESS(f'✓ {task_type.title()} tasks completed successfully'))

            # Display results
            for task_name, result in results.items():
                if isinstance(result, (int, bool)):
                    self.stdout.write(f'  {task_name}: {result}')
                elif isinstance(result, dict):
                    self.stdout.write(f'  {task_name}: {len(result)} items')
                else:
                    self.stdout.write(f'  {task_name}: completed')

        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Failed to run {task_type} tasks: {e}'))
            raise
