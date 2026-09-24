"""No database, migrations, external storage or SMTP. ORM boundaries are mocked."""
from datetime import datetime, timezone
from html.parser import HTMLParser
from types import SimpleNamespace
from unittest.mock import patch
from xml.etree import ElementTree
import json

from django.contrib.staticfiles import finders
from django.template.loader import render_to_string
from django.test import Client, RequestFactory, SimpleTestCase, override_settings
from django.urls import resolve, reverse
from django.utils.html import escape

from apps.guests.content import SERVICES
from apps.guests.forms import InquiryForm
from core.public_pages import case_study_pages
from core.seo import metadata


class Document(HTMLParser):
    def __init__(self, html):
        super().__init__()
        self.tags = []
        self.feed(html)

    def handle_starttag(self, tag, attrs):
        self.tags.append((tag, dict(attrs)))

    def attributes(self, tag):
        return [attrs for name, attrs in self.tags if name == tag]


@override_settings(
    ALLOWED_HOSTS=["testserver", "localhost", "127.0.0.1", "www.topmapsolutions.com"],
    SESSION_ENGINE="django.contrib.sessions.backends.signed_cookies",
    PUBLIC_SITE_URL="https://topmapsolutions.com",
    SECURE_SSL_REDIRECT=False,
    STORAGES={
        "default": {"BACKEND": "django.core.files.storage.InMemoryStorage"},
        "staticfiles": {"BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage"},
    },
    MIDDLEWARE=[
        "django.middleware.security.SecurityMiddleware",
        "django.contrib.sessions.middleware.SessionMiddleware",
        "django.middleware.common.CommonMiddleware",
        "django.middleware.csrf.CsrfViewMiddleware",
        "django.contrib.auth.middleware.AuthenticationMiddleware",
        "django.contrib.messages.middleware.MessageMiddleware",
    ],
)
class PublicSiteTestCase(SimpleTestCase):
    """Keep these unit tests database-free even under the normal project runner.

    Cookie sessions avoid session-table writes. Database-backed Wagtail redirect
    middleware is outside these tests; CMS query boundaries are mocked explicitly.
    Host and storage overrides belong to tests, not development/production settings.
    """


