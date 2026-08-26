from django.core.cache import cache
from apps.case_studies.models import CaseStudyIndexPage


def navigation(request):
    return {
        "case_studies": cache.get_or_set(
            "navigation_case_studies",
            lambda: CaseStudyIndexPage.objects.live().first(),
            60 * 60 * 24,
        ),
    }
