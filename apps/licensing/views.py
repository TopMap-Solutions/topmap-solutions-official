import json

from django.conf import settings
from django.core.cache import cache
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_GET, require_POST

from .services import LicenseDenied, activate, deactivate, validate

MAX_BODY_BYTES = 16_384


def api_response(data, status=200):
    response = JsonResponse(data, status=status)
    response["Cache-Control"] = "no-store"
    response["X-Content-Type-Options"] = "nosniff"
    return response


def client_address(request):
    if settings.LICENSING_TRUST_PROXY_HEADERS:
        forwarded = request.META.get("HTTP_X_FORWARDED_FOR", "")
        if forwarded:
            return forwarded.split(",", 1)[0].strip()
    return request.META.get("REMOTE_ADDR", "unknown")


def rate_limited(request):
    remote = client_address(request)
    bucket = f"licensing-rate:{remote}"
    if cache.add(bucket, 1, timeout=settings.LICENSING_RATE_WINDOW_SECONDS):
        return False
    try:
        count = cache.incr(bucket)
    except ValueError:
        cache.set(bucket, 1, timeout=settings.LICENSING_RATE_WINDOW_SECONDS)
        count = 1
    return count > settings.LICENSING_RATE_LIMIT


def parse_json(request, required):
    content_length = int(request.META.get("CONTENT_LENGTH") or 0)
    if content_length > MAX_BODY_BYTES or request.content_type != "application/json":
        raise ValueError
    data = json.loads(request.body or b"{}")
    if not isinstance(data, dict):
        raise ValueError
    cleaned = {}
    for field, limit in required.items():
        value = data.get(field)
        if not isinstance(value, str) or not value.strip() or len(value) > limit:
            raise ValueError
        cleaned[field] = value.strip()
    cleaned["plugin_version"] = str(data.get("plugin_version", ""))[:40]
    return cleaned


def protected_endpoint(view):
    @csrf_exempt
    @require_POST
    def wrapper(request):
        if rate_limited(request):
            response = api_response({"error": "rate_limited"}, status=429)
            response["Retry-After"] = str(settings.LICENSING_RATE_WINDOW_SECONDS)
            return response
        try:
            return view(request)
        except ValueError, json.JSONDecodeError, UnicodeDecodeError:
            return api_response({"error": "invalid_request"}, status=400)
        except LicenseDenied as exc:
            return api_response({"valid": False, "error": exc.code}, status=403)

    return wrapper


@require_GET
def health(request):
    return api_response({"status": "ok", "api_version": "v1"})


@protected_endpoint
def activate_view(request):
    data = parse_json(
        request,
        {
            "license_key": 128,
            "product_code": 80,
            "installation_id": 128,
            "device_fingerprint": 256,
        },
    )
    payload = activate(
        raw_key=data["license_key"],
        product_code=data["product_code"],
        installation_id=data["installation_id"],
        fingerprint=data["device_fingerprint"],
        plugin_version=data["plugin_version"],
        remote_address=client_address(request),
    )
    return api_response(payload)


@protected_endpoint
def validate_view(request):
    data = parse_json(
        request,
        {
            "activation_token": 4096,
            "product_code": 80,
            "installation_id": 128,
            "device_fingerprint": 256,
        },
    )
    payload = validate(
        token=data["activation_token"],
        product_code=data["product_code"],
        installation_id=data["installation_id"],
        fingerprint=data["device_fingerprint"],
        plugin_version=data["plugin_version"],
        remote_address=client_address(request),
    )
    return api_response(payload)


@protected_endpoint
def deactivate_view(request):
    data = parse_json(
        request, {"activation_token": 4096, "product_code": 80, "installation_id": 128}
    )
    deactivate(
        token=data["activation_token"],
        product_code=data["product_code"],
        installation_id=data["installation_id"],
        remote_address=client_address(request),
    )
    return api_response({"deactivated": True})
