from django import forms
from wagtail import blocks
from wagtail.snippets.blocks import SnippetChooserBlock


class ChatBotChannelChooserBlock(SnippetChooserBlock):
    def __init__(self, **kwargs):
        super().__init__(target_model='messaging.ChatbotChannel', **kwargs)


class ChatBotButtonBlock(blocks.StructBlock):
    subject = blocks.CharBlock()
    button_text = blocks.CharBlock()
    trigger_string = blocks.CharBlock()
    channel = ChatBotChannelChooserBlock()

    class Meta:
        icon = 'code'
        template = 'messaging/blocks/chatbot_button.html'
