from django.urls import path, include

app_name = "api"

urlpatterns = [
    path("", include("backend.api_urls", namespace="backend")),
]
