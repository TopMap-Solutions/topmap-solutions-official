from django.urls import path
from . import views

app_name = "guests"

urlpatterns = [
    path("", views.homepage, name="homepage"),
    path("products/", views.products_page, name="products"),
    path("privacy/", views.privacy_page, name="privacy"),
    path("legal/", views.legal_page, name="legal"),
    path("terms/", views.terms_page, name="terms"),
    path("services/<slug:slug>/", views.service_detail, name="service_detail"),
    path("inquiry/", views.inquiry_page, name="inquiry"),
    path("inquiry/form/", views.inquiry_form, name="inquiry_form"),
    path("inquiry/success/", views.inquiry_success, name="inquiry_success"),
    path("submit/", views.send_public_form, name="send_public_form"),
]
