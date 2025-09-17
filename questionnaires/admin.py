from wagtail_modeladmin.helpers import ButtonHelper
from wagtail_modeladmin.options import ModelAdmin, modeladmin_register
from django.utils.translation import get_language_info
from django.contrib.humanize.templatetags.humanize import naturaltime


from .models import Survey, Poll, Quiz


class HideCreateButtonHelper(ButtonHelper):

    def add_button(self, classnames_add=None, classnames_exclude=None):
        return None

class SurveyAdmin(ModelAdmin):
    model = Survey
    menu_label = "Surveys"
    menu_icon = "doc-full"
    add_to_settings_menu = False
    exclude_from_explorer = False
    button_helper_class = HideCreateButtonHelper
    list_display = ("title", "get_updated", "get_status", "get_locale",)
  
  
    def get_updated(self, obj):
        if obj.latest_revision_created_at:
            return naturaltime(obj.latest_revision_created_at)
        return "-"
    get_updated.short_description = "Updated"
    get_updated.admin_order_field = "last_published_at"

    def get_status(self, obj):
        return "Live" if obj.live else "Draft"
    get_status.short_description = "Status"
    get_status.admin_order_field = "live" 
    

    def get_locale(self, obj):
        if obj.locale:
            info = get_language_info(obj.locale.language_code)
            return info["name_local"]
        return "-"
    get_locale.short_description = "Locale"
    get_locale.admin_order_field = "locale"


class PollAdmin(ModelAdmin):
    model = Poll
    menu_label = "Polls"
    menu_icon = "doc-full"
    add_to_settings_menu = False
    exclude_from_explorer = False
    button_helper_class = HideCreateButtonHelper
    list_display = ("title", "get_updated", "get_status", "get_locale",)
    def get_updated(self, obj):
        if obj.latest_revision_created_at:
            return naturaltime(obj.latest_revision_created_at)
        return "-"
    get_updated.short_description = "Updated"
    get_updated.admin_order_field = "last_published_at"

    def get_status(self, obj):
        return "Live" if obj.live else "Draft"
    get_status.short_description = "Status"
    get_status.admin_order_field = "live" 
    

    def get_locale(self, obj):
        if obj.locale:
            info = get_language_info(obj.locale.language_code)
            return info["name_local"]
        return "-"
    get_locale.short_description = "Locale"
    get_locale.admin_order_field = "locale"



class QuizAdmin(ModelAdmin):
    model = Quiz
    menu_label = "Quizzes"
    menu_icon = "doc-full"
    add_to_settings_menu = False
    exclude_from_explorer = False
    button_helper_class = HideCreateButtonHelper
    list_display = ("title", "get_updated", "get_status", "get_locale",)
    def get_updated(self, obj):
        if obj.latest_revision_created_at:
            return naturaltime(obj.latest_revision_created_at)
        return "-"
    get_updated.short_description = "Updated"
    get_updated.admin_order_field = "last_published_at"

    def get_status(self, obj):
        return "Live" if obj.live else "Draft"
    get_status.short_description = "Status"
    get_status.admin_order_field = "live" 

    def get_locale(self, obj):
        if obj.locale:
            info = get_language_info(obj.locale.language_code)
            return info["name_local"]
        return "-"
    get_locale.short_description = "Locale"
    get_locale.admin_order_field = "locale"


modeladmin_register(SurveyAdmin)
modeladmin_register(PollAdmin)
modeladmin_register(QuizAdmin)
