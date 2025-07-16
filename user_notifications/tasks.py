from celery import shared_task
from django.contrib.auth import get_user_model
from notifications.signals import notify
from user_notifications.models import UserNotificationTemplate, NotificationPreference
from .models import NotificationLog
from notifications.models import Notification
from user_notifications.models import NotificationMeta
from webpush import send_user_notification
from django.utils.html import strip_tags
User = get_user_model()


@shared_task
def send_app_notifications(id, notification_type):
    from home.models import Article
    from questionnaires.models import Survey
    try:
        try:
            template = UserNotificationTemplate.objects.filter(active=True, type=notification_type).latest("updated_at")
            if notification_type == 'signup' or notification_type == 'web_push':
                 sender = User.objects.get(id=id)
                 notify.send(
                    sender=sender,
                    url='www.google.com',
                    recipient=sender,
                    verb=template.title,
                    description=template.message
                )
                 NotificationLog.objects.create(
                     user=sender,
                     notification_key=template.title,
                     tags=notification_type,
                     state="success"
                 )
            elif notification_type == 'article':
                sender = Article.objects.get(id=id)
            elif notification_type == 'survey':
                sender = Survey.objects.get(id=id)
        except User.DoesNotExist:
            return

        if notification_type != 'signup':
            for notification_preference in NotificationPreference.objects.filter(receive_notifications=True):
                try:
                    if (notification_type.capitalize()) not in list(notification_preference.content_tags.values_list("name", flat=True)):
                        NotificationLog.objects.create(
                            user=notification_preference.user,
                            notification_key=template.title,
                            tags=notification_type,
                            state="type"
                        )
                    else:
                        notify.send(
                            sender=sender,
                            url='www.google.com',
                            recipient=notification_preference.user,
                            verb=template.title,
                            description=template.message
                        )
                        # send_user_notification(user=user, payload=json.dumps(template), ttl=1000)
                        # raise Exception
                        NotificationLog.objects.create(
                            user=notification_preference.user,
                            notification_key=template.title,
                            tags=notification_type,
                            state="sent"
                        )
                        notif_instance = Notification.objects.filter(recipient=notification_preference.user).order_by('-timestamp').first()
                        if not notif_instance:
                            continue  # Shouldn't happen, but guard just in case

                        # 3. Avoid duplicate meta creation
                        try:
                            NotificationMeta.objects.get_or_create(notification=notif_instance)
                        except Exception as e:
                            print(e)
                        # 4. Send Web Push
                        try:
                            send_user_notification(
                                user=notification_preference.user,
                                payload={
                                    "title": template.title,
                                    "body": strip_tags(template.message),
                                    "url": 'www.google.com',
                                    "notification_id": notif_instance.id
                                },
                                ttl=1000)
                        except Exception as e:
                            print(e)

                except Exception as e:
                    NotificationLog.objects.create(
                        user=notification_preference.user,
                        notification_key=template.title,
                        tags=notification_type,
                        state="failed",
                        error_message=str(e)
                    )
    except Exception as e:
        # Optional: log failure for user if user or template not found
        NotificationLog.objects.create(
            user_id=sender,
            notification_key=template.title,
            tags=notification_type,
            state="failed",
            error_message=f"Task failure: {str(e)}"
        )