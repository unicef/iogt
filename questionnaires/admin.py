from wagtail.contrib.modeladmin.helpers import ButtonHelper
from wagtail.contrib.modeladmin.options import ModelAdmin, modeladmin_register

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


class PollAdmin(ModelAdmin):
    model = Poll
    menu_label = "Polls"
    menu_icon = "doc-full"
    add_to_settings_menu = False
    exclude_from_explorer = False
    button_helper_class = HideCreateButtonHelper


class QuizAdmin(ModelAdmin):
    model = Quiz
    menu_label = "Quizzes"
    menu_icon = "doc-full"
    add_to_settings_menu = False
    exclude_from_explorer = False
    button_helper_class = HideCreateButtonHelper


modeladmin_register(SurveyAdmin)
modeladmin_register(PollAdmin)
modeladmin_register(QuizAdmin)
