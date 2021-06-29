from django.contrib.auth import get_user_model
from wagtail.contrib.modeladmin.options import ModelAdmin, modeladmin_register, ModelAdminGroup

from home.models import SiteSettings
from iogt_users.filters import GroupsFilter


class UsersExportAdmin(ModelAdmin):
    model = get_user_model()
    menu_label = 'Users Data'
    menu_icon = 'user'
    list_display = ('username', 'date_joined', 'is_staff', 'is_active')
    list_filter = (GroupsFilter, 'date_joined', 'is_staff', 'is_active')
    form_fields_exclude = ('password', 'last_login', 'is_superuser', 'groups', 'user_permissions')
    search_fields = ('username',)
    list_export = ('username', 'first_name', 'last_name', 'email', 'is_staff', 'is_active', 'date_joined',
                   'terms_accepted', 'has_filled_registration_survey', 'registration_survey_response',)
    add_to_settings_menu = True
    list_per_page = 20
    menu_order = 1001

    def registration_survey_response(self, obj):
        site_settings = SiteSettings.get_for_default_site()
        user_submission = obj.usersubmission_set.filter(
            page__pk=site_settings.registration_survey.pk).order_by('-submit_time').first()
        return user_submission.form_data if user_submission else ''


class ExportGroup(ModelAdminGroup):
    menu_label = 'Export'
    menu_icon = 'download'
    menu_order = 1000
    items = (UsersExportAdmin,)


modeladmin_register(ExportGroup)
