import base64

from django.core.files.base import ContentFile
from django.test import TestCase, override_settings
from wagtail.images import get_image_model

from apps.case_studies.models import Testimonial
from apps.case_studies.selectors import public_testimonials


class TestimonialModelTests(TestCase):
    def test_testimonial_is_hidden_by_default_and_uses_organization_fallback(self):
        testimonial = Testimonial.objects.create(
            quote="A useful project outcome.",
            organization="Example Organization",
        )

        self.assertFalse(testimonial.approved_for_publication)
        self.assertEqual(str(testimonial), "Example Organization")
        self.assertNotIn(testimonial, public_testimonials())

    def test_public_selector_filters_and_orders_testimonials(self):
        second = Testimonial.objects.create(
            quote="Second",
            name="Second Person",
            organization="Second Organization",
            approved_for_publication=True,
            display_order=20,
        )
        first = Testimonial.objects.create(
            quote="First",
            organization="First Organization",
            approved_for_publication=True,
            display_order=10,
        )
        Testimonial.objects.create(
            quote="Private",
            organization="Private Organization",
            display_order=0,
        )

        self.assertEqual(list(public_testimonials()), [first, second])
        self.assertEqual(str(second), "Second Person")


@override_settings(
    ALLOWED_HOSTS=["testserver"],
    STORAGES={
        "default": {"BACKEND": "django.core.files.storage.InMemoryStorage"},
        "staticfiles": {
            "BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage"
        },
    },
)
class TestimonialHomepageTests(TestCase):
    def test_homepage_renders_an_optional_logo(self):
        gif = base64.b64decode(
            "R0lGODlhAQABAIAAAAAAAP///ywAAAAAAQABAAACAUwAOw=="
        )
        logo = get_image_model().objects.create(
            title="Example logo",
            file=ContentFile(gif, name="example.gif"),
        )
        Testimonial.objects.create(
            quote="The interactive map is easy to share.",
            organization="Example Organization",
            logo=logo,
            approved_for_publication=True,
        )

        response = self.client.get("/")

        self.assertContains(response, 'class="testimonial-logo"')
        self.assertContains(response, 'alt="Example Organization logo"')

# Create your tests here.
