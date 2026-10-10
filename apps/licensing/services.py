import hashlib
import hmac

from django.conf import settings
from django.core import signing
from django.db import transaction
from django.utils import timezone

from .models import License, LicenseActivation, LicenseEvent, digest_key

TOKEN_SALT = "topmap.licensing.activation.v1"


class LicenseDenied(Exception):
    def __init__(self, code="license_denied"):
        self.code = code


def safe_hash(value):
    return hashlib.sha256(value.encode()).hexdigest()


def remote_hash(value):
    if not value:
        return ""
    return hmac.new(
        settings.SECRET_KEY.encode(), value.encode(), hashlib.sha256
    ).hexdigest()


def issue_token(activation):
    return signing.dumps(
        {
            "activation_id": activation.pk,
            "installation_id": activation.installation_id,
            "product_code": activation.license.product.code,
        },
        salt=TOKEN_SALT,
        compress=True,
    )


def license_payload(activation):
    license_obj = activation.license
    return {
        "valid": license_obj.effective_status == "active" and activation.is_active,
        "status": license_obj.effective_status,
        "product_code": license_obj.product.code,
        "term": license_obj.term,
        "expires_at": (
            license_obj.expires_at.isoformat() if license_obj.expires_at else None
        ),
        "server_time": timezone.now().isoformat(),
        "activation_token": issue_token(activation),
    }


def find_license(raw_key):
    try:
        return License.objects.select_related("product").get(
            key_digest=digest_key(raw_key)
        )
    except License.DoesNotExist as exc:
        raise LicenseDenied() from exc


@transaction.atomic
def activate(
    *,
    raw_key,
    product_code,
    installation_id,
    fingerprint,
    plugin_version,
    remote_address,
):
    license_obj = find_license(raw_key)
    license_obj = (
        License.objects.select_for_update()
        .select_related("product")
        .get(pk=license_obj.pk)
    )
    if (
        license_obj.product.code != product_code
        or not license_obj.product.is_active
        or license_obj.state != License.State.ENABLED
        or license_obj.effective_status == "expired"
    ):
        _event(
            license_obj, None, LicenseEvent.Kind.REJECT, "not_available", remote_address
        )
        raise LicenseDenied()

    fingerprint_hash = safe_hash(fingerprint)
    activation = LicenseActivation.objects.filter(
        license=license_obj, installation_id=installation_id
    ).first()
    if activation and activation.device_fingerprint_hash != fingerprint_hash:
        _event(
            license_obj,
            activation,
            LicenseEvent.Kind.REJECT,
            "device_mismatch",
            remote_address,
        )
        raise LicenseDenied()
    if not activation:
        active_count = LicenseActivation.objects.filter(
            license=license_obj, is_active=True
        ).count()
        if active_count >= license_obj.max_activations:
            _event(
                license_obj,
                None,
                LicenseEvent.Kind.REJECT,
                "activation_limit",
                remote_address,
            )
            raise LicenseDenied()
        activation = LicenseActivation.objects.create(
            license=license_obj,
            installation_id=installation_id,
            device_fingerprint_hash=fingerprint_hash,
            plugin_version=plugin_version,
        )
    else:
        other_active = (
            LicenseActivation.objects.filter(license=license_obj, is_active=True)
            .exclude(pk=activation.pk)
            .count()
        )
        if not activation.is_active and other_active >= license_obj.max_activations:
            raise LicenseDenied()
        activation.is_active = True
        activation.deactivated_at = None
        activation.plugin_version = plugin_version
        activation.save(
            update_fields=(
                "is_active",
                "deactivated_at",
                "plugin_version",
                "last_validated_at",
            )
        )

    if not license_obj.activated_at:
        license_obj.activate_term()
        license_obj.save(update_fields=("activated_at", "expires_at"))
    _event(license_obj, activation, LicenseEvent.Kind.ACTIVATE, "", remote_address)
    return license_payload(activation)


def activation_from_token(token, installation_id, product_code):
    try:
        data = signing.loads(
            token,
            salt=TOKEN_SALT,
            max_age=settings.LICENSING_TOKEN_MAX_AGE_SECONDS,
        )
    except signing.BadSignature as exc:
        raise LicenseDenied("invalid_token") from exc
    if (
        data.get("installation_id") != installation_id
        or data.get("product_code") != product_code
    ):
        raise LicenseDenied("invalid_token")
    try:
        return LicenseActivation.objects.select_related("license__product").get(
            pk=data["activation_id"], installation_id=installation_id
        )
    except (KeyError, LicenseActivation.DoesNotExist) as exc:
        raise LicenseDenied("invalid_token") from exc


def validate(
    *, token, product_code, installation_id, fingerprint, plugin_version, remote_address
):
    activation = activation_from_token(token, installation_id, product_code)
    if activation.device_fingerprint_hash != safe_hash(fingerprint):
        _event(
            activation.license,
            activation,
            LicenseEvent.Kind.REJECT,
            "device_mismatch",
            remote_address,
        )
        raise LicenseDenied()
    if not activation.is_active or activation.license.effective_status != "active":
        _event(
            activation.license,
            activation,
            LicenseEvent.Kind.REJECT,
            "not_available",
            remote_address,
        )
        raise LicenseDenied("license_inactive")
    activation.plugin_version = plugin_version
    activation.save(update_fields=("plugin_version", "last_validated_at"))
    _event(
        activation.license, activation, LicenseEvent.Kind.VALIDATE, "", remote_address
    )
    return license_payload(activation)


@transaction.atomic
def deactivate(*, token, product_code, installation_id, remote_address):
    activation = activation_from_token(token, installation_id, product_code)
    activation.is_active = False
    activation.deactivated_at = timezone.now()
    activation.save(update_fields=("is_active", "deactivated_at", "last_validated_at"))
    _event(
        activation.license, activation, LicenseEvent.Kind.DEACTIVATE, "", remote_address
    )


def _event(license_obj, activation, kind, reason, remote_address):
    LicenseEvent.objects.create(
        license=license_obj,
        activation=activation,
        kind=kind,
        reason=reason,
        remote_address_hash=remote_hash(remote_address),
    )
