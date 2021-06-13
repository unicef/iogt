from django import forms
from django.utils.translation import ugettext_lazy as _

from .models import Choice

# TODO: validation doesn't catch when choice is not selected


class VoteForm(forms.Form):
    choice = forms.MultipleChoiceField(
        required=True, error_messages={"required": _("You didn't select a choice")}
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["choice"].choices = [(c.pk, c.title) for c in Choice.objects.all()]
