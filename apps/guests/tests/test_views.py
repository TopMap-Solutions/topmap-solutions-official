from django.test import TestCase
from django.urls import reverse

from core.decorators import without_manifest_storage


@without_manifest_storage
class HomepageViewTest(TestCase):

    def test_homepage_status_code(self):
        response = self.client.get(reverse("guests:homepage"))

        self.assertEqual(response.status_code, 200)

    def test_homepage_uses_correct_template(self):
        response = self.client.get(reverse("guests:homepage"))

        self.assertTemplateUsed(response, "homepage.html")


@without_manifest_storage
class InquiryPageViewTest(TestCase):

    def test_inquiry_page_status_code(self):
        response = self.client.get(reverse("guests:inquiry"))

        self.assertEqual(response.status_code, 200)

    def test_inquiry_page_uses_correct_template(self):
        response = self.client.get(reverse("guests:inquiry"))

        self.assertTemplateUsed(response, "inquiry.html")
