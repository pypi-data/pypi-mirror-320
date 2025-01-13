from django.conf import settings
import sys

apps_dir = str(getattr(settings, "DEFAULT_APP_DIR", "apps"))
sys.path.append(apps_dir)