from django.urls import path
from admin_login.views import AzureADSignupView


urlpatterns = [
    path('signup-as-admin/', AzureADSignupView.as_view(), name='signup_as_admin'),
    path('signup-as-admin/callback/', AzureADSignupView.as_view(), name='azure_signup_callback'),
]