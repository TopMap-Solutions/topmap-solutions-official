# Installation

## Requirements

Install **uv**, **Python 3.14+** and a running **PostgreSQL** server. Clone this
repository and open its directory. PostGIS/GDAL and Node.js are not required.

## 1. Install dependencies and configure the environment

```sh
uv sync --frozen
cp .env.example .env
uv run python -c 'from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())'
```

Paste the generated key into `SECRET_KEY` in `.env`. Replace the example database
values with your local database credentials:

| Variable | Local value |
| --- | --- |
| `SECRET_KEY` | The generated key |
| `DB_NAME` | Your database name, e.g. `topmap` |
| `DB_USER` | Your PostgreSQL role, e.g. `topmap` |
| `DB_PASSWORD` | That role's password |
| `DB_HOST` | `localhost` |
| `DB_PORT` | `5432` |

Leave the `BREVO_*` and `B2_*` placeholders for local development: development
settings use console email and local media. `WEBSITE_EMAIL` is currently unused;
notification addresses are defined in the inquiry email service.

## 2. Create a local database

Using a PostgreSQL administrator account, create the role and database. For
Linux installations with a `postgres` system account:

```sh
sudo -u postgres createuser --pwprompt topmap
sudo -u postgres createdb --owner=topmap topmap
```

Use the password you entered as `DB_PASSWORD`. If your role/database already
exist, use their details instead.

## 3. Initialize and run

On your new local database, apply the existing migrations and create an admin:

```sh
uv run python manage.py migrate
uv run python manage.py createsuperuser
uv run python manage.py runserver
```

These are setup instructions for the developer; documentation updates do not
execute them. Use `migrate` directly for installation: `make migrate` also
**generates** migrations and is not needed for a fresh checkout.

Open `http://127.0.0.1:8000/`. Manage inquiries at `/not-admin/` and content at
`/cms/`. In Wagtail, check the Site hostname, port and root page, then create and
publish a case-study index and its child case studies. The navigation link
appears when a public index exists within that site's page tree.

## Tests and production

Run `make test` for the full suite or `make test-ui` for the public-site subset.
Both use isolated settings without reading `.env`; the full suite initializes
and destroys a temporary SQLite test database.

Production Compose loads `.env.prod` and selects `config.settings.prod`.
Start from `.env.example`, replace all credentials, and supply working Brevo and
B2 settings. The server also needs PostgreSQL reachable through the existing
`gis_centralize_db` Docker network and an HTTPS reverse proxy forwarding to port
8000. `.env.prod` is loaded by Compose, not automatically by Django.

CI deployment expects `SERVER_IP`, `SERVER_USER` and `SSH_PRIVATE_KEY` repository
secrets and a server checkout at `~/myapps/topmap-solutions-official`. Container
startup applies migrations and collects static files before starting Gunicorn.
