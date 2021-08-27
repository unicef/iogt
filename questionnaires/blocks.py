from django import forms
from django.core.exceptions import ValidationError
from django.templatetags.static import static
from django.utils.safestring import mark_safe
from django.utils.translation import gettext_lazy as _

from wagtail.core import blocks
from wagtail.core.fields import StreamField


class SkipState:
    NEXT = "next"
    END = "end"
    QUESTION = "question"


VALID_SKIP_SELECTORS = [
    'checkbox', 'checkboxes', 'date', 'datetime', 'dropdown', 'email', 'singleline', 'multiline', 'number',
    'positivenumber', 'radio', 'url',
]
VALID_SKIP_LOGIC = VALID_SKIP_SELECTORS


class SkipLogicField(StreamField):
    def __init__(self, *args, **kwargs):
        args = [SkipLogicStreamBlock([('skip_logic', SkipLogicBlock())])]
        kwargs.update({
            'verbose_name': _('Answer options'),
            # Help text is used to display a message for a specific field type.
            # If different help text is required each type might need to be
            # wrapped in a <div id="<field-type>-helptext"> for the frontend
            'help_text': mark_safe(
                '<strong>{}</strong>'.format(
                    _('Checkbox must include only 2 Answer Options. '
                      'true and false in that order.')
                )
            )
        })
        super(SkipLogicField, self).__init__(*args, **kwargs)


class SkipLogicStreamBlock(blocks.StreamBlock):
    @property
    def media(self):
        media = super(SkipLogicStreamBlock, self).media
        media.add_js(
            [static('js/blocks/skiplogic_stream.js')]
        )
        media.add_css(
            {'all': [static('css/blocks/skiplogic.css')]}
        )
        return media

    def js_initializer(self):
        init = super(SkipLogicStreamBlock, self).js_initializer()
        return 'SkipLogic' + init

    class Meta:
        required = False


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


class QuestionSelectBlock(blocks.IntegerBlock):
    def __init__(self, *args, **kwargs):
        super(QuestionSelectBlock, self).__init__(*args, **kwargs)
        self.field.widget = SelectAndHiddenWidget()


class SkipLogicBlock(blocks.StructBlock):
    choice = blocks.CharBlock(required=False)
    skip_logic = blocks.ChoiceBlock(
        choices=[
            (SkipState.NEXT, _("Next default question")),
            (SkipState.END, _("End of survey")),
            (SkipState.QUESTION, _("Another question")),
        ],
        default=SkipState.NEXT,
        required=False,
    )
    question = QuestionSelectBlock(
        required=False,
        help_text=_('Please save the survey as a draft to populate or update the list of questions.'),
    )

    @property
    def media(self):
        return forms.Media(js=[static('js/blocks/skiplogic.js')])

    def js_initializer(self):
        opts = {'validSkipSelectors': VALID_SKIP_SELECTORS}
        return "SkipLogic(%s)" % blocks.utils.js_dict(opts)

    def clean(self, value):
        cleaned_data = super(SkipLogicBlock, self).clean(value)
        logic = cleaned_data['skip_logic']
        if logic == SkipState.QUESTION:
            if not cleaned_data['question']:
                raise ValidationError(
                    'A Question must be selected to progress to.',
                    params={'question': [_('Please select a question.')]}
                )

        if logic in [SkipState.END, SkipState.NEXT]:
            cleaned_data['question'] = None

        return cleaned_data
