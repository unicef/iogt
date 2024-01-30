from django.contrib import admin

from .models import CrankyUncleChannel


@admin.register(CrankyUncleChannel)
class CrankyUncleChannelAdmin(admin.ModelAdmin):
    list_display = ('id', 'display_name', 'request_url')
