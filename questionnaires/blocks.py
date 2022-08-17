from django.core.exceptions import ValidationError
from django.utils.safestring import mark_safe
from django.utils.translation import gettext_lazy as _

from wagtail.core import blocks
from wagtail.core.fields import StreamField
from wagtail.core.telepath import register

from questionnaires.adapters import SkipLogicStreamBlockAdapter, SkipLogicBlockAdapter
from questionnaires.widgets import SelectAndHiddenWidget


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
                    _('Checkbox must include exactly 2 Skip Logic Options: '
                      'true and false, in that order.')
                )
            )
        })
        super(SkipLogicField, self).__init__(*args, **kwargs)


class SkipLogicStreamBlock(blocks.StreamBlock):
    class Meta:
        form_classname = 'skip-logic-stream-block'


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

    class Meta:
        form_classname = 'skip-logic-block struct-block'


register(SkipLogicStreamBlockAdapter(), SkipLogicStreamBlock)
register(SkipLogicBlockAdapter(), SkipLogicBlock)
