"""Public CMS content scoped to the site serving the request."""
from wagtail.models import Page, Site

from apps.case_studies.models import CaseStudyIndexPage, CaseStudyPage


def case_study_pages(request):
    site = Site.find_for_request(request)
    if site is None:
        return Page.objects.none()
    return (
        Page.objects.descendant_of(site.root_page, inclusive=True)
        .live().public().type(CaseStudyIndexPage, CaseStudyPage).specific()
    )
