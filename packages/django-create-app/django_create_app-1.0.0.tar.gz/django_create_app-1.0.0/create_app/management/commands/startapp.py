from django.core.management.commands.startapp import Command as StartAppCommand
from django.conf import settings
import os


class Command(StartAppCommand):
    def handle(self, *args, **options):
        apps_dir = str(getattr(settings, "DEFAULT_APP_DIR", "apps"))
        os.makedirs(apps_dir, exist_ok=True)
        os.chdir(apps_dir)
        super().handle(*args, **options)
