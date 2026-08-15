from django.urls import path
from . import views

urlpatterns = [
    path("", views.homepage, name="homepage"),
    path("inquiry/", views.inquiry_page, name="inquiry"),
    path("inquiry/form/", views.inquiry_form, name="inquiry_form"),
    path("inquiry/success/", views.inquiry_success, name="inquiry_success"),
    path("submit/", views.send_public_form, name="send_public_form"),
]
