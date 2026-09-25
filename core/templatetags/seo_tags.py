import json

from django import template
from core.seo import metadata, page_schema

register = template.Library()


def script_json(value):
    # Prevent editor-controlled content from ending a JSON-LD script element.
    return json.dumps(value).replace("<", "\\u003c").replace(">", "\\u003e").replace("&", "\\u0026")


@register.inclusion_tag("seo_head.html", takes_context=True)
def seo_head(context):
    data = metadata(context["request"], context.get("page"))
    schema = {"@context": "https://schema.org", "@type": "Organization",
              "@id": data["home"] + "#organization",
              "name": "TopMap Solutions", "url": data["home"],
              "description": "Philippines-based GIS data conversion, spatial validation and web GIS consulting for local and international teams.",
              "address": {"@type": "PostalAddress", "addressCountry": "PH"}}
    data["organization_json"] = script_json(schema)
    service = page_schema(context["request"], data)
    data["service_json"] = script_json(service) if service else None
    return data
