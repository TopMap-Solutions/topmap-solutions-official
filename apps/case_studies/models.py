from django.db import models

from modelcluster.contrib.taggit import ClusterTaggableManager
from modelcluster.fields import ParentalKey

from taggit.models import ItemBase, TagBase

from wagtail.admin.panels import InlinePanel
from wagtail.fields import RichTextField
from wagtail.images import get_image_model_string
from wagtail.models import Page, Orderable


class CaseStudyIndexPage(Page):
    intro = RichTextField(blank=True)
    parent_page_types = ["wagtailcore.Page"]
    subpage_types = ["case_studies.CaseStudyPage"]
    content_panels = Page.content_panels + ["intro"]


class CaseStudyPage(Page):

    client = models.CharField(max_length=255)

    location = models.CharField(
        max_length=255,
        blank=True,
    )

    created_on = models.DateField(
        auto_now_add=True,
    )

    summary = models.TextField()
    challenge = RichTextField()
    solution = RichTextField()

    tags = ClusterTaggableManager(
        through="case_studies.CaseStudyPageTag",
        blank=True,
    )

    parent_page_types = ["case_studies.CaseStudyIndexPage"]

    content_panels = Page.content_panels + [
        "client",
        "location",
        "summary",
        "challenge",
        "solution",
        "tags",
        InlinePanel(
            "results",
            label="Results",
            heading="Project results",
            help_text=("Add key metrics or outcomes from the project."),
        ),
        InlinePanel(
            "gallery_images",
            label="Project images",
            heading="Project gallery",
            help_text=(
                "Add images showing the project, workflow, " "maps, or results."
            ),
        ),
    ]


class CaseStudyResult(Orderable):

    page = ParentalKey(
        "case_studies.CaseStudyPage",
        on_delete=models.CASCADE,
        related_name="results",
    )

    value = models.CharField(
        max_length=100,
        help_text="Example: 60,000+, 80%, 3x, ₱2.5M",
    )

    label = models.CharField(
        max_length=255,
        help_text="Example: Parcels converted",
    )

    description = models.CharField(
        max_length=255,
        blank=True,
        help_text="Optional supporting text.",
    )

    panels = [
        "value",
        "label",
        "description",
    ]


class CaseStudyTag(TagBase):

    class Meta:
        verbose_name = "Case study tag"
        verbose_name_plural = "Case study tags"


class CaseStudyPageTag(ItemBase):

    tag = models.ForeignKey(
        CaseStudyTag,
        related_name="case_study_pages",
        on_delete=models.CASCADE,
    )

    content_object = ParentalKey(
        "case_studies.CaseStudyPage",
        related_name="tagged_items",
        on_delete=models.CASCADE,
    )


class CaseStudyImage(Orderable):

    page = ParentalKey(
        "case_studies.CaseStudyPage",
        on_delete=models.CASCADE,
        related_name="gallery_images",
    )

    image = models.ForeignKey(
        get_image_model_string(),
        on_delete=models.CASCADE,
        related_name="+",
    )

    caption = models.CharField(
        max_length=255,
        blank=True,
    )

    panels = [
        "image",
        "caption",
    ]
