from wagtail.contrib.modeladmin.options import ModelAdmin, modeladmin_register
from wagtail.core import hooks

from notifications.models import Notification
from notifications.views import CreateNotificationView


class NotificationModelAdmin(ModelAdmin):
    model = Notification
    menu_label = 'Notifications'
    menu_icon = 'mail'
    list_display = ('head', 'body', 'url',)
    list_filter = ('groups',)
    search_fields = ('head', 'body', 'url',)
    menu_order = 601
    create_view_class = CreateNotificationView


modeladmin_register(NotificationModelAdmin)
