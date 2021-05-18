from django.urls import path, include

app_name = "api"

urlpatterns = [
    path("backend/", include("backend.api_urls", namespace="backend")),
]
