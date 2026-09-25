"""Full-suite settings: temporary SQLite database, no .env or external services."""
from .test_ui import *

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": ":memory:",
    }
}
SESSION_ENGINE = "django.contrib.sessions.backends.db"
MIDDLEWARE = [*MIDDLEWARE, "wagtail.contrib.redirects.middleware.RedirectMiddleware"]
PASSWORD_HASHERS = ["django.contrib.auth.hashers.MD5PasswordHasher"]
