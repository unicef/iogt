from django.contrib import admin

from .models import Message, UserThread, ChatbotChannel, Thread


class UserThreadAdmin(admin.ModelAdmin):
    list_display = ["thread", "user", "is_read", "is_active"]
    list_filter = ["is_read", "is_active"]
    raw_id_fields = ["user"]


class MessageAdmin(admin.ModelAdmin):
    list_display = ["thread", "sender", "sent_at"]
    list_filter = ["sent_at", "thread"]
    raw_id_fields = ["sender"]


admin.site.register(Message, MessageAdmin)
admin.site.register(UserThread, UserThreadAdmin)
admin.site.register(ChatbotChannel)
admin.site.register(Thread)
