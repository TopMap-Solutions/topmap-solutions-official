from django.urls import path

from . import views

app_name = "products"

urlpatterns = [
    path("", views.product_index, name="index"),
    path("<slug:product_slug>/", views.product_detail, name="detail"),
    path(
        "<slug:product_slug>/guides/<slug:guide_slug>/",
        views.product_guide,
        name="guide",
    ),
]
