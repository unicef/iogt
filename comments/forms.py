from django import forms
from django_comments_xtd.forms import XtdCommentForm as BaseCommentForm


class CommentForm(BaseCommentForm):

    def __init__(self, *args, **kwargs):
        super(CommentForm, self).__init__(*args, **kwargs)
        self.fields['email'].initial = 'noreply@example.com'
        self.fields['email'].widget = forms.HiddenInput()

        self.fields['followup'].initial = False
        self.fields['followup'].widget = forms.HiddenInput()
