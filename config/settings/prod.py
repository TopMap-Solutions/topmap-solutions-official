from .base import *

# ============================================================
# PRODUCTION
# ============================================================

DEBUG = False

ALLOWED_HOSTS = [
    "topmapsolutions.com",
    "www.topmapsolutions.com",
]


# ============================================================
# CSRF / HTTPS
# ============================================================

CSRF_TRUSTED_ORIGINS = [
    "https://topmapsolutions.com",
    "https://www.topmapsolutions.com",
]

SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
SECURE_SSL_REDIRECT = True

SECURE_HSTS_SECONDS = 3600
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True

SESSION_COOKIE_SECURE = True
SESSION_COOKIE_HTTPONLY = True

CSRF_COOKIE_SECURE = True
CSRF_COOKIE_HTTPONLY = False

USE_X_FORWARDED_HOST = True


# ============================================================
# EMAIL
# ============================================================

EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"

EMAIL_HOST = os.environ["BREVO_HOST"]
EMAIL_PORT = int(os.environ.get("BREVO_PORT", "587"))

EMAIL_USE_TLS = True

EMAIL_HOST_USER = os.environ["BREVO_SMTP_LOGIN"]
EMAIL_HOST_PASSWORD = os.environ["BREVO_SMTP_PASSWORD"]

# ============================================================
# STORAGES
# ============================================================


STORAGES = {
    "default": {
        "BACKEND": "storages.backends.s3.S3Storage",
        "OPTIONS": {
            "access_key": os.environ["B2_APPLICATION_KEY_ID"],
            "secret_key": os.environ["B2_APPLICATION_KEY"],
            "bucket_name": os.environ["B2_BUCKET_NAME"],
            "endpoint_url": os.environ["B2_ENDPOINT_URL"],
            "region_name": os.environ["B2_REGION"],

            "default_acl": None,
            "querystring_auth": False,
        },
    },

    "staticfiles": {
        "BACKEND": (
            "whitenoise.storage.CompressedManifestStaticFilesStorage"
        ),
    },
}