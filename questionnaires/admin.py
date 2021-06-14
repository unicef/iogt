from django.urls import reverse
from wagtail.contrib.modeladmin.options import ModelAdmin

from .models import Poll


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
