from django import forms
from wagtail.core import blocks

from .models import ChatbotChannel


class ChatBotChannelChooserBlock(blocks.ChooserBlock):
    target_model = ChatbotChannel
    widget = forms.Select


class ChatBotButtonBlock(blocks.StructBlock):
    button_text = blocks.CharBlock()
    trigger_string = blocks.CharBlock()
    channel = ChatBotChannelChooserBlock()
