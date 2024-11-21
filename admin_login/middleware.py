from django.shortcuts import redirect
from django.urls import reverse
from django.http import HttpResponseForbidden


class CustomAdminLoginRequiredMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Check if the request path is part of the Wagtail admin
        if request.path.startswith('/admin/') and not request.user.is_authenticated:
            # Redirect non-authenticated users to a custom login URL
            return redirect('/admin/signup-as-admin/')
        response = self.get_response(request)
        return response
