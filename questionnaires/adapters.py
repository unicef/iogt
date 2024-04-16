from functools import cached_property

from django import forms
from wagtail.admin.staticfiles import versioned_static
from wagtail.blocks.stream_block import StreamBlockAdapter
from wagtail.blocks.struct_block import StructBlockAdapter
from wagtail.widget_adapters import WidgetAdapter


class SkipLogicStreamBlockAdapter(StreamBlockAdapter):
    js_constructor = 'questionnaires.blocks.SkipLogicStreamBlock'

    @cached_property
    def media(self):
        media = super().media
        return forms.Media(
            js=media._js + [versioned_static('js/blocks/skip_logic_stream_block.js')],
            css=media._css
        )


class SkipLogicBlockAdapter(StructBlockAdapter):
    js_constructor = 'questionnaires.blocks.SkipLogicBlock'

    @cached_property
    def media(self):
        media = super().media
        return forms.Media(
            js=media._js + [versioned_static('js/blocks/skip_logic_block.js')],
            css=media._css
        )


class SelectAndHiddenWidgetAdapter(WidgetAdapter):
    js_constructor = 'questionnaires.widgets.SelectAndHiddenWidget'

    class Media:
        js = [versioned_static('js/widgets/select_and_hidden_widget.js')]
