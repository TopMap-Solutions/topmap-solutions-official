from django.db import models
from django.urls import reverse
from django.utils.text import slugify

from apps.maps.models import Client


class InteractiveMapProject(models.Model):
    client = models.ForeignKey(
        Client,
        on_delete=models.CASCADE,
        related_name="projects",
    )

    name = models.CharField(
        max_length=200,
    )

    slug = models.SlugField(
        max_length=220,
        blank=True,
    )

    description = models.TextField(
        blank=True,
    )

    source_file = models.FileField(
        upload_to="interactive_maps/source/",
        blank=True,
        null=True,
    )

    map_image = models.ImageField(
        upload_to="interactive_maps/maps/",
        blank=True,
        null=True,
    )

    west = models.FloatField(
        null=True,
        blank=True,
    )

    south = models.FloatField(
        null=True,
        blank=True,
    )

    east = models.FloatField(
        null=True,
        blank=True,
    )

    north = models.FloatField(
        null=True,
        blank=True,
    )

    is_public = models.BooleanField(
        default=False,
    )

    expires_at = models.DateTimeField(
        null=True,
        blank=True,
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    updated_at = models.DateTimeField(
        auto_now=True,
    )

    class Meta:
        ordering = ["-created_at"]

        constraints = [
            models.UniqueConstraint(
                fields=["client", "slug"],
                name="unique_client_interactive_map_slug",
            )
        ]

    def __str__(self):
        return f"{self.client.name} - {self.name}"

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)

        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse(
            "interactive_maps:project_detail",
            kwargs={
                "client_slug": self.client.slug,
                "project_slug": self.slug,
            },
        )