class PublicSiteTests(PublicSiteTestCase):
    def setUp(self):
        self.navigation = patch("core.context_processors.case_study_pages")
        self.navigation_mock = self.navigation.start()
        self.navigation_mock.return_value.type.return_value.first.return_value = None
        self.addCleanup(self.navigation.stop)
        self.payload = {"name": "Alex Example", "email": "alex@example.com", "organization": "Example team", "phone": "+44 1234 567890", "inquiry": "We need to map utility assets."}

    def test_homepage_positions_both_sectors_without_claiming_utility_clients(self):
        response = self.client.get("/")
        for copy in ("Make your spatial data work", "Land &amp; property", "Utilities &amp; infrastructure", "Expanding focus", "international inquiries"):
            self.assertContains(response, copy)
        self.assertNotContains(response, 'href=""')
        self.assertNotContains(response, "homepage.js")

    def test_every_service_has_buying_details_and_consistent_metadata(self):
        titles = set()
        for slug, service in SERVICES.items():
            with self.subTest(slug=slug):
                response = self.client.get(reverse("guests:service_detail", kwargs={"slug": slug}))
                self.assertContains(response, escape(service["headline"]))
                self.assertContains(response, "What we start with")
                self.assertContains(response, "What we scope together")
                self.assertContains(response, "Discuss your GIS project")
                doc = Document(response.content.decode())
                metas = doc.attributes("meta")
                title = next(x["content"] for x in metas if x.get("property") == "og:title")
                titles.add(title)
                self.assertIn(service["title"], title)
                self.assertIn({"name": "description", "content": service["description"]}, metas)
        self.assertEqual(len(titles), len(SERVICES))

    def test_canonical_drops_tracking_queries_and_www_host(self):
        response = self.client.get("/?utm_source=campaign", HTTP_HOST="www.topmapsolutions.com")
        doc = Document(response.content.decode())
        self.assertIn({"rel": "canonical", "href": "https://topmapsolutions.com/"}, doc.attributes("link"))
        self.assertIn({"property": "og:url", "content": "https://topmapsolutions.com/"}, doc.attributes("meta"))

    def test_semantic_landmarks_and_assets_on_public_pages(self):
        urls = ["/", "/inquiry/"] + [f"/services/{slug}/" for slug in SERVICES]
        for url in urls:
            with self.subTest(url=url):
                response = self.client.get(url)
                doc = Document(response.content.decode())
                self.assertEqual(len(doc.attributes("main")), 1)
                self.assertEqual(len(doc.attributes("h1")), 1)
                self.assertEqual(len(doc.attributes("title")), 1)
                self.assertContains(response, 'href="#main-content"')
                for tag, attrs in doc.tags:
                    source = attrs.get("src", attrs.get("href", ""))
                    if source.startswith("/static/"):
                        self.assertIsNotNone(finders.find(source.removeprefix("/static/")), source)
                    if tag == "img":
                        self.assertIn("alt", attrs)

    def test_organization_json_is_valid_and_has_no_invented_ratings(self):
        response = self.client.get("/")
        html = response.content.decode()
        schema = json.loads(html.split('<script type="application/ld+json">')[1].split('</script>')[0])
        self.assertEqual(schema["@type"], "Organization")
        self.assertEqual(schema["url"], "https://topmapsolutions.com/")
        self.assertNotIn("aggregateRating", schema)

    def test_unknown_service_is_a_real_noindex_404(self):
        response = self.client.get("/services/not-a-service/")
        self.assertEqual(response.status_code, 404)
        self.assertContains(response, 'content="noindex, follow"', status_code=404)

    def test_valid_service_links_resolve(self):
        doc = Document(self.client.get("/").content.decode())
        for attrs in doc.attributes("a"):
            href = attrs.get("href", "")
            if href.startswith("/"):
                self.assertIsNotNone(resolve(href.split("#")[0]))

    def test_inquiry_has_accessible_labels_and_international_phone_input(self):
        response = self.client.get("/inquiry/")
        doc = Document(response.content.decode())
        ids = {attrs["id"] for _, attrs in doc.tags if "id" in attrs}
        for attrs in doc.attributes("label"):
            self.assertIn(attrs["for"], ids)
        phone = next(attrs for attrs in doc.attributes("input") if attrs.get("name") == "phone")
        self.assertEqual(phone["type"], "tel")
        self.assertNotIn("minlength", phone)
        self.assertContains(response, "country code")

    @patch("apps.guests.views.inquiry.send_inquiry_emails")
    @patch("apps.guests.views.inquiry.Guest.objects.create")
    def test_invalid_submission_preserves_data_and_explains_errors(self, create, send):
        response = self.client.post("/submit/", {**self.payload, "email": "invalid"})
        self.assertContains(response, "Enter a valid email address")
        self.assertContains(response, 'value="Alex Example"')
        self.assertContains(response, 'value="invalid"')
        self.assertContains(response, self.payload["inquiry"])
        self.assertContains(response, 'aria-invalid="true"')
        self.assertContains(response, 'aria-describedby="id_email_error"')
        self.assertContains(response, 'content="noindex, follow"')
        self.assertContains(response, 'href="https://topmapsolutions.com/inquiry/"')
        create.assert_not_called()
        send.assert_not_called()

    @patch("apps.guests.views.inquiry.send_inquiry_emails")
    @patch("apps.guests.views.inquiry.Guest.objects.create")
    @patch("apps.guests.views.inquiry.check_email_cooldown", return_value=True)
    def test_cooldown_is_visible_and_retains_values(self, cooldown, create, send):
        response = self.client.post("/submit/", self.payload)
        self.assertContains(response, "within the last 24 hours")
        self.assertContains(response, 'value="alex@example.com"')
        create.assert_not_called()
        send.assert_not_called()

    @patch("apps.guests.views.inquiry.send_inquiry_emails")
    @patch("apps.guests.views.inquiry.Guest.objects.create")
    @patch("apps.guests.views.inquiry.check_email_cooldown", return_value=False)
    def test_successful_submission_and_single_use_success_page(self, cooldown, create, send):
        response = self.client.post("/submit/", self.payload)
        self.assertRedirects(response, "/inquiry/success/", fetch_redirect_response=False)
        create.assert_called_once_with(**self.payload)
        send.assert_called_once_with(self.payload)
        success = self.client.get("/inquiry/success/")
        self.assertContains(success, "alex@example.com")
        self.assertContains(success, 'content="noindex, follow"')
        self.assertRedirects(self.client.get("/inquiry/success/"), "/inquiry/", fetch_redirect_response=False)

    def test_csrf_rejects_forged_submission(self):
        client = Client(enforce_csrf_checks=True)
        self.assertEqual(client.post("/submit/", self.payload).status_code, 403)

    def test_get_submit_and_direct_success_redirect(self):
        for url in ("/submit/", "/inquiry/success/"):
            self.assertRedirects(self.client.get(url), "/inquiry/", fetch_redirect_response=False)

    def test_form_fragment_is_populated_and_not_indexable(self):
        response = self.client.get("/inquiry/form/")
        self.assertContains(response, 'name="email"')
        self.assertEqual(response["X-Robots-Tag"], "noindex, follow")

    def test_user_content_is_escaped_in_form(self):
        response = self.client.post("/submit/", {**self.payload, "email": "invalid", "name": '<script>alert(1)</script>'})
        self.assertNotContains(response, '<script>alert(1)</script>')
        self.assertContains(response, '&lt;script&gt;')

    def test_optional_fields_and_global_phone_are_accepted(self):
        form = InquiryForm({**self.payload, "organization": "", "phone": "+81 (0)3 1234-5678"})
        self.assertTrue(form.is_valid(), form.errors)

    def test_published_case_study_link_appears(self):
        self.navigation_mock.return_value.type.return_value.first.return_value = SimpleNamespace(url="/pages/work/")
        response = self.client.get("/")
        self.assertContains(response, 'href="/pages/work/"')


