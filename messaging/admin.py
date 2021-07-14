# -*- coding: utf-8 -*-
from django.contrib import admin

from .models import ChatbotChannel, Thread, UserThread, Message


@admin.register(ChatbotChannel)
class ChatbotChannelAdmin(admin.ModelAdmin):
    list_display = ('id', 'display_name', 'request_url')


@admin.register(Thread)
class ThreadAdmin(admin.ModelAdmin):
    list_display = ('id', 'last_message_at', 'subject', 'uuid', 'chatbot')
    list_filter = ('last_message_at', 'chatbot')
    raw_id_fields = ('users',)


@admin.register(UserThread)
class UserThreadAdmin(admin.ModelAdmin):
    list_display = ('id', 'is_active', 'is_read', 'thread', 'user')
    list_filter = ('is_active', 'is_read')


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'quick_replies',
        'rapidpro_message_id',
        'sent_at',
        'text',
        'thread',
        'sender',
    )
    list_filter = ('sent_at', )
