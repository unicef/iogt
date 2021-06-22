from django.db.models import QuerySet


class ThreadQuerySet(QuerySet):
    def of_user(self, user):
        return self.filter(user_threads__user=user)

    def inbox(self):
        return self.filter(user_threads__is_active=True)

    def deleted(self):
        return self.filter(user_threads__is_active=False)

    def unread(self):
        return self.filter(
            user_threads__is_active=True,
            user_threads__is_read=False
        )

    def order_by_latest(self):
        return self.filter(last_message_at__isnull=False).order_by('-last_message_at')
