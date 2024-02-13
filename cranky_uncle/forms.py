from django import forms


class CrankySendMessageForm(forms.Form):
    text = forms.CharField(widget=forms.TextInput(attrs={'class': 'btn btn-outline-secondary'}))
