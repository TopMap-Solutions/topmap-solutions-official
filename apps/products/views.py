from django.shortcuts import get_object_or_404, render

from .models import Product, ProductGuide
from .selectors import public_guides, public_products


def product_index(request):
    return render(
        request, "products/product_index.html", {"products": public_products()}
    )


def product_detail(request, product_slug):
    product = get_object_or_404(Product.objects.public(), slug=product_slug)
    request.topmap_editorial_object = product
    return render(
        request,
        "products/product_detail.html",
        {"product": product, "guides": public_guides(product)},
    )


def product_guide(request, product_slug, guide_slug):
    product = get_object_or_404(Product.objects.public(), slug=product_slug)
    guide = get_object_or_404(
        ProductGuide.objects.public().filter(product=product), slug=guide_slug
    )
    request.topmap_editorial_object = guide
    siblings = list(public_guides(product))
    position = siblings.index(guide)
    return render(
        request,
        "products/product_guide.html",
        {
            "product": product,
            "guide": guide,
            "previous_guide": siblings[position - 1] if position else None,
            "next_guide": siblings[position + 1]
            if position + 1 < len(siblings)
            else None,
        },
    )
