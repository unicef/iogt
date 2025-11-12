from functools import cached_property

from django.conf import settings
from django.contrib.auth import get_user_model
from django.db.models import Prefetch
from django.urls import reverse
from django.utils import timezone
from wagtail_modeladmin.helpers import ButtonHelper
from wagtail_modeladmin.options import ModelAdmin, modeladmin_register
from wagtail_modeladmin.helpers.permission import PermissionHelper

from home.models import SiteSettings
from .models import DeletedUserLog
from iogt_users.filters import GroupsFilter
from questionnaires.models import UserSubmission


class UserButtonHelper(ButtonHelper):
    view_button_classnames = ["button-small", "icon", "icon-form"]

    def form_data_button(self, obj):
        text = "Form Data"
        return {
            "url": f'{reverse("form_data_per_user")}?user_id={obj.id}',
            "label": text,
            "classname": self.finalise_classname(self.view_button_classnames),
            "title": text,
        }

    def get_buttons_for_obj(self, obj, exclude=None, classnames_add=None, classnames_exclude=None):
        btns = super().get_buttons_for_obj(obj, exclude, classnames_add, classnames_exclude)
        btns.append(self.form_data_button(obj))
        return btns


class UsersExportAdmin(ModelAdmin):
    model = get_user_model()
    menu_label = 'Export/Import Users'
    menu_icon = 'user'
    list_display = ('username', 'display_name', 'date_joined', 'is_staff', 'is_active')
    list_filter = (GroupsFilter, 'date_joined', 'is_staff', 'is_active')
    form_fields_exclude = ('password', 'last_login', 'is_superuser', 'groups', 'user_permissions')
    search_fields = ('username',)
    list_export = ('username', 'display_name', 'first_name', 'last_name', 'email', 'is_staff', 'is_active',
                   'date_joined', 'terms_accepted', 'has_filled_registration_survey', 'registration_survey_response',)
    add_to_settings_menu = True
    list_per_page = 20
    menu_order = 601
    button_helper_class = UserButtonHelper

    def registration_survey_response(self, obj):
        user_submissions = obj.user_submissions

        return user_submissions[0].form_data if user_submissions else ''

    @cached_property
    def get_registration_survey_ids(self):
        ids = []
        registration_survey = SiteSettings.get_for_default_site().registration_survey
        if registration_survey:
            ids = registration_survey.get_translations(inclusive=True).values_list('id', flat=True)

        return ids

    @property
    def export_filename(self):
        return f'users_{timezone.now().strftime(settings.EXPORT_FILENAME_TIMESTAMP_FORMAT)}'

    def get_queryset(self, request):
        qs = super().get_queryset(request)

        ids = self.get_registration_survey_ids
        return qs.prefetch_related(
            Prefetch(
                'usersubmission_set',
                queryset=UserSubmission.objects.filter(page__pk__in=ids),
                to_attr='user_submissions'
            )
        )
    

class DeletedLogsPermissionHelper(PermissionHelper):
    def user_can_create(self, user):
        return False
    def user_can_delete_obj(self, user, obj):
        return False


class DeletedUserLogAdmin(ModelAdmin):
    model = DeletedUserLog
    menu_label = "Deleted Users"
    menu_icon = "user"
    list_display = ("user_id", "deletion_time", "reason")
    search_fields = ("user_id",)
    permission_helper_class = DeletedLogsPermissionHelper

modeladmin_register(UsersExportAdmin)
modeladmin_register(DeletedUserLogAdmin)
