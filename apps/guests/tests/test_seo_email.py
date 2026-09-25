"""SEO and email regressions without database access or real SMTP delivery."""
import json
from types import SimpleNamespace
from unittest.mock import patch

from django.core import mail
from django.test import RequestFactory, SimpleTestCase, override_settings
from django.urls import resolve

from apps.guests.content import SERVICES
from apps.guests.services.inquiry_services import send_inquiry_emails
from core.seo import metadata, public_static_url
from core.templatetags.seo_tags import seo_head


@override_settings(
    PUBLIC_SITE_URL="https://topmapsolutions.com",
    STORAGES={"staticfiles": {"BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage"}},
    STATIC_URL="/static/",
)
class SEORegressionTests(SimpleTestCase):
    def request(self, path):
        request = RequestFactory().get(path)
        request.resolver_match = resolve(request.path)
        return request

    def test_homepage_explains_location_and_international_collaboration(self):
        data = seo_head({"request": self.request("/")})
        self.assertIn("Philippines", data["title"])
        self.assertIn("international", data["description"])
        self.assertFalse(data["noindex"])
        organization = json.loads(data["organization_json"])
        self.assertEqual(organization["address"]["addressCountry"], "PH")
        self.assertEqual(organization["@id"], data["home"] + "#organization")
        self.assertIsNone(data["service_json"])

    def test_service_schema_matches_visible_content_and_canonical(self):
        for slug, service in SERVICES.items():
            with self.subTest(slug=slug):
                data = seo_head({"request": self.request(f"/services/{slug}/?utm_source=test")})
                schema = json.loads(data["service_json"])
                self.assertEqual(schema["@type"], "Service")
                self.assertEqual(schema["name"], service["name"])
                self.assertEqual(schema["description"], service["description"])
                self.assertEqual(schema["url"], f"https://topmapsolutions.com/services/{slug}/")
                self.assertEqual(schema["provider"]["@id"], "https://topmapsolutions.com/#organization")
                self.assertFalse(data["noindex"])

    @override_settings(PUBLIC_SITE_URL="https://example.com")
    def test_schema_and_canonical_follow_configured_public_origin(self):
        data = seo_head({"request": self.request("/services/gis-data-conversion/")})
        self.assertEqual(data["canonical"], "https://example.com/services/gis-data-conversion/")
        self.assertEqual(json.loads(data["service_json"])["provider"]["@id"], "https://example.com/#organization")
        self.assertEqual(data["image"], "https://example.com/static/images/city-planning.jpg")

    @patch("core.seo.static", return_value="https://cdn.example.com/city-planning.abc123.jpg")
    def test_social_image_preserves_collected_filename_and_cdn_origin(self, static):
        self.assertEqual(public_static_url("images/city-planning.jpg"), "https://cdn.example.com/city-planning.abc123.jpg")
        static.assert_called_once_with("images/city-planning.jpg")

    def test_draft_cms_content_is_not_indexable(self):
        page = SimpleNamespace(
            seo_title="Draft", title="Draft", search_description="A draft.\n More detail.",
            live=False, get_url=lambda **kwargs: "/pages/draft/",
        )
        data = metadata(RequestFactory().get("/pages/draft/"), page)
        self.assertTrue(data["noindex"])
        self.assertEqual(data["description"], "A draft. More detail.")

    def test_service_json_cannot_close_script_element(self):
        service = {**SERVICES["gis-data-conversion"], "description": "</script><script>alert(1)</script>"}
        with patch.dict(SERVICES, {"gis-data-conversion": service}):
            data = seo_head({"request": self.request("/services/gis-data-conversion/")})
        self.assertNotIn("<", data["service_json"])
        self.assertEqual(json.loads(data["service_json"])["description"], service["description"])


@override_settings(EMAIL_BACKEND="django.core.mail.backends.locmem.EmailBackend")
class InquiryEmailTests(SimpleTestCase):
    def test_notification_and_confirmation_use_joshdels_sender_and_reply_to(self):
        send_inquiry_emails({
            "name": "Example", "email": "customer@example.com", "organization": "Example team",
            "phone": "", "inquiry": "Please discuss a GIS project.",
        })
        self.assertEqual(len(mail.outbox), 2)
        staff, customer = mail.outbox
        self.assertEqual(staff.to, ["joshdels@topmapsolutions.com"])
        self.assertEqual(customer.to, ["customer@example.com"])
        self.assertEqual(customer.alternatives[0].mimetype, "text/html")
        for message in mail.outbox:
            self.assertEqual(message.from_email, "joshdels@topmapsolutions.com")
            self.assertEqual(message.reply_to, ["joshdels@topmapsolutions.com"])
            self.assertEqual(message.message()["Reply-To"], "joshdels@topmapsolutions.com")
            self.assertNotIn("noreply@", message.message().as_string())
