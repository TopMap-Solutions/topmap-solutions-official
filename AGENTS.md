# TopMap Solutions — agent guide

Read this file before changing the project. Updated 2026-10-05.

## Project purpose

This is TopMap Solutions' public company website.

Its job is to:

1. Explain TopMap's land and property GIS services.
2. Show evidence through case studies and live interactive maps.
3. Turn visitors and prospects into sales conversations.

It is a Django monolith with a Wagtail case-study CMS and a lightweight public
interactive-map showcase.

It is NOT the operational CAD/GIS data-processing platform sold through the
website.

CAD conversion, georeferencing, geometry repair, parcel parsing, production GIS
processing and client-specific data pipelines remain outside this public website
unless explicitly requested otherwise.

See README.md and docs/ for setup and architecture.

## Business positioning

TopMap currently focuses on LAND AND PROPERTY.

There are two primary customer segments:

### Public sector — LGU land and parcel systems

TopMap helps LGUs improve the flow of parcel information between offices such as
the Assessor and City/Municipal Planning.

Current evidence includes workflows around:

- Assessor CAD parcel data
- standardized/georeferenced parcel information
- GIS-ready handoff to Planning
- centralized parcel databases
- browser-based parcel maps
- land-related planning and analysis workflows

The positioning is not to force Assessor staff to replace AutoCAD with GIS.
Where appropriate, existing CAD workflows can remain while parcel information is
standardized for downstream GIS use.

### Private sector — masterplans and land development

TopMap helps planning, land-development, surveying/geodetic and related firms
turn existing masterplan and site drawings into interactive maps that clients can
open in a browser or on a phone.

The current offer is centered on:

Masterplan/site drawing → prepared spatial data → interactive client map

Do not imply that TopMap designs masterplans, performs licensed surveying,
architecture or engineering work unless supported by actual project scope and
evidence.

Utilities and infrastructure are not a primary marketing focus at this stage.
Do not add or expand utility-specific positioning unless explicitly requested by
the owner.

## Core features

- Homepage: buyer problems, services, sectors, engagement process and FAQs.
- Service pages: land/property GIS services, GIS conversion, spatial-data
  validation and WebGIS consulting.
- Inquiries: validated contact form, 24-hour email cooldown, stored Guest records,
  staff/customer notifications and a session-based success page.
- Case studies: Wagtail-managed clients, locations, summaries, challenges,
  solutions, results, tags and image galleries.
- Testimonials: client-approved Wagtail-managed endorsements presented on the
  homepage as a progressively growing, horizontally scrollable collection.
- Interactive maps: public, permission-based MapLibre showcases of completed or
  prepared map outputs.
- SEO: page metadata, Wagtail SEO fields, canonical URLs, social previews,
  organization structured data, robots.txt and a public-content sitemap.
- Administration: Django admin for inquiries/map configuration and Wagtail for
  editorial content.

## Application boundaries

The public website MAY:

- display approved interactive maps;
- reference already-prepared map data;
- store presentation/configuration metadata;
- provide project and organization pages;
- show client-approved public project information;
- connect maps to case studies and inquiry CTAs.

The public website MUST NOT become a general GIS processing platform by default.

Do not introduce, unless explicitly requested:

- DWG/DXF conversion pipelines;
- automatic CAD parsing;
- CRS detection/reprojection pipelines;
- polygonization;
- geometry repair systems;
- arbitrary GIS upload-and-processing workflows;
- background geoprocessing infrastructure;
- client GIS editing systems;
- general-purpose GIS SaaS functionality.

The default principle is:

Prepared GIS output → public website → interactive presentation

not:

Raw CAD/GIS upload → public website → production GIS processing

## Stack and code map

- Python 3.14+, Django 6, Wagtail 7; uv with `pyproject.toml` and `uv.lock`.
- PostgreSQL in development/production; isolated SQLite for tests where supported.
- Server-rendered Django templates, plain CSS and JavaScript; no SPA build system.
- MapLibre GL JS for interactive public maps.
- Gunicorn, WhiteNoise, Docker/Compose, Vultr.
- Brevo SMTP and Backblaze B2 media/storage.

