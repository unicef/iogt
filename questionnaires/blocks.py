from django.utils.translation import gettext_lazy as _

from wagtail.core import blocks
from wagtail.core.fields import StreamField


class SkipState:
    NEXT = "next"
    END = "end"
    QUESTION = "question"


VALID_SKIP_SELECTORS = [
    'checkbox', 'checkboxes', 'date', 'datetime', 'email', 'singleline', 'multiline', 'positivenumber', 'radio', 'url',
]
VALID_SKIP_LOGIC = VALID_SKIP_SELECTORS


class SkipLogicField(StreamField):
    def __init__(self, *args, **kwargs):
        args = [blocks.StreamBlock([("skip_logic", SkipLogicBlock())])]
        kwargs.update(
            {
                "verbose_name": _("Answer options"),
                "blank": True,
            }
        )
        super().__init__(*args, **kwargs)


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
    question = blocks.IntegerBlock(required=False)
