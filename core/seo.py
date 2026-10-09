"""Canonical public URLs and metadata; never derive the public origin from a Host header."""

from urllib.parse import urljoin, urlsplit

from django.conf import settings
from django.urls import reverse
from django.templatetags.static import static
from django.utils.html import strip_tags

from apps.guests.content import SERVICES


def public_url(path):
    origin = getattr(settings, "PUBLIC_SITE_URL", "https://topmapsolutions.com").rstrip(
        "/"
    )
    return origin + "/" + urlsplit(path).path.lstrip("/")


def public_static_url(path):
    """Use collected filenames and preserve an externally hosted static origin."""
    return urljoin(public_url("/"), static(path))


def metadata(request, page=None):
    match = getattr(request, "resolver_match", None)
    route = getattr(match, "url_name", None)
    title = "LGU Land Parcels & Interactive Masterplans in the Philippines | TopMap Solutions"
    description = "Philippines-based TopMap Solutions helps LGU assessor and planning teams centralize land parcel, tax and spatial planning data, and turns existing masterplans into interactive browser maps for local and international teams."
    noindex = False
    path = request.path
    editorial = page or getattr(request, "topmap_editorial_object", None)
    if editorial is not None:
        label = getattr(editorial, "title", None) or getattr(
            editorial, "name", "Product"
        )
        title = f"{editorial.seo_title or label} | TopMap Solutions"
        description = strip_tags(
            editorial.search_description
            or getattr(editorial, "summary", "")
            or f"Learn about {label} from TopMap Solutions."
        )
        if hasattr(editorial, "get_url"):
            path = editorial.get_url(request=request) or request.path
        else:
            path = editorial.get_absolute_url()
        published = getattr(editorial, "live", getattr(editorial, "is_published", True))
        noindex = bool(getattr(request, "is_preview", False)) or not published
    elif route == "service_detail":
        service = SERVICES.get(match.kwargs.get("slug"))
        if service:
            title = f"{service['title']} | TopMap Solutions"
            description = service["description"]
        else:
            noindex = True
    elif route == "index" and getattr(match, "namespace", None) == "products":
        title = "GIS Products, Training & Manuals | TopMap Solutions"
        description = "Explore TopMap Solutions products for parcel and WebGIS workflows, with practical training and product manuals."
        path = reverse("products:index")
    elif route in {"privacy", "legal", "terms"}:
        legal_pages = {
            "privacy": (
                "Privacy Policy | TopMap Solutions",
                "Read TopMap Solutions' privacy policy for website visits, project inquiries, client materials, and interactive map demonstrations.",
            ),
            "legal": (
                "Legal & Map Disclaimer | TopMap Solutions",
                "Review TopMap Solutions' legal and map disclaimer for interactive maps, client materials, and third-party geographic information.",
            ),
            "terms": (
                "Terms of Use | TopMap Solutions",
                "Read the terms governing use of the TopMap Solutions website, interactive maps, demonstrations, and online materials.",
            ),
        }
        title, description = legal_pages[route]
        path = reverse(f"guests:{route}")
    elif route in {"inquiry", "send_public_form", "inquiry_form"}:
        title = "Start Your Land or Mapping Project | TopMap Solutions"
        description = "Tell TopMap Solutions about your LGU land information workflow or interactive masterplan project and the outcome you need."
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
    return {
        "title": title,
        "description": " ".join(description.split()),
        "canonical": public_url(path),
        "noindex": noindex,
        "image": public_static_url("images/city-planning.jpg"),
        "home": public_url("/"),
    }


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
