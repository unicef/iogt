from wagtail.contrib.modeladmin.options import ModelAdmin, modeladmin_register

from .models import Poll


class PollPageAdmin(ModelAdmin):

    model = Poll
    menu_label = "Polls"
    menu_icon = "placeholder"
    menu_order = 200
    add_to_settings_menu = False
    exclude_from_explorer = False
    list_display = ("title",)
    search_fields = ("title",)


modeladmin_register(PollPageAdmin)
