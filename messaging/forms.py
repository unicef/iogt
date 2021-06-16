from django import forms
from django.contrib.auth import get_user_model

from .hooks import hookset
from .models import Message, ChatbotChannel


class UserModelChoiceField(forms.ModelChoiceField):

    def label_from_instance(self, obj):
        return hookset.display_name(obj)


class UserModelMultipleChoiceField(forms.ModelMultipleChoiceField):

    def label_from_instance(self, obj):
        return hookset.display_name(obj)


class ChatbotChannelModelChoiceField(forms.ModelChoiceField):

    def label_from_instance(self, obj):
        return obj.display_name


class ChatbotChannelModelMultipleChoiceField(forms.ModelMultipleChoiceField):

    def label_from_instance(self, obj):
        return obj.display_name


class NewMessageForm(forms.ModelForm):

    subject = forms.CharField()
    chatbot = ChatbotChannelModelChoiceField(queryset=ChatbotChannel.objects.none())
    content = forms.CharField(widget=forms.Textarea)

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop("user")
        super().__init__(*args, **kwargs)
        self.fields["chatbot"].queryset = ChatbotChannel.objects.all()

    def save(self, commit=True):
        data = self.cleaned_data
        return Message.new_message(
            self.user, [], data["chatbot"], data["subject"], data["content"]
        )

    class Meta:
        model = Message
        fields = ["chatbot", "subject", "content"]


class NewMessageFormMultiple(forms.ModelForm):
    subject = forms.CharField()
    to_user = UserModelMultipleChoiceField(get_user_model().objects.none())
    chatbot = ChatbotChannelModelChoiceField(ChatbotChannel.objects.none())
    content = forms.CharField(widget=forms.Textarea)

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop("user")
        super().__init__(*args, **kwargs)
        self.fields["to_user"].queryset = hookset.get_user_choices(self.user)
        self.fields["chatbot"].queryset = ChatbotChannel.objects.all()
        if self.initial.get("to_user") is not None:
            qs = self.fields["to_user"].queryset.filter(pk__in=self.initial["to_user"])
            self.fields["to_user"].queryset = qs

    def save(self, commit=True):
        data = self.cleaned_data
        return Message.new_message(
            self.user, data["to_user"], data["chatbot"], data["subject"], data["content"]
        )

    class Meta:
        model = Message
        fields = ["to_user", "chatbot", "subject", "content"]


class MessageReplyForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        self.thread = kwargs.pop("thread")
        self.user = kwargs.pop("user")
        super().__init__(*args, **kwargs)

    def save(self, commit=True):
        return Message.new_reply_to_rapidpro(
            self.thread, self.user, self.cleaned_data["content"]
        )

    class Meta:
        model = Message
        fields = ["content"]
