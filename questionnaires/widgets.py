from django import forms
from wagtail.core.telepath import register

from questionnaires.adapters import SelectAndHiddenWidgetAdapter


class SelectAndHiddenWidget(forms.MultiWidget):
    def __init__(self, *args, **kwargs):
        widgets = [forms.HiddenInput, forms.Select]
        super(SelectAndHiddenWidget, self).__init__(
            widgets=widgets,
            *args,
            **kwargs
        )

    def decompress(self, value):
        return [value, None]

    def value_from_datadict(self, *args):
        value = super(SelectAndHiddenWidget, self).value_from_datadict(*args)
        return value[1]


register(SelectAndHiddenWidgetAdapter(), SelectAndHiddenWidget)
