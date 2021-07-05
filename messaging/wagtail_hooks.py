from wagtail.contrib.modeladmin.options import (
    ModelAdminGroup, ModelAdmin, modeladmin_register)
from .models import ChatbotChannel


class ChatbotChannelAdmin(ModelAdmin):
    model = ChatbotChannel
    menu_label = 'Chatbot Channels'
    menu_icon = 'code'


class ChatbotGroup(ModelAdminGroup):
    menu_label = 'Chatbot'
    menu_icon = 'code'
    items = (ChatbotChannelAdmin,)


modeladmin_register(ChatbotGroup)
