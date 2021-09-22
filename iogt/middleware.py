from home.models import SiteSettings


class CacheControlMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)

        if SiteSettings.for_request(request).opt_in_to_google_web_light:
            response['Cache-Control'] = 'no-transform'

        return response
