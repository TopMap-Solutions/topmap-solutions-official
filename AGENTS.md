# TopMap Solutions — project context and agent brief

Reviewed: 2026-09-24. This document records repository evidence, working rules,
and proposed priorities. Recommendations are not implemented features.

## Current implementation scope (supersedes the original review-only scope)

The owner authorized UI, buyer positioning, SEO and tests after this review.
Do not modify models or migrations, or execute migration-backed test setup.
TopMap is a broader GIS services business: **land is the lead sector; utilities
and infrastructure are an expanding focus**, not a claim of completed utility
projects. Welcome international inquiries without inventing foreign offices,
clients, certifications, measured outcomes or delivery guarantees.

Implemented in this pass: buyer-focused homepage and sector sections, three
service pages driven by `apps/guests/content.py`, consistent responsive styles,
bound inquiry fields/errors, shared SEO metadata, canonical URLs, social tags,
organization structured data, public-site-scoped CMS navigation and sitemap,
robots.txt, and a database-free regression suite in `tests/`.

Use `make test-ui` or `.venv/bin/python -B -m django test tests
--settings=config.settings.test_ui`. These settings do not load environment
files and use the dummy database backend. The owner retains `make test` as
`uv run manage.py test`, which discovers all 34 tests including the eight legacy
database tests. The public-site tests now isolate their settings under either
runner. Do not execute the full runner under the no-migration rule: its database
setup applies migrations. Tests mock CMS/persistence/mail boundaries;
they do not establish real database, email or browser behavior.

The remaining sections are the original review snapshot, not a current bug list.
The email-before-persistence failure risk and deployment risks remain open.

## Mandatory working rules

- Stay within the current authorized implementation scope above. Changes to
  deployment, models or migrations are outside this pass.
- Never create, edit, delete, regenerate, or apply migrations. Do not run
  `makemigrations`, `migrate`, or `make migrate`.
- Do not start the Docker application: its entrypoint runs migrations. Do not
  run the existing database test suite under the current prohibition; Django's
  normal test database setup can apply migrations.
- If future work requires schema changes, explain the dependency and leave it
  unimplemented under this rule. Prefer solutions using the existing schema.
- Preserve existing user edits, especially the pre-existing `.env.example` edit.
- Do not read or expose secret values from `.env`, `.env.prod`, or `.env.testing`.
  Do not submit real inquiries, send email, deploy, or mutate production data
  during a review.
- Distinguish source-code findings from verified production behavior. Do not
  invent client results, endorsements, commercial commitments, or SEO metrics.
- Keep this a simple Django monolith. New frameworks, queues, services, and
  schema changes need a concrete operational benefit, not architectural fashion.

## What this repository is

TopMap Solutions' public marketing and lead-generation website for GIS services.
It explains services, displays customer logos, publishes case studies through
Wagtail, and captures inquiries with staff notifications and customer email.
The core business journey is visitor -> relevant evidence -> inquiry -> follow-up.

It is not currently the operational land-management/GIS platform described in
README.md. There are no implemented parcels, owners, boundaries, or customer
dashboard apps in this checkout. MapLibre assets alone do not establish a map
application. The README's GeoDjango/PostGIS/allauth stack and ingestion commands
are stale relative to the current application. Package version 1.0.1.0 is not
evidence of production maturity.

Current assessment: a small, understandable marketing-site foundation with a
useful case-study content model, but incomplete lead reliability, release
verification, discoverability, and commercial clarity. Production uptime,
published CMS content, traffic, conversion, revenue, and client outcomes were
not established by this review.

## Architecture and ownership map

- `pyproject.toml`, `uv.lock`: uv-managed Python project; declared Python >=3.14,
  Django >=6.0.6, Wagtail >=7.4.2, PostgreSQL driver, Gunicorn, WhiteNoise,
  django-storages/Boto3. The lockfile is the installation reference.
- `config/settings/base.py`: shared apps, middleware, PostgreSQL, templates,
  local media paths, and loading `.env`.
- `config/settings/dev.py`: local hosts, debug, filesystem storage, console mail.
- `config/settings/prod.py`: HTTPS-related settings, Brevo SMTP, Backblaze B2
  storage, WhiteNoise manifest static storage, apex/www host allowlist.
