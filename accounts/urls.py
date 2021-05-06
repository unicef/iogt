from django.contrib.auth.views import LoginView, LogoutView
from django.urls import path, reverse_lazy

from . import views

app_name = "accounts"
urlpatterns = [
    path("login/", LoginView.as_view(template_name="accounts/login.html"), name="login"),
    path("logout/", LogoutView.as_view(template_name="accounts/logout.html"), name="logout"),
    path("update/", views.UserUpdateView.as_view(), name="update"),
    path("profile/", views.UserProfileView.as_view(), name="profile"),
]
