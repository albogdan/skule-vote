from django.urls import path
from backend import views
from django.conf import settings

app_name = "backend"

urlpatterns = [
    path(
        "elections/",
        views.ElectionListView.as_view(),
        name="election-list",
    ),
    path("vote/", views.BallotSubmitView.as_view(), name="ballot-submit"),
    path(
        "electionsession/",
        views.ElectionSessionListView.as_view(),
        name="election-session-list",
    ),
    path("votereligible/", views.VoterEligibleView.as_view(), name="voter-eligible"),
]

if not settings.CONNECT_TO_UOFT:
    urlpatterns.append(
        path(
            "bypasscookie/", views.BypassUofTCookieView.as_view(), name="bypass-cookie"
        )
    )
