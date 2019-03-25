from django.conf import settings


class ReferrerPolicyMiddleware(object):
    def process_response(self, request, response):
        response["Referrer-Policy"] = settings.REFERRER_POLICY
        return response
