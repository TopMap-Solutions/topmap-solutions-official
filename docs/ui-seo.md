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

## Run checks without migrations

```sh
make test-ui
# Or, with the existing virtual environment:
.venv/bin/python -B -m django test tests --settings=config.settings.test_ui
```

Only the new `tests/` suite is selected. It uses SimpleTestCase and a dummy
backend, so database access fails rather than connecting to a real database.
Settings do not load `.env` files. CMS queries, lead persistence and notifications
are mocked. This covers rendering, routes, form validation, CSRF, metadata,
canonicalization and crawl endpoints, not real database persistence or SMTP.
The new GitHub workflow runs this same suite on pushes and pull requests. It
is separate from the existing deploy workflow; it does not gate deployment.

`make test` retains `uv run manage.py test` and discovers all 34 tests, including
the eight unchanged legacy database tests. Public-site test classes isolate their
hosts, sessions, middleware and storage so they also work under the normal runner.
`make test-ui` selects only the 26 database-free tests. CI uses that target.
Do not execute the full runner or start Docker under the current no-migration
rule: those workflows can apply migrations.

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
