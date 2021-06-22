from wagtail.contrib.modeladmin.options import ModelAdmin, modeladmin_register

from .models import Survey, Poll


class SurveyAdmin(ModelAdmin):
    model = Survey
    menu_label = "Surveys"
    menu_icon = "doc-full"
    add_to_settings_menu = False
    exclude_from_explorer = False


class PollAdmin(ModelAdmin):
    model = Poll
    menu_label = "Polls"
    menu_icon = "doc-full"
    add_to_settings_menu = False
    exclude_from_explorer = False


modeladmin_register(SurveyAdmin)
modeladmin_register(PollAdmin)
