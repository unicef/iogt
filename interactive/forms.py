from django import forms


class MessageSendForm(forms.Form):
    text = forms.CharField(widget=forms.TextInput(attrs={'class': 'btn btn-outline-secondary'}))
