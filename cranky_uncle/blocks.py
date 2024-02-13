from django import forms
from wagtail.core import blocks


class CrankyUncleChannelChooserBlock(blocks.ChooserBlock):
    from .models import CrankyUncleChannel

    target_model = CrankyUncleChannel
    widget = forms.Select


class CrankyUncleButtonBlock(blocks.StructBlock):
    subject = blocks.CharBlock()
    button_text = blocks.CharBlock()
    trigger_string = blocks.CharBlock()
    cranky_uncle_channel = CrankyUncleChannelChooserBlock()

    class Meta:
        icon = 'tag'
        # template = ''
