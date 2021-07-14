from wagtail.contrib.modeladmin.options import ModelAdmin, modeladmin_register

from home.models import ManifestSettings


class ManifestSettingsAdmin(ModelAdmin):
    model = ManifestSettings
    menu_label = "Manifest Settings"
    menu_icon = "cog"
    add_to_settings_menu = True
    list_display = ("language", "name")
    exclude_from_explorer = False


modeladmin_register(ManifestSettingsAdmin)
