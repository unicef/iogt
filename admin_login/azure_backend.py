import requests
import base64
import json
import jwt

from django.contrib.auth.backends import BaseBackend
from django.contrib.auth import get_user_model
from django.conf import settings
from django.core.exceptions import ValidationError

from requests.exceptions import RequestException
from admin_login.azure_utility import get_azure_auth_details, get_b2c_token_url, payload_for_access_token
User = get_user_model()


class AzureADBackend(BaseBackend):
    """
    Custom authentication backend for Azure AD using MSAL.
    """
    def authenticate(self, request, username=None, password=None, **kwargs):
        """
        Authenticate user via Azure AD using username (email) and password.
        """
        pass
    #     azure_details = get_azure_auth_details()
    #
    #     # Initialize MSAL client
    #     msal_client = PublicClientApplication(
    #         client_id=azure_details['client_id'],
    #         authority=azure_details['authority'],
    #     )
    #
    #     # Acquire token using username and password
    #     try:
    #         token_data = msal_client.acquire_token_by_username_password(
    #             username=username,
    #             password=password,
    #             scopes=azure_details['scope']
    #         )
    #
    #         if 'access_token' in token_data:
    #             # Token is valid, retrieve or create the user
    #             user, created = User.objects.get_or_create(
    #                 email=username, defaults={'username': username}
    #             )
    #             return user
    #         else:
    #             return None
    #     except Exception as e:
    #         # Log or handle error appropriately
    #         print(f"Error during Azure AD authentication: {e}")
    #         return None
    #
    # def get_user(self, user_id):
    #     """
    #     Retrieve user by their ID.
    #     """
    #     try:
    #         return User.objects.get(pk=user_id)
    #     except User.DoesNotExist:
    #         return None


class AzureADSignupService:
    def __init__(self):
        # Retrieve Azure AD settings from configuration
        self.token_url = get_b2c_token_url()
        print(f"Constructed token URL: {self.token_url}")

    def handle_signup_callback(self, request):
        """
        Handle the OAuth 2.0 callback after user authorization.
        This function will exchange the authorization code for tokens.
        """
        code = request.GET.get('code')
        if not code:
            raise ValidationError("Authorization code not found in the callback.")

        # Exchange the code for an access token
        token_data = self._exchange_code_for_tokens(code)

        # Retrieve user information from the ID token

        # Print the decoded token to see the claims
        user_info = self._get_user_info(token_data['id_token'])

        # Here, you would typically use user_info to create a new user in your system.
        return user_info

    def _exchange_code_for_tokens(self, code):
        """
        Exchange the authorization code for access and ID tokens.
        """
        try:
            # Prepare the data payload and headers
            data = payload_for_access_token(code)
            headers = {
                'Content-Type': 'application/x-www-form-urlencoded',
            }

            # Send the POST request
            response = requests.post(self.token_url, data=data, headers=headers)
            response.raise_for_status()  # Raise an error for HTTP response codes >= 400

            # Parse the JSON response
            tokens = response.json()

            # Decode the ID token for user information (without verifying the signature)
            id_token = tokens.get('id_token')
            if not id_token:
                raise ValueError("ID token not found in the response")

            return {
                "access_token": tokens.get("access_token"),
                "refresh_token": tokens.get("refresh_token"),
                "id_token": tokens.get('id_token'),
                "expires_in": tokens.get("expires_in"),
            }

        except RequestException as e:
            # Handle HTTP request errors
            return {"error": "HTTP Request failed", "details": str(e)}
        except jwt.DecodeError:
            # Handle ID token decoding errors
            return {"error": "Failed to decode ID token"}
        except Exception as e:
            # Handle any other unexpected errors
            return {"error": "An unexpected error occurred", "details": str(e)}

    def _get_user_info(self, id_token):
        """
        Decode the ID token to get user information.
        """
        decoded_token = jwt.decode(id_token, options={"verify_signature": False})

        return decoded_token
