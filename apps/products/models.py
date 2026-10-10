from django.db import models
from django.urls import reverse
from wagtail.admin.panels import FieldPanel, MultiFieldPanel
from wagtail.fields import StreamField
from wagtail.images import get_image_model_string
from wagtail.snippets.models import register_snippet

from .blocks import editorial_blocks


class PublishableQuerySet(models.QuerySet):
    def public(self):
        return self.filter(is_published=True)


@register_snippet
class Product(models.Model):
    class Status(models.TextChoices):
        COMING_SOON = "coming_soon", "Coming soon"
        AVAILABLE = "available", "Available"
        DISCONTINUED = "discontinued", "Discontinued"

    name = models.CharField(max_length=120)
    slug = models.SlugField(unique=True)
    product_code = models.SlugField(
        unique=True,
        help_text="Stable code shared with the licensing system. Do not change after release.",
    )
    summary = models.CharField(max_length=300)
    body = StreamField(editorial_blocks(), blank=True, use_json_field=True)
    card_image = models.ForeignKey(
        get_image_model_string(),
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
    )
    status = models.CharField(
        max_length=20, choices=Status.choices, default=Status.COMING_SOON
    )
    current_version = models.CharField(max_length=40, blank=True)
    download_url = models.URLField(blank=True)
    is_published = models.BooleanField(
        default=False,
        help_text="Only explicitly published products appear on the public website.",
    )
    display_order = models.PositiveIntegerField(default=0)
    seo_title = models.CharField(max_length=70, blank=True)
    search_description = models.CharField(max_length=170, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = PublishableQuerySet.as_manager()

    panels = [
        MultiFieldPanel(
            ["name", "slug", "product_code", "summary", "card_image", "status"]
        ),
        FieldPanel("body"),
        MultiFieldPanel(["current_version", "download_url"], heading="Release"),
        MultiFieldPanel(["is_published", "display_order"], heading="Publishing"),
        MultiFieldPanel(["seo_title", "search_description"], heading="SEO"),
    ]

    class Meta:
        ordering = ("display_order", "name", "pk")

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse("products:detail", kwargs={"product_slug": self.slug})


@register_snippet
class ProductGuide(models.Model):
    class Kind(models.TextChoices):
        MANUAL = "manual", "Manual"
        TRAINING = "training", "Training"
        VIDEO = "video", "Video guide"

    product = models.ForeignKey(
        Product, on_delete=models.CASCADE, related_name="guides"
    )
    title = models.CharField(max_length=160)
    slug = models.SlugField()
    kind = models.CharField(max_length=20, choices=Kind.choices, default=Kind.MANUAL)
    summary = models.CharField(max_length=300, blank=True)
    body = StreamField(editorial_blocks(), blank=True, use_json_field=True)
    is_published = models.BooleanField(default=False)
    display_order = models.PositiveIntegerField(default=0)
    seo_title = models.CharField(max_length=70, blank=True)
    search_description = models.CharField(max_length=170, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = PublishableQuerySet.as_manager()

    panels = [
        MultiFieldPanel(["product", "title", "slug", "kind", "summary"]),
        FieldPanel("body"),
        MultiFieldPanel(["is_published", "display_order"], heading="Publishing"),
        MultiFieldPanel(["seo_title", "search_description"], heading="SEO"),
    ]

    class Meta:
        ordering = ("display_order", "title", "pk")
        constraints = [
            models.UniqueConstraint(
                fields=("product", "slug"), name="unique_product_guide_slug"
            )
        ]

    def __str__(self):
        return f"{self.product}: {self.title}"

    def get_absolute_url(self):
        return reverse(
            "products:guide",
            kwargs={"product_slug": self.product.slug, "guide_slug": self.slug},
        )
