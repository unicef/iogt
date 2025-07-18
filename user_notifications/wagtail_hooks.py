from wagtail.contrib.modeladmin.options import (
    ModelAdmin, ModelAdminGroup, modeladmin_register
)
from .models import NotificationLog, NotificationPreference, NotificationTag
from admin_notifications.wagtail_hooks import NotificationModelAdmin

class NotificationTagAdmin(ModelAdmin):
    model = NotificationTag
    menu_label = "Notification Tags"
    menu_icon = "tag"
    list_display = ("name", "slug")


class NotificationPreferenceAdmin(ModelAdmin):
    model = NotificationPreference
    menu_label = "Notification Preferences"
    menu_icon = "bell"

    def get_content_tags(self, obj):
        return ", ".join([tag.name for tag in obj.content_tags.all()])

    get_content_tags.short_description = "Tags"
    list_display = ("user", "receive_notifications", "preferred_language", "get_content_tags")
    search_fields = ("user__username", "user__email", "preferred_language")
    list_filter = ('preferred_language', 'content_tags')




# class NotificationsGroup(ModelAdminGroup):
#     menu_label = "User Notifications"
#     menu_icon = "mail"
#     menu_order = 200
#     items = (NotificationTagAdmin, NotificationPreferenceAdmin)

class NotificationLogAdmin(ModelAdmin):
    model = NotificationLog
    menu_label = "Notification Logs"
    menu_icon = "list-ul"  # Wagtail icon name
    menu_order = 200
    list_display = ("notification_key", "user", "state", "tags", "received_at")
    search_fields = ("notification_key", "user__username", "user__email", "tags")


class NotificationsParentGroup(ModelAdminGroup):
    menu_label = "Notifications"
    menu_icon = "bell"
    items = (
        NotificationTagAdmin,
        NotificationPreferenceAdmin,
        NotificationModelAdmin,
        NotificationLogAdmin
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