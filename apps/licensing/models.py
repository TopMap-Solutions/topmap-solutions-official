import calendar
import hashlib
import hmac
import secrets
from datetime import timedelta

from django.conf import settings
from django.core.validators import MinValueValidator
from django.db import models
from django.utils import timezone


def normalize_key(value):
    return "".join(value.upper().split())


def digest_key(value):
    return hmac.new(
        settings.LICENSING_KEY_PEPPER.encode(),
        normalize_key(value).encode(),
        hashlib.sha256,
    ).hexdigest()


def generate_license_key():
    parts = [secrets.token_hex(3).upper() for _ in range(4)]
    return "TM-" + "-".join(parts)


def add_months(value, months):
    month_index = value.month - 1 + months
    year = value.year + month_index // 12
    month = month_index % 12 + 1
    day = min(value.day, calendar.monthrange(year, month)[1])
    return value.replace(year=year, month=month, day=day)


class LicensedProduct(models.Model):
    name = models.CharField(max_length=120)
    code = models.SlugField(
        unique=True, help_text="Must match the public product code."
    )
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ("name",)

    def __str__(self):
        return self.name


class License(models.Model):
    class Term(models.TextChoices):
        DAYS_14 = "14_days", "14 days"
        MONTH_1 = "1_month", "1 month"
        MONTHS_3 = "3_months", "3 months"
        YEAR_1 = "1_year", "1 year"
        LIFETIME = "lifetime", "Lifetime"

    class State(models.TextChoices):
        ENABLED = "enabled", "Enabled"
        SUSPENDED = "suspended", "Suspended"
        REVOKED = "revoked", "Revoked"

    product = models.ForeignKey(
        LicensedProduct, on_delete=models.PROTECT, related_name="licenses"
    )
    key_digest = models.CharField(max_length=64, unique=True, editable=False)
    key_hint = models.CharField(max_length=24, editable=False)
    term = models.CharField(max_length=20, choices=Term.choices)
    customer_name = models.CharField(max_length=160, blank=True)
    customer_email = models.EmailField(blank=True)
    reference = models.CharField(max_length=120, blank=True)
    state = models.CharField(
        max_length=20, choices=State.choices, default=State.ENABLED
    )
    max_activations = models.PositiveSmallIntegerField(
        default=1, validators=[MinValueValidator(1)]
    )
    issued_at = models.DateTimeField(auto_now_add=True)
    activated_at = models.DateTimeField(null=True, blank=True)
    expires_at = models.DateTimeField(null=True, blank=True)
    notes = models.TextField(blank=True)

    class Meta:
        ordering = ("-issued_at",)

    def __str__(self):
        return f"{self.product.code} · {self.key_hint}"

    @property
    def effective_status(self):
        if self.state != self.State.ENABLED:
            return self.state
        if self.expires_at and self.expires_at <= timezone.now():
            return "expired"
        return "active" if self.activated_at else "unused"

    def set_generated_key(self):
        while True:
            raw = generate_license_key()
            digest = digest_key(raw)
            if not type(self).objects.filter(key_digest=digest).exists():
                break
        self.key_digest = digest
        self.key_hint = f"TM-••••-••••-••••-{raw.rsplit('-', 1)[-1]}"
        self._generated_key = raw

    def save(self, *args, **kwargs):
        if not self.key_digest:
            self.set_generated_key()
        super().save(*args, **kwargs)

    def activate_term(self, activated_at=None):
        activated_at = activated_at or timezone.now()
        self.activated_at = activated_at
        if self.term == self.Term.DAYS_14:
            self.expires_at = activated_at + timedelta(days=14)
        elif self.term == self.Term.MONTH_1:
            self.expires_at = add_months(activated_at, 1)
        elif self.term == self.Term.MONTHS_3:
            self.expires_at = add_months(activated_at, 3)
        elif self.term == self.Term.YEAR_1:
            self.expires_at = add_months(activated_at, 12)
        else:
            self.expires_at = None


class LicenseActivation(models.Model):
    license = models.ForeignKey(
        License, on_delete=models.PROTECT, related_name="activations"
    )
    installation_id = models.CharField(max_length=128)
    device_fingerprint_hash = models.CharField(max_length=64)
    plugin_version = models.CharField(max_length=40, blank=True)
    is_active = models.BooleanField(default=True)
    activated_at = models.DateTimeField(auto_now_add=True)
    last_validated_at = models.DateTimeField(auto_now=True)
    deactivated_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ("-activated_at",)
        constraints = [
            models.UniqueConstraint(
                fields=("license", "installation_id"),
                name="unique_license_installation",
            )
        ]

    def __str__(self):
        return f"{self.license.key_hint} · {self.installation_id[:12]}"


class LicenseEvent(models.Model):
    class Kind(models.TextChoices):
        ACTIVATE = "activate", "Activated"
        VALIDATE = "validate", "Validated"
        DEACTIVATE = "deactivate", "Deactivated"
        REJECT = "reject", "Rejected"

    license = models.ForeignKey(
        License, null=True, blank=True, on_delete=models.SET_NULL, related_name="events"
    )
    activation = models.ForeignKey(
        LicenseActivation,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="events",
    )
    kind = models.CharField(max_length=20, choices=Kind.choices)
    reason = models.CharField(max_length=120, blank=True)
    remote_address_hash = models.CharField(max_length=64, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ("-created_at",)
