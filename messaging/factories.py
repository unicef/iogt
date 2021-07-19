import factory
from factory.django import DjangoModelFactory


class ChatbotFactory(DjangoModelFactory):
    class Meta:
        model = 'messaging.ChatbotChannel'


class ThreadFactory(DjangoModelFactory):
    chatbot = factory.SubFactory(ChatbotFactory)
    subject = factory.Sequence(lambda n: f'Subject:0{n}')


    class Meta:
        model = 'messaging.Thread'
