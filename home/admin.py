from django.contrib import admin
from wagtail.contrib.modeladmin.options import ModelAdmin, modeladmin_register

from home.models import ManifestSettings, SVGToPNGMap


class ManifestSettingsAdmin(ModelAdmin):
    model = ManifestSettings
    menu_label = "Manifest Settings"
    menu_icon = "cog"
    add_to_settings_menu = True
    list_display = ("language", "name")
    exclude_from_explorer = False


modeladmin_register(ManifestSettingsAdmin)


@admin.register(SVGToPNGMap)
class SVGToPNGMapAdmin(admin.ModelAdmin):
    list_display = ('id', 'svg_path', 'fill_color', 'stroke_color', 'png_image_file')


