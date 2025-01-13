from django.conf import settings
import sys

apps_dir = str(getattr(settings, "DEFAULT_APP_DIR", "apps"))
apps_index = getattr(settings, "DEFAULT_APP_DIR_INDEX", None)

if apps_index is None:
    sys.path.append(apps_dir)
elif isinstance(apps_index, int):
    sys.path.insert(apps_index, apps_dir)