Applications:

- `apps/guests/`
  Public marketing views, forms, inquiry services/selectors and tests.

- `apps/guests/content.py`
  Service copy and public URL slugs.

- `apps/case_studies/`
  Wagtail case-study models, templates and styles, plus related editorial proof
  such as testimonials. See `apps/case_studies/AGENTS.md` before changing this
  app.

- `apps/maps/`
  Public interactive-map showcases.
  See `apps/maps/AGENTS.md` before changing this app.

- `core/`
  Shared layouts, styles, navigation, SEO helpers and crawl endpoints.

- `config/settings/`
  Base, development, production and isolated test settings.

- `.docker/`
  Image and deployment service configuration.

- `.github/workflows/deploy.yml`
  Test → build → deploy workflow.

## Public routes

Existing routes include:

- `/`
- `/services/<slug>/`
- `/inquiry/`
- `/submit/`
- `/inquiry/success/`
- `/pages/`
- `/cms/`
- `/not-admin/`
- `/robots.txt`
- `/sitemap.xml`

Interactive-map routes belong under:

- `/maps/`
- `/maps/<organization-slug>/`
- `/maps/<organization-slug>/<project-slug>/`

Do not change existing published URLs without preserving compatibility or adding
an appropriate redirect.

## Interactive-map philosophy

Interactive maps are primarily proof and presentation.

Their purpose is to let a prospect or authorized viewer understand what an
existing land/masterplan drawing can become.

Keep the viewer focused.

Typical useful capabilities include:

- pan and zoom;
- readable labels;
- feature selection/popups;
- legend/layer visibility;
- mobile-friendly interaction;
- optional search;
- optional browser geolocation where appropriate;
- organization/project branding.

Do not turn every map into a dashboard.

New functionality should be driven by demonstrated project requirements rather
than speculative platform development.

## Public-data and client-permission rules

Never assume a supplied client file may be published.

A map must not be made publicly discoverable merely because its source file was
provided to TopMap.

Public showcases require explicit owner/client authorization appropriate to the
project.

Do not expose:

- confidential project information;
- credentials or internal URLs;
- personal information;
- private ownership information without authorization;
- sensitive engineering or infrastructure information;
- source files that were not approved for public distribution.

Use real evidence for business claims.

Never invent clients, projects, results, locations, certifications, partnerships,
foreign offices or performance metrics.

Testimonials are public claims. Store and display only wording, attribution and
logos that TopMap has permission to publish. New testimonial records must remain
hidden from the public site until that approval is explicitly recorded in the
CMS.

## Working rules

- Keep changes within the user's request.
- Preserve unrelated work.
- Read a nested `AGENTS.md` before modifying files within its scope.
- Prefer the simplest architecture that satisfies the current requirement.
- Reuse existing Django patterns before adding frameworks or infrastructure.
- Do not introduce React, Next.js or another frontend framework merely for maps.
- Use MapLibre with the existing server-rendered Django architecture unless a
  concrete requirement justifies otherwise.
- Do not expose `.env`, `.env.prod`, `.env.testing` or credentials.
- Do not deploy, submit real inquiries or send real mail while checking changes.
- Keep canonical URLs aligned with `PUBLIC_SITE_URL`.
- Preserve published service slugs or plan redirects.
- Do not create fake translations or location pages.

## Models and migrations

Do not casually change existing models or migrations.

Existing migration history must not be edited, deleted or regenerated.

If a requested feature genuinely requires a new model or model field, first
identify the required schema change and follow the owner's migration instructions.

Do not run migration commands against development or production databases unless
explicitly authorized.

Full tests may create a disposable test database using existing migrations and
`config.settings.test`.

## Tests and commands

All test files belong inside:

`apps/<app>/tests/`

or an app's `tests.py`.

Do not create a root-level `tests/` directory.

Let Django discover test modules. Do not import test classes into package
`__init__.py` files.

```sh
uv sync --frozen

make test

# Equivalent full suite
uv run python manage.py test --settings=config.settings.test

# Optional quick public-site subset
make test-ui

# Development server
make run
```
