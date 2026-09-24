"""Database-free UI/SEO regression settings. Never loads .env or applies migrations.

Run only the SimpleTestCase suite: python -m django test tests --settings=config.settings.test_ui
"""
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[2]
SECRET_KEY = "isolated-ui-tests-not-a-production-key"
DEBUG = False
ALLOWED_HOSTS = ["testserver", "localhost", "127.0.0.1", "www.topmapsolutions.com"]
DATABASES = {"default": {"ENGINE": "django.db.backends.dummy"}}
INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django.contrib.postgres",
    "wagtail",
    "wagtail.admin",
    "wagtail.documents",
    "wagtail.images",
    "wagtail.search",
    "wagtail.snippets",
    "wagtail.sites",
    "wagtail.users",
    "wagtail.embeds",
    "wagtail.contrib.forms",
    "wagtail.contrib.redirects",
    "modelcluster",
    "taggit",
    "core",
    "apps.guests",
    "apps.case_studies",
]
ROOT_URLCONF = "config.urls"
MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
]
SESSION_ENGINE = "django.contrib.sessions.backends.signed_cookies"
EMAIL_BACKEND = "django.core.mail.backends.locmem.EmailBackend"
TEMPLATES = [{"BACKEND": "django.template.backends.django.DjangoTemplates", "APP_DIRS": True,
    "OPTIONS": {"context_processors": [
        "django.template.context_processors.request",
        "django.contrib.auth.context_processors.auth",
        "django.contrib.messages.context_processors.messages",
        "core.context_processors.navigation",
    ]}}]
STATIC_URL = "/static/"
STATIC_ROOT = BASE_DIR / "staticfiles"
STATICFILES_DIRS = [BASE_DIR / "static"]
MEDIA_URL = "/media/"
MEDIA_ROOT = "/tmp/topmap-test-media"
STORAGES = {"default": {"BACKEND": "django.core.files.storage.InMemoryStorage"},
            "staticfiles": {"BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage"}}
PUBLIC_SITE_URL = "https://topmapsolutions.com"
WAGTAILADMIN_BASE_URL = PUBLIC_SITE_URL
WAGTAIL_SITE_NAME = "TopMap Solutions"
USE_TZ = True
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
