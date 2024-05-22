from wagtail import blocks

from messaging.views import chatbot_channel_viewset


ChatBotChannelChooserBlock = chatbot_channel_viewset.get_block_class(
    name="ChatBotChannelChooserBlock",
    module_path="messaging.blocks",
)


class ChatBotButtonBlock(blocks.StructBlock):
    subject = blocks.CharBlock()
    button_text = blocks.CharBlock()
    trigger_string = blocks.CharBlock()
    channel = ChatBotChannelChooserBlock()

    class Meta:
        icon = "mail"
        template = "messaging/blocks/chatbot_button.html"
