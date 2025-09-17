from django.utils.html import format_html
from wagtail_modeladmin.options import (
    ModelAdmin, ModelAdminGroup, modeladmin_register
)
from .models import NotificationLog, NotificationPreference, NotificationTag, UserNotificationTemplate
from admin_notifications.wagtail_hooks import NotificationModelAdmin
from django.conf import settings
from wagtail_modeladmin.helpers.permission import PermissionHelper

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


class NotificationLogPermissionHelper(PermissionHelper):
    def user_can_list(self, user):
        return True  
    def user_can_create(self, user):
        return False
    def user_can_edit_obj(self, user, obj):
        return False
    def user_can_delete_obj(self, user, obj):
        return False


class NotificationLogAdmin(ModelAdmin):
    model = NotificationLog
    menu_label = "Notification Logs"
    menu_icon = "list-ul"  # Wagtail icon name
    menu_order = 200
    list_display = ("notification_key", "user", "state", "get_notification_url", "get_is_clicked", "tags", "received_at")
    search_fields = ("notification_key", "user__username", "user__email", "tags")
    list_filter = ("state", "tags", "user")
    ordering = ["-received_at"]
    permission_helper_class = NotificationLogPermissionHelper
    
    def get_is_clicked(self, obj):
        try:
            return obj.notification.meta.is_clicked
        except AttributeError:
            return False  # or 'N/A' if you prefer
    
    get_is_clicked.boolean = True  # shows a checkmark in admin
    get_is_clicked.short_description = 'Is Clicked'

    def get_notification_url(self, obj):
        url = obj.notification.data.get("url") if hasattr(obj.notification, "data") else ""
        if url:
            return format_html('<a href="{}" target="_blank">{}</a>', url, url)
        return "-"
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
        NotificationLogAdmin,
        UserNotificationTemplateAdmin
    )
    if settings.PUSH_NOTIFICATION:
        items += (NotificationModelAdmin,)



# class NotificationPreferenceAdmin(ModelAdmin):
#     model = NotificationPreference
#     menu_label = "Notification Preferences"
#     menu_icon = "bell"  # Wagtail icon name
#     list_display = ("user", "receive_notifications")
#     search_fields = ("user__username", "user__email")




modeladmin_register(NotificationsParentGroup)
# modeladmin_register(NotificationPreferenceAdmin)
# modeladmin_register(NotificationLogAdmin)