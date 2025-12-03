from django.shortcuts import redirect
from django.contrib.auth import login, get_user_model
from django.views import View
from django.core.exceptions import ValidationError, PermissionDenied
from django.http import JsonResponse
from urllib.parse import urlencode, quote, unquote
import json
import base64
import hmac
import hashlib
from admin_login.azure_backend import AzureADSignupService, get_azure_auth_details

User = get_user_model()

def _b64url(data: bytes) -> str:
    return base64.urlsafe_encode64(data).decode().rstrip("=")

def _b64url_decode(s: str) -> bytes:
    pad = "=" * ((4 - len(s) % 4) % 4)
    return base64.urlsafe_b64decode(s + pad)

class AzureADSignupView(View):
    """
    Forces Wagtail admin logins through Azure AD B2C.
    Uses `state` to preserve ?next= across the round-trip.
    """
    template_name = 'signup.html'

    # Optional: simple HMAC to avoid tampering with state in transit.
    STATE_SECRET = b'change-me-in-settings-or-env'  # set from settings.SECRET_KEY ideally

    def get(self, request, *args, **kwargs):
        # If already authenticated, go straight to admin
        if request.user.is_authenticated:
            return redirect('/admin/')

        code = request.GET.get('code')
        state = request.GET.get('state')

        if code:
            # === Callback phase ===
            next_url = '/admin/'
            if state:
                try:
                    next_url = self._parse_state(state)
                except Exception:
                    # If state invalid, fall back safely
                    next_url = '/admin/'

            signup_service = AzureADSignupService()
            try:
                user_info = signup_service.handle_signup_callback(request)
                user = self._save_user_info(user_info)
                self._login_user(request, user)

                # Mark this session as B2C for your middleware
                request.session['auth_via'] = 'b2c'

                return redirect(next_url)
            except ValidationError as e:
                return JsonResponse({"error": str(e)}, status=400)

        # === Initial phase ===
        next_url = request.GET.get('next', '/admin/')
        azure_signup_url = self._get_azure_signup_url(next_url)
        return redirect(azure_signup_url)

    def post(self, request, *args, **kwargs):
        return self.get(request, *args, **kwargs)

    def _get_azure_signup_url(self, next_url: str) -> str:
        """
        Generate the Azure AD B2C authorize URL and include a signed `state`
        carrying the next URL so we can round-trip it back.
        """
        auth = get_azure_auth_details()
        tenant = auth['tenant_id']          # e.g. 'contoso' (without .onmicrosoft.com)
        client_id = auth['client_id']
        redirect_uri = auth['redirect_uri'] # MUST match the one in Azure portal exactly
        policy = auth['policy']             # e.g. 'B2C_1_signupsignin'

        # Recommended B2C format with policy segment in the path:
        # https://{tenant}.b2clogin.com/{tenant}.onmicrosoft.com/{policy}/oauth2/v2.0/authorize
        base = f"https://{tenant}.b2clogin.com/{tenant}.onmicrosoft.com/{policy}/oauth2/v2.0/authorize"

        # Build signed state containing next_url
        state = self._make_state({'next': next_url})

        params = {
            'client_id': client_id,
            'response_type': 'code',
            'redirect_uri': redirect_uri,
            'response_mode': 'query',
            'scope': 'openid profile email',
            'state': state,
        }
        return f"{base}?{urlencode(params)}"

    # --- state helpers (simple HMAC-protected blob) ---
    def _make_state(self, payload: dict) -> str:
        blob = json.dumps(payload, separators=(',', ':')).encode()
        mac = hmac.new(self.STATE_SECRET, blob, hashlib.sha256).digest()
        return _b64url(mac + blob)

    def _parse_state(self, state: str) -> str:
        raw = _b64url_decode(state)
        mac, blob = raw[:32], raw[32:]
        calc = hmac.new(self.STATE_SECRET, blob, hashlib.sha256).digest()
        if not hmac.compare_digest(mac, calc):
            raise ValueError("bad state")
        data = json.loads(blob.decode())
        nxt = data.get('next') or '/admin/'
        # Very light safety: do not allow absolute external redirects
        if nxt.startswith('http://') or nxt.startswith('https://'):
            return '/admin/'
        return nxt

    def _save_user_info(self, user_info):
        email = (user_info.get('emails') or [None])[0]
        given_name = user_info.get('given_name')
        if not email:
            raise ValidationError("Email not found in B2C claims")

        # Only allow pre-existing superusers or a whitelisted check
        if not User.objects.filter(email=email, is_active=True, is_superuser=True).exists():
            raise PermissionDenied("Access Denied: You are not allowed to sign up.")

        user, _created = User.objects.get_or_create(
            email=email,
            defaults={
                'username': email,
                'first_name': given_name or '',
                'is_staff': True,
                'is_superuser': True,
            },
        )
        # Ensure flags (in case user existed)
        user.is_staff = True
        user.is_superuser = True
        user.save()
        return user

    def _login_user(self, request, user):
        user.backend = "django.contrib.auth.backends.ModelBackend"
        login(request, user)
