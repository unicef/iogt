from django.utils.timezone import now
from .models import PageVisit

class TrackFrontendPageVisitsMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)

        if request.user.is_authenticated:
            path = request.path
            print('path', path)

            # Only track GET requests
            if request.method != "GET":
                return response

            # Exclude paths that are not real pages
            excluded_paths = [
                "/admin",
                "/static",
                "/media",
                "/api",
                "/my-activity",
                "/users/profile/my-activity"
            ]
            if "my-activity" in path or path.startswith("/admin") or path.startswith("/static") or path.startswith("/media") or path.startswith("/api"):
                return response

            # Exclude AJAX requests
            if request.headers.get("x-requested-with") == "XMLHttpRequest":
                return response

            # Only track HTML page loads
            accept_header = request.headers.get("Accept", "")
            if "text/html" not in accept_header:
                return response

            # Prevent double counts for rapid reloads
            last_visit = PageVisit.objects.filter(user=request.user, page_slug=path)\
                                          .order_by("-timestamp").first()
            if not last_visit or (now() - last_visit.timestamp).total_seconds() > 10:
                PageVisit.objects.create(
                    user=request.user,
                    page_slug=path,
                    timestamp=now()
                )

        return response
