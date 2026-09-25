"""Canonical public URLs and metadata; never derive the public origin from a Host header."""
from urllib.parse import urljoin, urlsplit

from django.conf import settings
from django.urls import reverse
from django.templatetags.static import static
from django.utils.html import strip_tags

from apps.guests.content import SERVICES


def public_url(path):
    origin = getattr(settings, "PUBLIC_SITE_URL", "https://topmapsolutions.com").rstrip("/")
    return origin + "/" + urlsplit(path).path.lstrip("/")


def public_static_url(path):
    """Use collected filenames and preserve an externally hosted static origin."""
    return urljoin(public_url("/"), static(path))


def metadata(request, page=None):
    match = getattr(request, "resolver_match", None)
    route = getattr(match, "url_name", None)
    title = "GIS Services in the Philippines | TopMap Solutions"
    description = "Philippines-based GIS data conversion, spatial validation and web GIS consulting. Land expertise, with remote collaboration for local and international teams."
    noindex = False
    path = request.path
    if page is not None:
        title = f"{page.seo_title or page.title} | TopMap Solutions"
        description = strip_tags(page.search_description or getattr(page, "summary", "") or getattr(page, "intro", "") or f"Explore {page.title}: GIS project work from TopMap Solutions.")
        path = page.get_url(request=request) or request.path
        noindex = bool(getattr(request, "is_preview", False)) or not getattr(page, "live", True)
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
    return {"title": title, "description": " ".join(description.split()), "canonical": public_url(path), "noindex": noindex,
            "image": public_static_url("images/city-planning.jpg"), "home": public_url("/")}


def page_schema(request, data):
    """Describe public service pages using the same evidence as their visible copy."""
    match = getattr(request, "resolver_match", None)
    if data["noindex"] or getattr(match, "url_name", None) != "service_detail":
        return None
    service = SERVICES.get(match.kwargs.get("slug"))
    if not service:
        return None
    return {
        "@context": "https://schema.org",
        "@type": "Service",
        "@id": data["canonical"] + "#service",
        "name": service["name"],
        "serviceType": service["title"],
        "description": service["description"],
        "url": data["canonical"],
        "provider": {"@id": data["home"] + "#organization"},
    }
