from django.contrib import admin

from .models import InteractiveChannel


@admin.register(InteractiveChannel)
class InteractiveChannelAdmin(admin.ModelAdmin):
    list_display = ("id", "display_name", "request_url")
