from xml.etree.ElementTree import Element, SubElement, tostring

from django.http import HttpResponse
from django.urls import reverse
from django.views.decorators.http import require_safe

from apps.guests.content import SERVICES
from core.public_pages import case_study_pages
from core.seo import public_url


@require_safe
def robots(request):
    body = "User-agent: *\nAllow: /\nDisallow: /cms/\nDisallow: /not-admin/\n"
    return HttpResponse(body + f"\nSitemap: {public_url('/sitemap.xml')}\n", content_type="text/plain")


@require_safe
def sitemap(request):
    root = Element("urlset", xmlns="http://www.sitemaps.org/schemas/sitemap/0.9")
    paths = [reverse("guests:homepage"), reverse("guests:inquiry")]
    paths += [reverse("guests:service_detail", kwargs={"slug": slug}) for slug in SERVICES]
    entries = [(path, None) for path in paths]
    for page in case_study_pages(request):
        url = page.get_url(request=request)
        if url:
            entries.append((url, page.last_published_at))
    seen = set()
    for path, modified in entries:
        url = public_url(path)
        if url in seen:
            continue
        seen.add(url)
        item = SubElement(root, "url")
        SubElement(item, "loc").text = url
        if modified:
            SubElement(item, "lastmod").text = modified.date().isoformat()
    return HttpResponse(tostring(root, encoding="utf-8", xml_declaration=True), content_type="application/xml")
