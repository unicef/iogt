from django.urls import reverse
from wagtail.contrib.modeladmin.options import ModelAdmin, modeladmin_register

from .models import Poll, Survey


class PollAdmin(ModelAdmin):
    model = Poll
    menu_label = "Polls"
    menu_icon = "doc-full"
    add_to_settings_menu = False
    list_display = ("entries", "live")
    exclude_from_explorer = False

    def entries(self, obj, *args, **kwargs):
        url = reverse("question-results-admin", args=(obj.id,))
        return f'<a href="{url}">{obj}</a>'

    entries.allow_tags = True
    entries.short_description = "Title"


class SurveyAdmin(ModelAdmin):
    model = Survey
    menu_label = "Surveys"
    menu_icon = "doc-full"
    add_to_settings_menu = False
    exclude_from_explorer = False


modeladmin_register(SurveyAdmin)
