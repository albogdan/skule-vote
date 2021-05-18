from django.urls import path
from backend import views


app_name = "backend"

urlpatterns = [
    path(
        "elections/",
        views.ElectionListView.as_view(),
        name="election-list",
    ),
    path("cookie/", views.CookieView),
]
