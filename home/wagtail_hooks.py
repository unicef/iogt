from wagtail.core import hooks
from wagtail.core.models import Site
from wagtail.contrib.modeladmin.options import ModelAdmin, modeladmin_register

from .models import SiteSettings


class SiteSettingsAdmin(ModelAdmin):
    model = SiteSettings

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        site = Site.find_for_request(request)
        qs = qs.filter(site=site)
        return qs


modeladmin_register(SiteSettingsAdmin)


@hooks.register('construct_main_menu')
def hide_site_settings_in_main_item(request, menu_items):
    if request.user.is_superuser:
        menu_items[:] = [item for item in menu_items if item.name != 'site-settings']


@hooks.register('construct_settings_menu')
def hide_site_settings_in_settings_menu(request, menu_items):
    if request.user.is_superuser:
        return

    menu_items[:] = [item for item in menu_items if item.name != 'site-settings']
