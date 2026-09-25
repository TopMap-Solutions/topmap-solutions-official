# TopMap Solutions

The public website for **TopMap Solutions** — GIS data conversion, spatial-data
validation and web mapping services for local and international buyers.
Land and property are our core sector, with utilities and infrastructure an
expanding focus.

## Features

- Service pages with clear inputs, deliverables and project inquiries.
- Wagtail case studies with results, tags and image galleries.
- Inquiry management in Django admin, with email notifications.
- Search metadata, social previews, canonical URLs and a sitemap.

## Stack

Python 3.14+ · Django · Wagtail · PostgreSQL · uv · Docker

Server-rendered templates with plain CSS and JavaScript. Production uses
Gunicorn, WhiteNoise, Brevo email and Backblaze B2 media storage.

## Get started

With uv, Python 3.14+ and PostgreSQL installed, open the repository directory:

```sh
uv sync --frozen
cp .env.example .env
```

Set a unique `SECRET_KEY` and your PostgreSQL `DB_*` values in `.env`.
Then follow the [installation guide](docs/installation.md) to create the local
database, initialize it and start the site.

Development email prints to the terminal; Brevo and B2 credentials are only
needed for production. Keep `.env` files out of version control.

## Tests

```sh
make test       # Full Django suite; temporary SQLite database
make test-ui    # Optional database-free public-site checks
```

Tests do not need PostgreSQL, `.env` or external services. CI runs the full suite,
then builds the production image; successful pushes to `main` deploy to Vultr.

## Documentation

- [Installation](docs/installation.md) — environment, local setup and production requirements.
- [Architecture](docs/architecture.md) — components, request flow and deployment.
- [UI and SEO](docs/ui-seo.md) — content editing and verification notes.
- [Agent guide](AGENTS.md) — project context and contributor rules.

Licensed under [Apache 2.0](LICENSE).