- `manage.py` defaults to development; `config/wsgi.py` defaults to production.
  Compose explicitly selects production settings for the production container.
- `apps/guests`: homepage, inquiry form, Guest lead model, cooldown selector,
  email service, views, admin, and eight basic test methods.
- `apps/case_studies`: Wagtail index/detail pages, client/location/summary,
  challenge/solution, tags, ordered outcome metrics and gallery images.
  `tests.py` is a placeholder.
- `core`: shared templates/styles/images, navigation context processor, and
  test storage override decorator.
- Frontend: server-rendered Django templates, plain CSS and JavaScript. No
  frontend build pipeline is declared. Homepage copy is hardcoded in templates;
  case studies are CMS-managed.
- `.docker`: multistage Python container and Compose definitions. Production
  expects an external Docker network/database and an environment file.
- `.github/workflows/deploy.yml`: pushes to main trigger SSH deployment to a
  Vultr server, reset its checkout, rebuild containers, and prune Docker resources.
  Reverse-proxy configuration is not present in the reviewed source.

### Routes and data flow

- `/`: public homepage.
- `/inquiry/`: inquiry page; `/inquiry/form/`: standalone form fragment.
- `/submit/`: POST validation -> 24-hour exact-email cooldown -> send staff email
  -> send customer email -> save Guest -> set session -> redirect.
- `/inquiry/success/`: consumes the submitted-email session value. Subsequent
  visits without that value redirect to inquiry.
- `/not-admin/`: Django administration; `/cms/`: Wagtail administration.
- `/documents/`: Wagtail documents; `/pages/`: Wagtail page routing. Actual case
  study URLs depend on the CMS tree and site configuration, not source alone.
- Guest records contain organization, name, email, inquiry, phone, created_at,
  and contacted. There is no modeled sales pipeline beyond contacted.

## Prioritized review findings

### P1 — Protect inquiries before acquiring more traffic

1. **Email failure prevents lead persistence.**
   `apps/guests/views/inquiry.py:49` sends both emails before creating Guest.
   Exceptions propagate. A staff email may succeed while customer email fails,
   leaving no stored lead and an error response. There is no explicit SMTP timeout
   in project settings. Future fix: make lead persistence independent of email
   availability, make the response truthful, and define observable recovery for
   failed notifications. A queue is not automatically necessary.
   Acceptance: simulate each email failure and verify the inquiry remains
   recoverable, the user gets a meaningful response, and retries are understood.

2. **Validation and cooldown errors are invisible; entered data disappears.**
   Views pass a bound `form`, but `templates/form/contact.html` reads standalone
   variables (`name`, `email`, etc.) and `error`, not the form's values/errors.
   Future fix: render bound values and field/non-field errors with accessible
   associations. Acceptance: invalid input and a cooldown rejection preserve
   entered values and clearly explain the next step.

3. **Deployment has no quality or readiness gate.**
   The only checked-in workflow deploys immediately on main pushes, uses mutable
   remote main, has no tests, health probe, rollback procedure, or concurrency
   guard. Detached Compose startup is not evidence that Gunicorn is serving.
   Cleanup prunes resources across the Docker host; volume pruning can remove
   eligible unused volumes and should not be routine application deployment.
   This does not prove active database volumes are being deleted.
   Future work: test gate, deploy a known revision, verify health, serialize
   deployments, document rollback and backup restore, scope cleanup explicitly.
   The Docker startup migration chain conflicts with this review's no-migration
   rule; document it without running or modifying it.

### P2 — Close material coverage, abuse, SEO, and trust gaps

4. **Tests do not protect the money path.** Eight authored tests cover Guest
   basics and two GET pages. Missing: successful submission, invalid input,
   cooldown behavior/boundary, mail failure, database failure, success-session
   behavior, CSRF enforcement, case-study routing/rendering, and missing CMS index.
   Prioritize behavior, not a headline coverage percentage. Under the current
   rule, use mocked/database-free checks; propose isolated DB tests separately
   without executing migration-backed setup.

5. **Cooldown is not effective abuse protection.** It checks an exact email
   string and is separate from insertion; different addresses and simultaneous
   submissions bypass it. The public endpoint sends to a submitted address.
   Propose layered rate limits and a lightweight spam trap, with useful errors
   and controls that do not exclude legitimate repeat inquiries. Confirm any
   existing proxy controls before claiming the production site lacks them.

