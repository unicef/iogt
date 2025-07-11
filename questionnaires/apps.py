from django.apps import AppConfig


class QuestionnairesConfig(AppConfig):
    name = 'questionnaires'

    def ready(self):
        import questionnaires.signals  #
