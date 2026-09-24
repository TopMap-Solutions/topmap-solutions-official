from django.http import Http404
from django.shortcuts import render

from apps.guests.content import SERVICES
from apps.guests.forms import InquiryForm


def homepage(request):
    return render(request, "homepage.html", {"services": SERVICES})


def service_detail(request, slug):
    if slug not in SERVICES:
        raise Http404("Service not found")
    return render(request, "service_detail.html", {"service": SERVICES[slug], "services": SERVICES})


def inquiry_page(request):
    return render(request, "inquiry.html", {"form": InquiryForm()})
