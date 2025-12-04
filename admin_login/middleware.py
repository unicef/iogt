from django.contrib.auth import logout
from django.shortcuts import redirect
from django.urls import reverse

class EnforceB2CForAdminMiddleware:
    """
    If a user is authenticated but not via B2C, log them out and send them to
    the B2C admin login, keeping ?next= to return to /admin/ after B2C.
    """
    def __init__(self, get_response):
        self.get_response = get_response
        self.admin_prefix = '/admin/'
        self.allowlist = {
            '/admin/login/',      # avoids loop
            '/admin/logout/',
            '/admin/static/',     # assets
            '/admin/autocomplete/',
            '/admin/pages/',
            '/admin/images/',
            '/admin/media/',
            '/admin/documents/',
            '/admin/wagtailsvg/',
            '/admin/snippets/',
            '/admin/translation_manager/',
            '/admin/forms/',
            '/admin/iogt_users/',
        }

    def __call__(self, request):
        path = request.path
        if path.startswith(self.admin_prefix):
            # let allowlisted paths pass
            for allowed in self.allowlist:
                if path.startswith(allowed):
                    return self.get_response(request)

            if request.user.is_authenticated and request.session.get('auth_via') not in ('b2c',):
                logout(request)
                return redirect(reverse('wagtailadmin_login'))

        return self.get_response(request)