class CrawlTests(PublicSiteTestCase):
    @patch("core.views.case_study_pages", return_value=[])
    def test_sitemap_contains_all_public_service_pages_and_no_action_routes(self, pages):
        response = self.client.get("/sitemap.xml", HTTP_HOST="www.topmapsolutions.com")
        self.assertEqual(response.status_code, 200)
        tree = ElementTree.fromstring(response.content)
        urls = [node.text for node in tree.findall("{*}url/{*}loc")]
        expected = {"https://topmapsolutions.com/", "https://topmapsolutions.com/inquiry/"}
        expected |= {f"https://topmapsolutions.com/services/{slug}/" for slug in SERVICES}
        self.assertEqual(set(urls), expected)

    @patch("core.views.case_study_pages")
    def test_sitemap_includes_cms_urls_and_publication_dates(self, pages):
        page = SimpleNamespace(get_url=lambda **kw: "https://www.topmapsolutions.com/pages/work/example/", last_published_at=datetime(2026, 9, 24, tzinfo=timezone.utc))
        pages.return_value = [page, page, SimpleNamespace(get_url=lambda **kw: None)]
        response = self.client.get("/sitemap.xml")
        self.assertContains(response, "https://topmapsolutions.com/pages/work/example/", count=1)
        self.assertContains(response, "<lastmod>2026-09-24</lastmod>")

    def test_robots_advertises_canonical_sitemap_without_blocking_assets(self):
        response = self.client.get("/robots.txt")
        self.assertContains(response, "Sitemap: https://topmapsolutions.com/sitemap.xml")
        self.assertNotContains(response, "Disallow: /static/")
        self.assertNotContains(response, "Disallow: /inquiry/")

    def test_crawl_endpoints_reject_post(self):
        for url in ("/robots.txt", "/sitemap.xml"):
            self.assertEqual(self.client.post(url).status_code, 405)

    @patch("core.public_pages.Page")
    @patch("core.public_pages.Site.find_for_request")
    def test_cms_query_requires_live_public_pages_in_current_site(self, site, page_model):
        site.return_value = SimpleNamespace(root_page="root")
        descendants = page_model.objects.descendant_of.return_value
        case_study_pages(RequestFactory().get("/"))
        page_model.objects.descendant_of.assert_called_once_with("root", inclusive=True)
        descendants.live.assert_called_once_with()
        descendants.live.return_value.public.assert_called_once_with()
        descendants.live.return_value.public.return_value.type.assert_called_once()

    @patch("core.public_pages.Page")
    @patch("core.public_pages.Site.find_for_request", return_value=None)
    def test_no_cms_site_yields_no_pages(self, site, page_model):
        case_study_pages(RequestFactory().get("/"))
        page_model.objects.none.assert_called_once()


class CMSMetadataTests(PublicSiteTestCase):
    def setUp(self):
        self.request = RequestFactory().get("/pages/work/example/?utm_source=test")
        self.page = SimpleNamespace(seo_title="A specific GIS project", title="Project example", search_description="A useful project description.", summary="Fallback summary", get_url=lambda **kwargs: "/pages/work/example/")

    def test_editor_seo_fields_are_used(self):
        result = metadata(self.request, self.page)
        self.assertEqual(result["title"], "A specific GIS project | TopMap Solutions")
        self.assertEqual(result["description"], self.page.search_description)
        self.assertEqual(result["canonical"], "https://topmapsolutions.com/pages/work/example/")

    def test_fallback_and_preview_noindex(self):
        self.page.seo_title = ""
        self.page.search_description = ""
        self.request.is_preview = True
        result = metadata(self.request, self.page)
        self.assertEqual(result["title"], "Project example | TopMap Solutions")
        self.assertEqual(result["description"], "Fallback summary")
        self.assertTrue(result["noindex"])

    @patch("core.context_processors.case_study_pages")
    def test_case_study_without_results_still_has_cta_and_single_main(self, navigation):
        navigation.return_value.type.return_value.first.return_value = None
        empty = SimpleNamespace(all=lambda: [])
        self.page.get_parent = lambda: None
        self.page.tags = self.page.gallery_images = self.page.results = empty
        self.page.client = "Example client"
        self.page.location = ""
        self.page.challenge = "<p>Disconnected records.</p>"
        self.page.solution = "<p>Structured GIS layers.</p>"
        html = render_to_string("case_studies/case_study_page.html", {"page": self.page}, request=self.request)
        doc = Document(html)
        self.assertEqual(len(doc.attributes("main")), 1)
        self.assertEqual(len(doc.attributes("h1")), 1)
        self.assertIn("Discuss your GIS project", html)
        self.assertIn("A specific GIS project | TopMap Solutions", html)
