# TopMap Solutions — agent guide

Read this file before changing the project. Updated 2026-09-25.

## Project purpose

This is TopMap Solutions' public company website: it explains GIS services,
shows project evidence and turns visitor inquiries into sales conversations.
It is a Django monolith with a Wagtail case-study CMS, not an operational GIS
data-processing platform. See README.md and docs/ for setup and architecture.

TopMap serves local and international buyers. Land and property are the lead
sector; utilities and infrastructure are an expanding focus. Keep the broader
GIS positioning while using land projects as current evidence. Never invent
clients, completed utility projects, foreign offices, certifications or results.

## Core features

- Homepage: buyer problems, services, sectors, engagement process and FAQs.
- Service pages: GIS conversion, spatial-data validation and web GIS consulting,
  with inputs, deliverables and scope expectations.
- Inquiries: validated contact form, 24-hour email cooldown, stored Guest records,
  staff/customer notifications and a session-based success page.
- Case studies: Wagtail-managed clients, locations, summaries, challenges,
  solutions, results, tags and image galleries.
- SEO: page metadata, Wagtail SEO fields, canonical URLs, social previews,
  organization structured data, robots.txt and a public-content sitemap.
- Administration: Django admin for inquiries and Wagtail for editorial content.

## Stack and code map

- Python 3.14+, Django 6, Wagtail 7; uv with `pyproject.toml` and `uv.lock`.
- PostgreSQL in development/production; isolated in-memory SQLite for full tests.
- Server-rendered Django templates, plain CSS and JavaScript; no SPA build system.
- Gunicorn, WhiteNoise, Docker/Compose, Vultr; Brevo SMTP and Backblaze B2 media.
- `apps/guests/`: public views, forms, inquiry services/selectors and tests.
- `apps/guests/content.py`: service copy and URL slugs.
- `apps/guests/templates/`, `apps/guests/static/`: public pages and styles.
- `apps/case_studies/`: Wagtail content models, templates and styles.
- `core/`: shared layouts, styles, navigation, SEO helpers and crawl endpoints.
- `config/settings/`: base, development, production and isolated test settings.
- `.docker/`: image and deployment service configuration.
- `.github/workflows/deploy.yml`: test → build → deploy workflow.

Main routes: `/`, `/services/<slug>/`, `/inquiry/`, `/submit/`,
`/inquiry/success/`, `/pages/` (CMS content), `/cms/`, `/not-admin/`,
`/robots.txt` and `/sitemap.xml`.

## Working rules

- Keep changes within the user's request. Preserve unrelated work.
- Do not change models or create, edit, delete or regenerate migration files.
  Do not run migration commands against development or production databases.
- Full tests are authorized to create a disposable test database using existing
  migrations. Use `config.settings.test`, which never loads `.env` files and
  cannot connect to the production database. This supersedes the earlier
  prohibition on migration-backed test setup only for isolated tests.
- Do not expose `.env`, `.env.prod`, `.env.testing` or credentials.
- Do not deploy, submit real inquiries or send real mail while checking changes.
- The Dockerfile's default startup applies migrations. For container tests,
  override its command with `python manage.py test` and select test settings.
- Keep architecture simple. Use existing Django forms, services, templates and
  Wagtail fields before introducing frameworks or infrastructure.
- Use real evidence for business claims. Utilities remain an expanding service
  area unless the owner supplies evidence to update that description.
- Keep canonical URLs aligned with `PUBLIC_SITE_URL`. Preserve published service
  slugs or plan redirects. Do not create fake translations or location pages.

## Tests and commands

All test files belong inside `apps/<app>/tests/` or an app's `tests.py`.
Do not create a root-level `tests/` directory. Let Django discover test modules;
do not import test classes into package `__init__.py` files.

```sh
uv sync --frozen
make test
# Full suite, equivalent command:
uv run python manage.py test --settings=config.settings.test

# Optional quick public-site subset:
make test-ui

# Development server (requires the owner's configured environment):
make run
```

The full suite currently has 34 tests: eight existing model/view tests plus
26 public-site checks in `apps/guests/tests/test_public_site.py`. Full tests use
an in-memory SQLite database and in-memory email/storage. Public-site unit tests
mock CMS/persistence/mail boundaries and isolate their host/session/middleware
settings; the model tests exercise actual database persistence.

`config.settings.test_ui` remains available for the database-free subset.
Neither test settings module imports production settings or reads secret files.
SQLite tests do not verify PostgreSQL-specific behavior, real SMTP, B2 or browser
layout. `make lint` reformats templates; it is not a read-only lint command.

## CI/CD

Pushes and pull requests targeting `main` run the full Django suite inside the
Docker image. Tests must pass before the production build job runs. Deployment
requires a successful build and a push to `main`; pull requests never deploy.

Deployment uses `appleboy/ssh-action@v1.0.3`, the existing `SERVER_IP`,
`SERVER_USER` and `SSH_PRIVATE_KEY` secrets, and the server checkout at
`~/myapps/topmap-solutions-official`. It resets to the tested commit, rebuilds
with Compose and prunes unused images. The CI build validates the image build;
the server rebuilds from the same source rather than pulling a CI artifact.
The simplified deployment does not include an HTTP health check or automatic
rollback. Never report a successful CI run or deployment without observing it.

## Known follow-up work

- Email currently runs before saving the inquiry; an SMTP failure can prevent
  lead persistence. Fix only when that backend work is requested.
- Cooldown is not comprehensive spam protection or concurrency control.
- Real browser/mobile verification and live search indexing require separate checks.
