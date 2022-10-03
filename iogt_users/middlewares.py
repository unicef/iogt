from django.contrib import messages
from django.shortcuts import redirect
from django.urls import resolve, Resolver404, translate_url
from django.utils import translation
from django.utils.translation import gettext as _

from home.models import SiteSettings


class RegistrationSurveyRedirectMiddleware:
    """
    The purpose of this middleware is to make the registration survey form
    mandatory. See https://github.com/unicef/iogt/issues/113 for details
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if not request.user.is_superuser:
            return self.get_response(request)

        request_path = request.path_info
        registration_survey = SiteSettings.for_request(request).registration_survey
        if registration_survey:
            registration_survey = registration_survey.localized
            is_registration_survey_url = request_path == registration_survey.url
        else:
            is_registration_survey_url = False

        allowed_url_names = ['account_logout']
        language = translation.get_language()
        try:
            current_url = resolve(request_path).url_name
        except Resolver404:
            current_url = translate_url(request_path, language)
        is_url_allowed = current_url in allowed_url_names or is_registration_survey_url

        user = request.user
        is_registered_user = not user.is_anonymous

        language = translation.get_language()
        if (request_path.startswith(('/media/', f'/{language}/images/', f'/{language}/jsi18n/'))
                or is_url_allowed
                or not is_registered_user):
            return self.get_response(request)

        should_redirect_to_registration_survey = False
        if (not user.has_filled_registration_survey
                and registration_survey
                and registration_survey.has_required_fields()):
            should_redirect_to_registration_survey = True
            if user.has_viewed_registration_survey and not user.has_filled_registration_survey:
                messages.add_message(
                    request, messages.ERROR, _('Please complete the questions marked as required to continue'))

        elif (not user.has_filled_registration_survey
                and not user.has_viewed_registration_survey
                and registration_survey):
            should_redirect_to_registration_survey = True

        if should_redirect_to_registration_survey:
            user.has_viewed_registration_survey = True
            user.save(update_fields=['has_viewed_registration_survey'])
            return redirect(registration_survey.localized.url)

        return self.get_response(request)
