from wagtail.contrib.modeladmin.views import CreateView
from webpush import send_user_notification


class CreateNotificationView(CreateView):
    def form_valid(self, form):
        payload = form.cleaned_data.copy()
        groups = payload.pop('groups')
        for group in groups:
            for user in group.user_set.all():
                send_user_notification(user=user, payload=payload, ttl=1000)
        return super().form_valid(form)
