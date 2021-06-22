from django.contrib.auth import get_user_model


class DefaultHookSet:

    def display_name(self, user):
        return str(user)

    def get_user_choices(self, user):
        return get_user_model().objects.exclude(id=user.id)


hookset = DefaultHookSet()
