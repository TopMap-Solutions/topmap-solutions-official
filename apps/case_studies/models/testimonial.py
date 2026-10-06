from django.db import models

from wagtail.admin.panels import FieldPanel
from wagtail.images import get_image_model_string
from wagtail.search import index
from wagtail.snippets.models import register_snippet
from wagtail.snippets.views.snippets import SnippetViewSet


class Testimonial(index.Indexed, models.Model):
    quote = models.TextField()
    name = models.CharField(
        max_length=255,
        blank=True,
        help_text="Optional. Leave blank to attribute the testimonial to the organization.",
    )
    organization = models.CharField(
        max_length=255,
        blank=True,
        help_text="Optional. Leave both name and organization blank for Anonymous.",
    )
    logo = models.ForeignKey(
        get_image_model_string(),
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
    )
    approved_for_publication = models.BooleanField(
        default=False,
        help_text="Confirm that TopMap has permission to publish this testimonial.",
    )
    display_order = models.PositiveIntegerField(
        default=0,
        help_text="Lower numbers appear first.",
    )

    panels = [
        FieldPanel("quote"),
        FieldPanel("name"),
        FieldPanel("organization"),
        FieldPanel("logo"),
        FieldPanel("approved_for_publication"),
        FieldPanel("display_order"),
    ]
    search_fields = [
        index.SearchField("quote"),
        index.SearchField("name"),
        index.SearchField("organization"),
    ]

    class Meta:
        ordering = ["display_order", "pk"]

    @property
    def attribution(self):
        return self.name or self.organization or "Anonymous"

    @property
    def logo_alt(self):
        return f"{self.organization or self.name or 'Testimonial'} logo"

    def __str__(self):
        return self.attribution


class TestimonialViewSet(SnippetViewSet):
    model = Testimonial
    icon = "openquote"
    list_display = [
        "name",
        "organization",
        "approved_for_publication",
        "display_order",
    ]
    list_filter = ["approved_for_publication"]
    search_fields = ["quote", "name", "organization"]
    ordering = ["display_order", "pk"]


register_snippet(TestimonialViewSet)
