from django.conf import settings
from django.http import Http404
from django.shortcuts import render

from apps.case_studies.selectors import public_testimonials
from apps.guests.content import SERVICES
from apps.guests.forms import InquiryForm


def homepage(request):
    image_directory = settings.BASE_DIR / "core" / "static" / "images"
    hero_images = [
        {
            "path": f"images/{path.name}",
            "alt": path.stem.replace("-", " ").replace("_", " "),
        }
        for path in sorted(
            image_directory.glob("*"),
            key=lambda path: (path.name != "city-planning.jpg", path.name.lower()),
        )
        if path.is_file()
        and path.suffix.lower()
        in {".jpg", ".jpeg", ".png", ".webp", ".avif", ".gif", ".svg"}
    ]
    return render(
        request,
        "homepage.html",
        {
            "services": SERVICES,
            "hero_images": hero_images,
            "testimonials": public_testimonials(),
        },
    )


def service_detail(request, slug):
    if slug not in SERVICES:
        raise Http404("Service not found")
    return render(
        request,
        "service_detail.html",
        {"service": SERVICES[slug], "services": SERVICES},
    )


def inquiry_page(request):
    return render(request, "inquiry.html", {"form": InquiryForm()})


def privacy_page(request):
    return render(request, "privacy.html")


def legal_page(request):
    return render(request, "legal.html")


def terms_page(request):
    return render(request, "terms.html")
