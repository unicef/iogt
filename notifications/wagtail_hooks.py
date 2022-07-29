from wagtail.contrib.modeladmin.options import ModelAdmin, modeladmin_register
from wagtail.core import hooks

from notifications.models import Notification
from notifications.views import CreateNotificationView


class NotificationModelAdmin(ModelAdmin):
    model = Notification
    menu_label = 'Notification'
    menu_icon = 'mail'
    list_display = ('head', 'body', 'url',)
    list_filter = ('groups',)
    search_fields = ('head', 'body', 'url',)
    menu_order = 601
    create_view_class = CreateNotificationView


modeladmin_register(NotificationModelAdmin)


@hooks.register('construct_main_menu')
def hide_notification_menu_item_from_unauthorized_users(request, menu_items):
    user = request.user
    if user.is_superuser:
        return

    if request.user.has_perms(['notification.add_notification', 'notification.view_notification']):
        menu_items[:] = [item for item in menu_items if item.name != 'notification']
