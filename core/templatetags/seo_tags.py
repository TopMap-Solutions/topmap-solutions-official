import json

from django import template
from core.seo import metadata

register = template.Library()


@register.inclusion_tag("seo_head.html", takes_context=True)
def seo_head(context):
    data = metadata(context["request"], context.get("page"))
    # Escape HTML-significant characters before placing JSON inside a script element.
    schema = {"@context": "https://schema.org", "@type": "Organization",
              "name": "TopMap Solutions", "url": data["home"]}
    data["organization_json"] = json.dumps(schema).replace("<", "\\u003c").replace(">", "\\u003e").replace("&", "\\u0026")
    return data
