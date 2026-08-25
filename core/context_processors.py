from apps.case_studies.models import CaseStudyIndexPage


def navigation(request):
    return {
        "case_studies": CaseStudyIndexPage.objects.live().first(),
    }
