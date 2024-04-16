from django import forms
from wagtail import blocks

from .models import ChatbotChannel


class ChatBotChannelChooserBlock(blocks.ChooserBlock):
    target_model = ChatbotChannel
    widget = forms.Select


class ChatBotButtonBlock(blocks.StructBlock):
    subject = blocks.CharBlock()
    button_text = blocks.CharBlock()
    trigger_string = blocks.CharBlock()
    channel = ChatBotChannelChooserBlock()

    class Meta:
        icon = 'code'
        template = 'messaging/blocks/chatbot_button.html'
