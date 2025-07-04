from django.conf import settings
from wagtail.contrib.modeladmin.options import ModelAdmin, modeladmin_register



from admin_notifications.models import AdminNotification
from admin_notifications.views import CreateNotificationView
from user_notifications.models import NotificationPreference


class NotificationModelAdmin(ModelAdmin):
    model = AdminNotification
    menu_label = 'Admin Notifications'
    menu_icon = 'mail'
    list_display = ('head', 'body', 'url',)
    list_filter = ('groups',)
    search_fields = ('head', 'body', 'url',)
    menu_order = 601
    create_view_class = CreateNotificationView


class NotificationPreferenceAdmin(ModelAdmin):
    model = NotificationPreference
    menu_label = "Notification Preferences"
    menu_icon = "bell"  # Wagtail icon name
    list_display = ("user", "receive_notifications")
    search_fields = ("user__username", "user__email")

# Register with Wagtail admin
if settings.PUSH_NOTIFICATION:
    modeladmin_register(NotificationModelAdmin)

modeladmin_register(NotificationPreferenceAdmin)
