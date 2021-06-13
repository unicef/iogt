from django.contrib.auth.decorators import login_required
from django.urls import path

from questionnaires import views

urlpatterns = [
    path("", views.IndexView.as_view(), name="index"),
    path("results/<int:poll_id>/", views.poll_results, name="results"),
    path(
        "vote/<int:poll_id>/",
        views.VoteFormView.as_view(),
        name="vote",
    ),
    path(
        "auth-vote/<int:poll_id>/",
        login_required(views.VoteFormView.as_view()),
        name="auth_vote",
    ),
]
