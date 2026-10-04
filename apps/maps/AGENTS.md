# TopMap Interactive Maps — agent guide

This file applies to `apps/maps/` and overrides the root guide where it is more
specific.

Read the repository root `AGENTS.md` first.

## Purpose

`apps/maps/` powers TopMap Solutions' public interactive-map showcase.

Its job is to display already-prepared spatial outputs as simple, polished,
browser-based maps.

The primary current use case is:

masterplan/site drawing → externally prepared map data → interactive client map

It may also support other land/property outputs such as:

- subdivision plans;
- parcel maps;
- site-development plans;
- zoning/land-use examples;
- approved LGU demonstrations;
- other client-approved land maps.

The app is a PRESENTATION layer.

It is not the production GIS-processing platform.

## Core domain

Use two primary concepts unless real requirements demonstrate otherwise.

### Organization

Represents the organization associated with one or more published map projects.

Typical fields may include:

- name;
- slug;
- logo/branding reference;
- website;
- short public description.

Do not assume every organization is a paying client.

Do not call an organization a client unless supported by real evidence.

### MapProject

Represents one interactive map.

Typical responsibilities include:

- organization relationship;
- title;
- slug;
- public description;
- published/public state;
- map-data reference;
- initial map position/extent;
- presentation configuration;
- optional relationship to supporting case-study content.

Keep this model small.

Do not attempt to model a complete GIS project-management system.

## URLs

Public URLs should follow:

```text
/maps/
/maps/<organization-slug>/
/maps/<organization-slug>/<project-slug>/
```

