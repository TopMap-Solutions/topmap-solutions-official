# UI, positioning and SEO changes

TopMap now presents GIS services across sectors, with land as the strongest
current specialty and utilities/infrastructure explicitly marked as an expanding
focus. The public site welcomes international inquiries without asserting a
foreign presence or completed utility projects.

## Editing content

- Homepage and sectors: `apps/guests/templates/homepage.html`.
- Service copy: `apps/guests/content.py`. Its keys determine the service URLs.
  Preserve published slugs or add redirects when changing them.
- Shared metadata: `core/seo.py` and `core/templates/seo_head.html`.
- Case studies: use Wagtail's existing title, SEO title and search description.
  Empty SEO fields fall back to the title and summary/intro.
- Preferred public origin: `PUBLIC_SITE_URL` in base settings, currently
  `https://topmapsolutions.com`. Canonicals and sitemap URLs agree on this origin.
- Sitemap includes static public pages and live, unrestricted case-study pages
  within the Wagtail site serving the request. Confirm the production Wagtail
  Site hostname/root page; an absent site produces static entries only.

The site remains English-language. No placeholder translations, unsupported
hreflang variants, location pages, review ratings or international client claims
were added. International discovery depends on useful content and evidence,
not merely saying “global.”

## Run tests

```sh
make test
# Full native Django discovery, using an isolated in-memory database:
uv run python manage.py test --settings=config.settings.test

# Optional database-free public-site subset:
make test-ui
```

All tests live in their apps. The 26 public-site tests are in
`apps/guests/tests/test_public_site.py`; eight existing model/view tests bring
full discovery to 34 tests. The full suite passes with a temporary SQLite
database created from existing migrations and destroyed after the run. Test
settings never load `.env` files. No model or migration files were changed.
The public-site unit tests mock external/ORM boundaries; existing model tests
exercise database persistence. PostgreSQL-specific behavior and real SMTP/B2
are not verified by this suite.

CI builds a Docker test image and runs `python manage.py test` with
`DJANGO_SETTINGS_MODULE=config.settings.test`. Test success gates the production
build, which gates deployment on pushes to main. Pull requests do not deploy.
The Docker test command overrides the normal production startup command.

## Verification and remaining work

Django checks and the new regression suite pass. No models or migrations changed.
Browser tooling was unavailable in this session; visual checks at 320, 375, 768,
1024 and 1440 pixels remain a release verification step. Check navigation with a
published CMS index, long case-study titles, keyboard focus, error messages,
image cropping and horizontal overflow. No real inquiries were submitted.

The prior email-before-lead-save behavior is outside this UI/SEO pass and still
needs a reliability fix. The current tests do not imply this failure mode is fixed.
Existing deploy startup/cleanup behavior is unchanged; nothing was deployed.

After deployment, verify the public sitemap, robots.txt, canonical links,
apex/www redirect policy and Wagtail-generated case-study URLs. Submit the
sitemap in Search Console and establish a baseline for qualified inquiries and
search impressions. Live indexing and improved rankings are not verified here.

References:
- https://developers.google.com/search/docs/fundamentals/seo-starter-guide
- https://developers.google.com/search/docs/crawling-indexing/consolidate-duplicate-urls
- https://developers.google.com/search/docs/specialty/international/managing-multi-regional-sites
- https://docs.djangoproject.com/en/6.0/topics/testing/tools/#simpletestcase

## SEO and sender audit — 2026-09-25

Read-only HTTP checks found the public HTTPS homepage responding with 200 but
still serving the older generic title, without description or canonical metadata.
`/robots.txt`, `/sitemap.xml`, and `/services/gis-data-conversion/` returned 404.
The www homepage also served 200 without redirecting to the apex; plain HTTP
returned 404. These are live deployment findings, not failures of the current
local route definitions. No deployment was performed.

The local SEO implementation now makes the Philippines base explicit in homepage
metadata while describing international remote collaboration. Organization
JSON-LD identifies the business with a stable canonical ID and country, and
service pages describe their actual services with linked provider JSON-LD.
Social image URLs use Django static storage so collected filenames and external
static hosts are respected. Public pages allow large image previews; drafts,
previews, submission responses and success pages remain non-indexable. Existing
canonical URLs, service slugs and public-only sitemap filtering are preserved.
No invented offices, ratings, translations or client evidence were added.

Inquiry staff notifications and customer confirmations now set both From and
Reply-To to `joshdels@topmapsolutions.com`. SMTP authentication credentials remain
unchanged. Brevo domain authentication and sender authorization must be verified
in the owner's Brevo account; local in-memory tests do not prove delivery.
See https://help.brevo.com/hc/en-us/articles/7924908994450-Send-transactional-emails-using-Brevo-SMTP.

Before claiming these changes are public, deploy through the existing approved
release process, then verify 200 responses for each sitemap URL, canonical and
social tags, public image access, and HTTP/www redirect policy at the proxy.
Submit the sitemap and inspect representative URLs in Google Search Console.
Crawl eligibility is not a guarantee of indexing or ranking:
https://developers.google.com/search/docs/essentials/technical.

Run the database-free SEO, public-site and sender checks without migrations:

```sh
uv run python manage.py test apps.guests.tests.test_public_site apps.guests.tests.test_seo_email --settings=config.settings.test_ui
```
