from django.shortcuts import render
from django.shortcuts import redirect, render
from django.contrib.auth import authenticate, login, get_user_model
from django.views.generic import TemplateView
from django.http import HttpResponseBadRequest
from django.core.exceptions import ValidationError
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from django.views import View
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied

from admin_login.azure_backend import AzureADSignupService, get_azure_auth_details

User = get_user_model()
# Create your views here.



class AzureADSignupView(View):
    template_name = 'signup.html'

    def get(self, request, *args, **kwargs):
        """
        Render the signup form or redirect to Azure AD B2C for authorization.
        """
        # Check if we have an authorization code (callback)
        if request.user.is_authenticated:
            return redirect('/admin/')  # Replace with the appropriate URL for logged-in users

        code = request.GET.get('code')
        next_url = request.GET.get('next', '/admin/')

        if code:
            # Handle the callback and complete signup
            signup_service = AzureADSignupService()
            try:
                user_info = signup_service.handle_signup_callback(request)
                user = self._save_user_info(user_info)
                self._login_user(request, user)
                return redirect(next_url)
            except ValidationError as e:
                return JsonResponse({"error": str(e)}, status=400)

        # Redirect to Azure AD B2C for user signup
        azure_signup_url = self._get_azure_signup_url()
        return redirect(azure_signup_url)


    def post(self, request, *args, **kwargs):
        """
        Handle user input, prepare for redirect to Azure AD B2C for signup.
        """
        # Here, you could collect user info and generate a redirect to Azure AD B2C.
        return self.get(request, *args, **kwargs)


    def _get_azure_signup_url(self):
        """
        Generate the URL for Azure AD B2C authorization.
        """
        tenant_id = get_azure_auth_details()['tenant_id']
        client_id = get_azure_auth_details()['client_id']
        redirect_uri = get_azure_auth_details()['redirect_uri']
        policy = get_azure_auth_details()['policy']

        authority = f"https://{tenant_id}.b2clogin.com/{tenant_id}.onmicrosoft.com/v2.0"

        # Construct the URL for Azure AD B2C login/signup
        signup_url = f"{authority}/oauth2/v2.0/authorize?p={policy}&client_id={client_id}&response_type=code&redirect_uri={redirect_uri}&scope=openid+profile+email"
        return signup_url

    def _save_user_info(self, user_info):
        """
        Save the user information in the database.
        """
        email = user_info.get('emails', [])[0]
        name = user_info.get('name')
        given_name = user_info.get('given_name')

        if not User.objects.filter(email=email).exists():
            raise PermissionDenied("Access Denied: You are not allowed to sign up.")
        # Check if the user already exists
        user, created = User.objects.get_or_create(
            email=email,
            defaults={
                'username': email,
                'first_name': given_name,
                'is_staff': True,  # Make the user an admin
                'is_superuser': True,  # Grant superuser permissions
            },
        )
        if not created:
            # Update user details if necessary
            user.first_name = given_name
            user.save()

        user.is_superuser = True
        user.is_staff = True
        user.save()
        return user

    def _login_user(self, request, user):
        """
        Log the user in.
        """
        user.backend = "django.contrib.auth.backends.ModelBackend"
        login(request, user)
