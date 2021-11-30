from functools import cached_property

from django.conf import settings
from django.contrib.auth import get_user_model
from django.db.models import Prefetch
from django.utils import timezone
from wagtail.contrib.modeladmin.options import ModelAdmin, modeladmin_register

from home.models import SiteSettings
from iogt_users.filters import GroupsFilter
from questionnaires.models import UserSubmission


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
        """
        Returns a QuerySet of all model instances that can be edited by the
        admin site.
        """
        qs = self.model._default_manager.get_queryset()
        ordering = self.get_ordering(request)
        if ordering:
            qs = qs.order_by(*ordering)

        ids = self.get_registration_survey_ids
        return qs.prefetch_related(
            Prefetch(
                'usersubmission_set',
                queryset=UserSubmission.objects.filter(page__pk__in=ids),
                to_attr='user_submissions'
            )
        )


modeladmin_register(UsersExportAdmin)
