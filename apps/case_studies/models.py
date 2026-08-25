from django.db import models
from wagtail.fields import RichTextField
from wagtail.models import Page


class CaseStudyIndexPage(Page):
    intro = RichTextField(blank=True)

    parent_page_types = [
        "wagtailcore.Page",
    ]

    subpage_types = [
        "case_studies.CaseStudyPage",
    ]

    content_panels = Page.content_panels + [
        "intro",
    ]


class CaseStudyPage(Page):
    client = models.CharField(max_length=255)
    location = models.CharField(max_length=255, blank=True)
    project_type = models.CharField(max_length=255, blank=True)

    summary = models.TextField()
    challenge = RichTextField()
    solution = RichTextField()
    results = RichTextField()

    parent_page_types = [
        "case_studies.CaseStudyIndexPage",
    ]

    content_panels = Page.content_panels + [
        "client",
        "location",
        "project_type",
        "summary",
        "challenge",
        "solution",
        "results",
    ]