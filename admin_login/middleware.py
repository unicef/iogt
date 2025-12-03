from django.shortcuts import redirect
from django.urls import reverse

class EnforceB2CForAdminMiddleware:
    """
    If a user is authenticated but not via B2C, block entry to Wagtail admin and
    redirect them to the B2C login with ?next=...
    """

    def __init__(self, get_response):
        self.get_response = get_response
        self.admin_prefix = '/admin/'  # adjust if you've customized WAGTAIL_ADMIN_URL

        # Allowlist admin paths that must remain accessible:
        self.allowlist = {
            '/admin/login/',      # your B2C login override
            '/admin/logout/',
            '/admin/shell/',      # optional, remove if not used
            '/admin/api/',        # optional, remove if not used
            '/admin/static/',     # static/assets
        }

    def __call__(self, request):
        path = request.path

        # Only guard Wagtail admin area
        if path.startswith(self.admin_prefix):
            # Skip allowlisted subpaths (avoid loops and let assets load)
            for allowed in self.allowlist:
                if path.startswith(allowed):
                    return self.get_response(request)

            # If user is authenticated but not via B2C, redirect to B2C login
            if request.user.is_authenticated:
                if request.session.get('auth_via') != 'b2c':
                    b2c_login_url = reverse('azure_signup_view')
                    return redirect(f"{b2c_login_url}?next={request.get_full_path()}")

            # (Unauthenticated users will be challenged by Wagtail itself,
            # which we already pointed to the B2C login via WAGTAIL_LOGIN_URL.)

        return self.get_response(request)