6. **SEO foundations are absent from application templates/routes.** No meta
   descriptions, canonical links, social preview tags, structured data, sitemap
   route, or robots route were found. Homepage title is brand-only; case-study
   detail titles use client instead of page SEO title; Wagtail SEO fields are not
   wired into the rendered head. No dedicated service landing pages exist.
   Add accurate page-specific titles/descriptions and sensible canonical policy;
   connect Wagtail fields; expose an appropriate sitemap and public crawl policy;
   add useful social previews and only truthful structured data.
   Missing robots.txt does not itself block crawling. Social cards are for sharing,
   and a sitemap or structured data does not guarantee rankings.
   Verify live status codes, apex/www redirects, indexability, Search Console,
   and sitemap URLs before making production SEO claims.

7. **Case-study navigation can be missing or stale.**
   `core/context_processors.py` caches the first live index object for 24 hours;
   navbar always renders its URL. With no index it becomes an empty link; an
   existing cached object can outlive an unpublish or URL change. No invalidation
   or shared cache configuration is declared. Test absent/published/changed index
   states and make link behavior intentional.

8. **Buyer trust and follow-up need an explicit operating process.** The form
   has a short contact-use statement but no linked privacy notice. The site
   promises a reply in 1–2 business days without a documented ownership/escalation
   process. Define inquiry owner, response target, qualification questions,
   access/retention practices, and alternative contact path. Validate logo usage
   and case-study claims with the company; the repository cannot establish them.

### P3 — Refine frontend and maintainability after the above

- Homepage hero cycles through eleven assets, including code screenshots; two
  PNGs are roughly 1.7 and 2.0 MB on disk. They load over time, not all at initial
  render. Prefer a representative project visual, optimized responsive images,
  appropriate dimensions and reduced-motion support. Measure actual LCP/CLS/INP
  before claiming performance scores or regressions.
- Hero rotation and logo animation have no reviewed pause/reduced-motion behavior.
  Generic image alternative text, nested/repeated main landmarks and heading
  structure need accessibility review. Multiple h1 elements are not automatically
  an SEO penalty; improve the document outline for comprehension.
- CSS includes `--color-darl` instead of `--color-dark`, and invalid `1  rem`.
  Narrow-screen layouts deserve browser verification; none was performed here.
- The inquiry template contains malformed paragraph markup. An unused success
  component has an unnamespaced URL reversal; the active success template uses
  the correct namespace. Do not report that unused component as a confirmed live
  failure.
- The case-study CTA is conditional on outcome records; offer an intentional
  next step even when those records are absent.
- Case-study index queries per-card relations; measure before optimizing. The
  index has no pagination. Both matter more as the content library grows.
- `.dockerignore` omits `.venv`, local media and collected static exclusions;
  avoid unnecessarily large build contexts/images in later maintenance.
- `make lint` reformats templates; it is not a read-only check. Do not run it
  during review. Correct README only in a separately authorized change.

## Business positioning: proposed direction, not established strategy

Current homepage: “Modernize Your City With GIS”; five buyer groups, six service
categories, eight maturity stages, and competing CTA wording. This conveys
technical breadth but leaves the purchase vague. The visitor has to infer the
starting engagement, deliverables, risk, evidence, and next step.

Blunt diagnosis: this reads like a capable GIS practitioner's capability list
more than an easy-to-buy offer. An assessor with unreliable parcel records is
not shopping for an eight-stage maturity lecture. “Become our Partner” asks for
a relationship before explaining the transaction. Code screenshots show how
you work, not why an office should trust its records to you. More organic traffic
will not automatically repair that uncertainty.

Working niche hypothesis: Philippine city/municipal assessor and planning teams
with fragmented parcel records. This follows current copy and displayed Tagum
logos; it is not proven to be the most profitable segment. Validate with actual
client interviews, delivery margins, procurement cycle, and win/loss history.
Distinguish daily users, internal champions, budget holders and procurement.

### Original StoryBrand-style working brief

- Hero: the office/team responsible for dependable parcel information.
- Want: find and use records confidently without repeated manual reconciliation.
- External problem: paper, technical descriptions, CAD and GIS records disagree
  or live in separate places.
