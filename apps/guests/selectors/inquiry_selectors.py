from datetime import timedelta
from django.utils import timezone
from apps.guests.models import Guest


def check_email_cooldown(email: str) -> bool:
    """Return True if the email was used within the last 24 hours."""

    cooldown = Guest.objects.filter(
        email=email,
        created_at__gte=timezone.now() - timedelta(hours=24),
    ).exists()

    return cooldown
