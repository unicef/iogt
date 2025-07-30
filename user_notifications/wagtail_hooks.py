from wagtail.contrib.modeladmin.options import (
    ModelAdmin, ModelAdminGroup, modeladmin_register
)
from .models import NotificationLog, NotificationPreference, NotificationTag, UserNotificationTemplate
from admin_notifications.wagtail_hooks import NotificationModelAdmin

class NotificationTagAdmin(ModelAdmin):
    model = NotificationTag
    menu_label = "Notification Tags"
    menu_icon = "tag"
    list_display = ("name", "slug")


class NotificationPreferenceAdmin(ModelAdmin):
    model = NotificationPreference
    menu_label = "Notification Preferences"
    menu_icon = "user"

    def get_content_tags(self, obj):
        return ", ".join([tag.name for tag in obj.content_tags.all()])

    get_content_tags.short_description = "Tags"
    list_display = ("user", "receive_notifications", "preferred_language", "get_content_tags")
    search_fields = ("user__username", "user__email", "preferred_language")
    list_filter = ('preferred_language', 'content_tags')


class NotificationLogAdmin(ModelAdmin):
    model = NotificationLog
    menu_label = "Notification Logs"
    menu_icon = "list-ul"  # Wagtail icon name
    menu_order = 200
    list_display = ("notification_key", "user", "state", "get_notification_url", "get_is_clicked", "tags", "received_at")
    search_fields = ("notification_key", "user__username", "user__email", "tags", "get_notification_url")
    
    def get_is_clicked(self, obj):
        try:
            return obj.notification.meta.is_clicked
        except AttributeError:
            return False  # or 'N/A' if you prefer
    
    get_is_clicked.boolean = True  # shows a checkmark in admin
    get_is_clicked.short_description = 'Is Clicked'

    def get_notification_url(self, obj):
        try:
            url =  obj.notification.data["url"]
            return url
        except AttributeError:
            return ""
    get_notification_url.short_description = "Target URL"



class UserNotificationTemplateAdmin(ModelAdmin):
    model = UserNotificationTemplate
    menu_label = "User Notification Template"
    menu_icon = "tag"
    list_display = ("title", "message", "active", "updated_at")


class NotificationsParentGroup(ModelAdminGroup):
    menu_label = "Notifications"
    menu_icon = "bell"
    items = (
        NotificationTagAdmin,
        NotificationPreferenceAdmin,
        NotificationModelAdmin,
        NotificationLogAdmin,
        UserNotificationTemplateAdmin
    )



# class NotificationPreferenceAdmin(ModelAdmin):
#     model = NotificationPreference
#     menu_label = "Notification Preferences"
#     menu_icon = "bell"  # Wagtail icon name
#     list_display = ("user", "receive_notifications")
#     search_fields = ("user__username", "user__email")




modeladmin_register(NotificationsParentGroup)
# modeladmin_register(NotificationPreferenceAdmin)
# modeladmin_register(NotificationLogAdmin)