from django.contrib.auth import get_user_model
from wagtail.contrib.modeladmin.options import ModelAdmin, modeladmin_register, ModelAdminGroup

from iogt_users.filters import GroupsFilter


class UsersExportAdmin(ModelAdmin):
    model = get_user_model()
    menu_label = 'Users Data'
    menu_icon = 'user'
    list_display = ('username', 'date_joined', 'is_staff', 'is_active')
    list_filter = (GroupsFilter, 'date_joined', 'is_staff', 'is_active')
    form_fields_exclude = ('password', 'last_login', 'is_superuser', 'groups', 'user_permissions')
    search_fields = ('username',)
    list_export = ('username', 'first_name', 'last_name', 'email', 'is_staff', 'is_active', 'date_joined',
                   'terms_accepted', 'has_filled_registration_survey')
    add_to_settings_menu = True
    list_per_page = 20
    menu_order = 1001


class ExportGroup(ModelAdminGroup):
    menu_label = 'Export'
    menu_icon = 'download'
    menu_order = 1000
    items = (UsersExportAdmin,)


modeladmin_register(ExportGroup)
