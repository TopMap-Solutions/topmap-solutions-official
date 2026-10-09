from django.urls import path

from . import views

app_name = "licensing"

urlpatterns = [
    path("health/", views.health, name="health"),
    path("activate/", views.activate_view, name="activate"),
    path("validate/", views.validate_view, name="validate"),
    path("deactivate/", views.deactivate_view, name="deactivate"),
]
