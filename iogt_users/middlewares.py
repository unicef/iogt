from django.shortcuts import redirect
from django.urls import resolve

from home.models import SiteSettings


class RegistrationSurveyRedirectMiddleware:
    """
    The purpose of this middleware is to make the registration survey form
    mandatory. See https://github.com/unicef/iogt/issues/113 for details
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        site_settings = SiteSettings.for_request(request)
        if site_settings.registration_survey:
            is_registration_survey_url = request.path_info == site_settings.registration_survey.url
        else:
            is_registration_survey_url = False

        allowed_url_names = ['account_logout']
        current_url = resolve(request.path_info).url_name
        is_url_allowed = current_url in allowed_url_names or is_registration_survey_url

        is_registered_user = not request.user.is_anonymous

        if is_registered_user and not request.user.has_filled_registration_survey \
                and not is_url_allowed and site_settings.registration_survey:
            site_settings = SiteSettings.for_request(request)
            return redirect(site_settings.registration_survey.url)

        return self.get_response(request)