- Internal problem: staff face delays and uncertainty when asked for answers.
- Principle: public-service teams deserve information they can work with reliably.
- Guide: TopMap understands the workflow and demonstrates relevant, permissioned
  project evidence. Do not substitute unsupported superiority claims for proof.
- Plan: review a representative sample -> agree a scoped pilot and acceptance
  criteria -> validate results together and plan rollout/handover.
- Direct CTA proposal: “Request a Parcel Data Assessment.” Explain what happens
  next and whether it costs anything before publishing.
- Transitional CTA: “See a Parcel Conversion Case Study.”
- Stakes: continued rework, slow retrieval and inconsistent records, without
  invented savings or alarmist promises.
- Success: usable, validated parcel data and a team equipped to maintain it.

Proposed headline: “Turn scattered parcel records into GIS data your office can use.”
Supporting copy: “TopMap Solutions helps Philippine assessor and planning teams
convert, clean and organize parcel information, with a clear path from a sample
review to a working GIS workflow.” Validate service/geography before publication.

### Make the offer purchasable

1. Define an assessment: representative input sample, problem inventory, feasible
   output formats, pilot scope and written next-step recommendation. State sample
   handling rules; do not invite confidential land records into the public form.
2. Define a bounded pilot: agreed source volume/quality, QA method, acceptance
   criteria, exceptions, deliverables, handover and commercial terms.
3. Offer implementation and ongoing support only within demonstrated capacity.
   Separate conversion, integration, training and maintenance responsibilities.

Do not invent prices, turnaround guarantees, accuracy percentages or ROI. Build
one strong case study with permission: starting problem, source volume, scope,
method, measured outcome, limitations and client attribution. The existing CMS
already supports much of this; no schema change is needed to begin.

Suggested homepage order: specific outcome and CTA -> relevant proof -> concrete
problem -> offer -> three-step plan -> case study -> buyer questions -> same CTA.
Move the eight-stage educational material to supporting content if useful.

SEO content hypotheses: technical-description conversion, CAD-to-GIS conversion,
parcel-data validation, and GIS for assessor offices. Validate search intent and
commercial relevance; no keyword-volume research was performed. Publish useful
service pages with examples, required inputs, outputs, process and proof rather
than thin location pages or generic GIS articles.

Business measures: qualified inquiries by source, assessment bookings, proposals,
wins, response time, sales-cycle length, delivery margin and repeat business.
Traffic is diagnostic; qualified profitable work is the outcome. No analytics
integration was found in templates; external measurement remains unknown.

## Suggested next work sequence

1. Repair and verify inquiry persistence, validation UX and notification failure
   behavior; define the staff follow-up process.
2. Add release checks and targeted behavior tests within the migration constraint;
   separately plan infrastructure readiness, backups, restore and rollback.
3. Validate primary buyer and entry offer; agree evidence and claims with owner.
4. Update homepage and publish one substantial proof page, then service pages.
5. Implement technical SEO and measurement; verify live crawling and conversions.
6. Refine mobile UX, accessibility and image delivery based on browser measurements.

## Review evidence and limits

- Read application source, templates, CSS/JS, settings, build/deploy definitions,
  project metadata and test source. Did not open secret environment files.
- Parsed 35 Python files excluding migrations successfully.
- Used isolated Django settings with a declared in-memory database but no database
  connection/schema operations. Rendered the form with invalid bound data:
  validation error existed, error text was absent, and entered name was absent.
- Called the submission view with cooldown, mail and persistence mocked:
  simulated mail exception propagated and persistence was never called.
- No email sent, database accessed, migrations touched, Docker started, full test
  suite run, production inspected, or browser visual audit performed.
- Existing `.env.example` modification belongs to the user. This review adds only
  `agent.md`. This filename is the requested brief; it is not a claim that an
  assistant automatically loads it as repository instructions.

Primary references for the recommendations:

- Google Search Central, SEO Starter Guide:
  https://developers.google.com/search/docs/fundamentals/seo-starter-guide
- Google Search Central, title links:
  https://developers.google.com/search/docs/appearance/title-link
- StoryBrand, Your Brand Is Not the Hero:
  https://storybrand.com/downloads/your-brand-is-not-the-hero.pdf

Revalidate this dated snapshot as the repository and business change.
