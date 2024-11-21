from django.urls import path
from admin_login.views import AzureADSignupView


urlpatterns = [
    path('signup-as-admin/callback/', AzureADSignupView.as_view(), name='azure_signup_callback'),
]