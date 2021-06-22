from django.db.models import QuerySet


class ThreadQuerySet(QuerySet):
    def of_user(self, user):
        return self.filter(user_threads__user=user)

    def inbox(self):
        return self.filter(user_threads__is_active=False)

    def deleted(self):
        return self.filter(user_threads__is_active=True)

    def unread(self):
        return self.filter(
            user_threads__is_active=False,
            user_threads__is_read=True
        )

    def order_by_latest(self):
        return self.filter(last_message_at__isnull=False).order_by('-last_message_at')
