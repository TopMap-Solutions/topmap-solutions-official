from django.contrib import admin, messages

from .models import License, LicenseActivation, LicenseEvent, LicensedProduct


@admin.register(LicensedProduct)
class LicensedProductAdmin(admin.ModelAdmin):
    list_display = ("name", "code", "is_active")
    list_filter = ("is_active",)
    search_fields = ("name", "code")


@admin.register(License)
class LicenseAdmin(admin.ModelAdmin):
    list_display = (
        "key_hint",
        "product",
        "term",
        "customer_email",
        "status",
        "expires_at",
    )
    list_filter = ("state", "term", "product")
    search_fields = ("key_hint", "customer_name", "customer_email", "reference")
    readonly_fields = ("key_hint", "issued_at", "activated_at", "expires_at")
    fieldsets = (
        (
            "License",
            {"fields": ("product", "term", "max_activations", "state", "key_hint")},
        ),
        ("Customer", {"fields": ("customer_name", "customer_email", "reference")}),
        ("Lifecycle", {"fields": ("issued_at", "activated_at", "expires_at")}),
        ("Internal", {"fields": ("notes",)}),
    )

    @admin.display(description="Status")
    def status(self, obj):
        return obj.effective_status

    def response_add(self, request, obj, post_url_continue=None):
        raw = getattr(obj, "_generated_key", None)
        if raw:
            self.message_user(
                request,
                f"Copy this license now; it cannot be recovered later: {raw}",
                level=messages.WARNING,
            )
        return super().response_add(request, obj, post_url_continue)


@admin.register(LicenseActivation)
class LicenseActivationAdmin(admin.ModelAdmin):
    list_display = (
        "license",
        "installation_id",
        "plugin_version",
        "is_active",
        "last_validated_at",
    )
    list_filter = ("is_active", "plugin_version")
    search_fields = ("license__key_hint", "installation_id")
    readonly_fields = [field.name for field in LicenseActivation._meta.fields]


@admin.register(LicenseEvent)
class LicenseEventAdmin(admin.ModelAdmin):
    list_display = ("created_at", "kind", "license", "reason")
    list_filter = ("kind",)
    search_fields = ("license__key_hint", "reason")
    readonly_fields = [field.name for field in LicenseEvent._meta.fields]
