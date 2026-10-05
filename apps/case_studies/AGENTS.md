# Case studies and testimonials — agent guide

Read the repository-level `AGENTS.md` first. This file applies to everything in
`apps/case_studies/`.

## Scope

This app owns Wagtail-managed editorial evidence:

- case-study index and detail pages;
- project outcomes, tags and galleries;
- reusable client testimonials shown on the marketing site.

Do not turn this app into a CRM or duplicate inquiry/contact records from
`apps/guests/`.

## Planned testimonial architecture

Testimonials should be a standalone Wagtail snippet, not fields attached to the
homepage or a `CaseStudyPage`. This allows the collection to grow and be reused
without requiring one testimonial per case study.

Keep the initial schema focused on the requested content:

- testimonial text;
- optional person's name;
- optional organization;
- optional Wagtail image for the organization logo;
- explicit public-approval/published state, hidden by default;
- numeric display order, with a stable secondary ordering.

Do not add job titles, ratings, invented metrics, or a case-study relationship
until there is a demonstrated content requirement.

Register the model in Wagtail's Snippets area with useful list columns, filters
and search. Logo deletion must not delete the testimonial; an absent logo must
remain a valid state.

## Homepage presentation contract

The public homepage continues to own the presentation template and styles under
`apps/guests/`. The homepage view should receive testimonials through a small
query/selector boundary from this app and fetch only publicly approved records.
Avoid database queries inside templates.

Render the attribution as follows:

1. When a person's name exists, show it followed by the organization when one
   is available.
2. When no name exists, show the organization as the sole attribution.
3. When both name and organization are absent, show `Anonymous`.
4. When a logo exists, render an appropriate Wagtail image rendition with useful
   alternative text based on the organization.
5. When no logo exists, omit the logo element and preserve the layout; do
   not show a broken image or generic fake logo.

Render testimonials as a centered, touch-friendly carousel using CSS overflow
and scroll snapping. Keep native scrolling and keyboard access and do not add a
carousel dependency. Show compact previous/next chevrons and up to five truthful
slide-indicator dots when there is more than one item; do not show text labels or
a numeric counter. When there is more than one item, advance every five seconds;
pause while the component has keyboard focus or the document is hidden, and
disable timed motion for visitors who prefer reduced motion. The layout must work
with one item and continue growing without template changes. Preserve an honest
empty state when there are no approved testimonials.

## Models and migrations

Any testimonial model requires a new migration. Never modify the existing
migration history. Identify and review the schema first, then create a new
migration only when the owner authorizes implementation under the repository's
model and migration rules.

## Tests

Cover at least:

- Wagtail snippet/model validation and default hidden state;
- public filtering and deterministic ordering;
- name plus organization attribution;
- organization-only fallback when the name is blank;
- anonymous fallback when both name and organization are blank;
- logo present and logo absent rendering;
- empty-state rendering;
- accessible horizontal scrolling markup and unchanged homepage section order.

Keep public UI tests database-free where practical by mocking the testimonial
query boundary, consistent with `apps/guests/tests/test_public_site.py`.
