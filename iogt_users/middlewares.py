from django.shortcuts import redirect
from django.urls import resolve


class RegistrationSurveyRedirectMiddleware:
    """
    The purpose of this middleware is to make the registration survey form
    mandatory. See https://github.com/unicef/iogt/issues/113 for details
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        current_url = resolve(request.path_info).url_name
        is_post_registration_survey_url = current_url == 'post_registration_survey'
        is_registered_user = not request.user.is_anonymous

        if is_registered_user and not is_post_registration_survey_url and \
                not request.user.has_filled_registration_survey:
            return redirect('post_registration_survey')

        return self.get_response(request)
