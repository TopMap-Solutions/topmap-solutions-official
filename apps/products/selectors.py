from .models import Product, ProductGuide


def public_products():
    return Product.objects.public().select_related("card_image")


def homepage_products():
    return public_products().filter(highlight_on_homepage=True)


def public_guides(product):
    return ProductGuide.objects.public().filter(product=product)
