import json
from user_notifications.models import NotificationMeta
from wagtail.contrib.modeladmin.views import CreateView
from webpush import send_user_notification
from notifications.signals import notify
from notifications.models import Notification


class CreateNotificationView(CreateView):
    def form_valid(self, form):
        payload = form.cleaned_data.copy()
        groups = payload.pop('groups')
        for group in groups:
            for user in group.user_set.all():
                # 1. Create Notification
                notify.send(
                    sender=self.request.user,
                    recipient=user,
                    verb=payload.get('head', 'New Notification'),
                    description=payload.get('body', ''),
                    url=payload.get("url", "/")
                )

                # 2. Get latest Notification for user (created just now)
                notif_instance = Notification.objects.filter(recipient=user).order_by('-timestamp').first()
                if not notif_instance:
                    continue  # Shouldn't happen, but guard just in case

                # 3. Avoid duplicate meta creation
                NotificationMeta.objects.get_or_create(notification=notif_instance)

                # 4. Send Web Push
                send_user_notification(
                    user=user, 
                    payload={
                        "title": payload.get("head", "IoGT Notification"),
                        "body": payload.get("body", ""),
                        "url": payload.get("url", "/"),
                        "notification_id": notif_instance.id
                    },
                    ttl=1000)
        return super().form_valid(form)
