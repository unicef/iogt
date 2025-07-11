from django.conf import settings
from wagtail.contrib.modeladmin.options import ModelAdmin, modeladmin_register
from admin_notifications.models import AdminNotification
from admin_notifications.views import CreateNotificationView


class NotificationModelAdmin(ModelAdmin):
    model = AdminNotification
    menu_label = 'Admin Notifications'
    menu_icon = 'mail'
    list_display = ('head', 'body', 'url',)
    list_filter = ('groups',)
    search_fields = ('head', 'body', 'url',)
    menu_order = 601
    create_view_class = CreateNotificationView

print('status_of_notification', settings.PUSH_NOTIFICATION)


# Register with Wagtail admin
if settings.PUSH_NOTIFICATION:
    modeladmin_register(NotificationModelAdmin)

