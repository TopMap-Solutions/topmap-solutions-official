"""Canonical public URLs and metadata; never derive the public origin from a Host header."""
from urllib.parse import urlsplit

from django.conf import settings
from django.urls import reverse
from django.utils.html import strip_tags

from apps.guests.content import SERVICES


def public_url(path):
    origin = getattr(settings, "PUBLIC_SITE_URL", "https://topmapsolutions.com").rstrip("/")
    return origin + "/" + urlsplit(path).path.lstrip("/")


def metadata(request, page=None):
    match = getattr(request, "resolver_match", None)
    route = getattr(match, "url_name", None)
    title = "GIS Data Conversion, Mapping & Web GIS | TopMap Solutions"
    description = "Make spatial data work for your team. TopMap Solutions offers GIS data conversion, validation and web mapping, with land expertise and a growing utilities focus."
    noindex = False
    path = request.path
    if page is not None:
        title = f"{page.seo_title or page.title} | TopMap Solutions"
        description = strip_tags(page.search_description or getattr(page, "summary", "") or getattr(page, "intro", "") or f"Explore {page.title}: GIS project work from TopMap Solutions.")
        path = page.get_url(request=request) or request.path
        noindex = bool(getattr(request, "is_preview", False))
    elif route == "service_detail":
        service = SERVICES.get(match.kwargs.get("slug"))
        if service:
            title = f"{service['title']} | TopMap Solutions"
            description = service["description"]
        else:
            noindex = True
    elif route in {"inquiry", "send_public_form", "inquiry_form"}:
        title = "Discuss Your GIS Project | TopMap Solutions"
        description = "Tell us about your GIS data, mapping or web application needs. Discuss project scope, deliverables and remote collaboration with TopMap Solutions."
        path = reverse("guests:inquiry")
        noindex = route != "inquiry"
    elif route == "inquiry_success":
        title = "Inquiry Received | TopMap Solutions"
        description = "Your project inquiry has been received by TopMap Solutions."
        noindex = True
    elif route != "homepage":
        title = "Page Not Found | TopMap Solutions"
        description = "Find GIS services and project information from TopMap Solutions."
        noindex = True
    return {"title": title, "description": description, "canonical": public_url(path), "noindex": noindex,
            "image": public_url("/static/images/city-planning.jpg"), "home": public_url("/")}
