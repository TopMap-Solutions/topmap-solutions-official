from apps.case_studies.models import CaseStudyIndexPage
from core.public_pages import case_study_pages


def navigation(request):
    # Resolve published navigation on each request so unpublishing is reflected immediately.
    return {"case_studies": case_study_pages(request).type(CaseStudyIndexPage).first()}
