from apps.case_studies.models import Testimonial


def public_testimonials():
    return Testimonial.objects.filter(approved_for_publication=True).select_related(
        "logo"
    )
