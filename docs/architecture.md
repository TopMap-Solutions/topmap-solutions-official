# Architecture

TopMap is a **Django monolith** for marketing, case studies and lead capture.
It is not the GIS data-processing platform sold through the website.

## Components

| Location | Responsibility |
| --- | --- |
| `apps/guests/` | Homepage, services, inquiry forms, validation, email and lead records |
| `apps/guests/content.py` | Service descriptions and public URL slugs |
| `apps/case_studies/` | Wagtail case-study pages, metrics, tags and galleries |
| `core/` | Shared templates/styles, navigation, SEO and crawl endpoints |
| `config/` | Settings, URLs and WSGI/ASGI entry points |
| `apps/*/tests/` | App-owned tests; no root-level test directory |
| `.docker/` | Production image and Compose configuration |
| `.github/workflows/deploy.yml` | Test → build → deploy pipeline |

## Request flow

Public routes use Django views and server-rendered templates. `/pages/` delegates
to Wagtail; `/cms/` is the editor and `/not-admin/` is Django admin.

An inquiry follows this sequence:

```text
POST /submit/ → validate form → check email cooldown
              → notify staff/customer → save Guest → success redirect
```

Email currently precedes persistence: an SMTP failure can prevent the lead from
being stored. That reliability issue remains open.

Shared metadata uses `PUBLIC_SITE_URL` for canonical URLs. Case-study titles and
descriptions use Wagtail SEO fields with content fallbacks. Navigation and the
sitemap select live, public case studies within the current Wagtail site.

## Environments

| Environment | Database | Email | Media / static files |
| --- | --- | --- | --- |
| Development | PostgreSQL | Console | Local files / Django development server |
| Full tests | Temporary SQLite | In-memory | In-memory media / static file lookup |
| UI-only tests | No database | In-memory | Mocked CMS boundaries / static file lookup |
| Production | PostgreSQL | Brevo SMTP | Backblaze B2 / WhiteNoise |

`manage.py` defaults to development settings; WSGI and production Compose select
production settings. Test settings are independent and never load `.env`.

## Delivery

Pull requests and pushes to `main` run the full Django suite inside Docker.
A successful test job unlocks the production build. Only a successful push to
`main` deploys through SSH to Vultr using `appleboy/ssh-action@v1.0.3`.

The server checks out the tested commit and rebuilds it with Compose. It does
not pull the CI-built image. Startup applies existing migrations, collects static
files and launches Gunicorn. The workflow has no HTTP readiness check or
automatic rollback.
