from wagtail import hooks
from wagtail.contrib.modeladmin.options import (
    ModelAdminGroup,
    ModelAdmin,
    modeladmin_register,
)

from messaging.models import ChatbotChannel
from messaging.views import chatbot_channel_viewset


@hooks.register("register_admin_viewset")
def register_chatbot_channel_viewset():
    return chatbot_channel_viewset


class ChatbotChannelAdmin(ModelAdmin):
    model = ChatbotChannel
    menu_label = 'Chatbot Channels'
    menu_icon = 'code'
    index_template_name = 'messaging/chatbotchannel/index.html'


class ChatbotGroup(ModelAdminGroup):
    menu_label = 'Chatbot'
    menu_icon = 'code'
    items = (ChatbotChannelAdmin,)


modeladmin_register(ChatbotGroup)
