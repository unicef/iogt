from django.conf import settings
from django.contrib.auth import get_user_model
from django.utils import timezone
from wagtail.contrib.modeladmin.options import ModelAdmin, modeladmin_register

from home.models import SiteSettings
from iogt_users.filters import GroupsFilter


class UsersExportAdmin(ModelAdmin):
    model = get_user_model()
    menu_label = 'Export/Import Users'
    menu_icon = 'user'
    list_display = ('username', 'date_joined', 'is_staff', 'is_active')
    list_filter = (GroupsFilter, 'date_joined', 'is_staff', 'is_active')
    form_fields_exclude = ('password', 'last_login', 'is_superuser', 'groups', 'user_permissions')
    search_fields = ('username',)
    list_export = ('username', 'first_name', 'last_name', 'email', 'is_staff', 'is_active', 'date_joined',
                   'terms_accepted', 'has_filled_registration_survey', 'registration_survey_response',)
    add_to_settings_menu = True
    list_per_page = 20
    menu_order = 601

    def registration_survey_response(self, obj):
        registration_survey = SiteSettings.get_for_default_site().registration_survey
        user_submission = None
        if registration_survey:
            ids = registration_survey.get_translations(inclusive=True).values_list('id', flat=True)
            user_submission = obj.usersubmission_set.filter(page__pk__in=ids).order_by('submit_time').first()

        return user_submission.form_data if user_submission else ''

    @property
    def export_filename(self):
        return f'users_{timezone.now().strftime(settings.EXPORT_FILENAME_TIMESTAMP_FORMAT)}'


modeladmin_register(UsersExportAdmin)
