from django import forms
from django_comments_xtd.forms import XtdCommentForm as BaseCommentForm
from django.utils.translation import gettext as _

from comments.models import CannedResponse, CommentModeration


class CommentForm(BaseCommentForm):

    def __init__(self, *args, **kwargs):
        super(CommentForm, self).__init__(*args, **kwargs)
        self.fields['email'].initial = 'noreply@example.com'
        self.fields['email'].widget = forms.HiddenInput()

        canned_responses_choices = [(None, 'Select Canned Response')]
        for canned_response in CannedResponse.objects.all():
            text = f"{canned_response.text[:50]}..." if len(canned_response.text) > 50 else canned_response.text
            canned_responses_choices.append((canned_response.id, f'{canned_response.header} - {text}'))

        self.fields['canned_responses'] = forms.ChoiceField(choices=canned_responses_choices, required=False)
        self.fields['canned_responses'].widget.attrs['class'] = 'canned-response-select'

        self.fields['name'].widget = forms.HiddenInput()

        self.fields['followup'].initial = False
        self.fields['followup'].widget = forms.HiddenInput()

        self.fields['post_anonymously'] = forms.BooleanField(
            label=_('Don\'t display my username next to my comment'), required=False)

    def get_comment_create_data(self, site_id=None):
        data = super().get_comment_create_data(site_id=site_id)

        if self.cleaned_data['canned_responses']:
            data['comment'] = f'{data["comment"]} {self.cleaned_data["canned_responses"]}'

        if self.cleaned_data['post_anonymously']:
            data['user_email'] = ''
            data['user_name'] = 'Anonymous'
        return data


class AdminCommentForm(CommentForm):

    def __init__(self, *args, **kwargs):
        super(AdminCommentForm, self).__init__(*args, **kwargs)
        self.is_admin = True


class CommentFilterForm(forms.Form):
    state = forms.ChoiceField(label='Moderation',
                              choices=(('ALL', 'All'),
                                       (CommentModeration.CommentModerationState.UNMODERATED, 'Unmoderated'),
                                       (CommentModeration.CommentModerationState.APPROVED, 'Approved'),
                                       (CommentModeration.CommentModerationState.REJECTED, 'Rejected'),
                                       (CommentModeration.CommentModerationState.UNSURE, 'Unsure')),
                              required=False)
    from_date = forms.DateField(label='From', required=False, widget=forms.DateInput(attrs={'type': 'date'}))
    to_date = forms.DateField(label='To', required=False, widget=forms.DateInput(attrs={'type': 'date'}))

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['state'].initial = 'UNMODERATED'
