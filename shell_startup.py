# Django Shell Plus Startup Script
# Usage: python manage.py shell_plus -c "exec(open('shell_startup.py').read())"

from pprint import pprint
from django.conf import settings

def show_database_config():
    """Display current database configuration with pretty formatting"""
    print("\n" + "="*60)
    print("🔗 DATABASE CONFIGURATION")
    print("="*60)
    pprint(settings.DATABASES)
    print("="*60)
    print("🚀 Shell Plus Ready!")
    print("💡 All Django models and utilities are imported.")
    
    # Only show SQL info if django_extensions is available
    if 'django_extensions' in settings.INSTALLED_APPS:
        print("💡 SQL queries will be displayed with --print-sql")
        print("💡 Use show_database_config() to display DB info again.")
    else:
        print("💡 Running in basic shell mode")
        
    print("="*60 + "\n")

# Auto-display database config
show_database_config() 