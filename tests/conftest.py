import os

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "proxy_project.settings")

# Ensure Django apps are loaded before test collection
import django  # noqa: E402

django.setup()  # noqa: E402
