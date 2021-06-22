from django import forms
from wagtail.core import blocks

from .models import ChatbotChannel


class ChannelChooserBlock(blocks.ChooserBlock):
    target_model = ChatbotChannel
    widget = forms.Select


class ChatBotBlock(blocks.StructBlock):
    user_facing_string = blocks.CharBlock()
    trigger_string = blocks.CharBlock()
    channel = ChannelChooserBlock()
