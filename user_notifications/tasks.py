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
def send_app_notifications(id, url=None, notification_type=None):
    from home.models import Article
    from questionnaires.models import Survey
    try:
        try:
            template = UserNotificationTemplate.objects.filter(active=True, type=notification_type).latest("updated_at")
            if notification_type == 'signup' or notification_type == 'web_push':
                 sender = User.objects.get(id=id)
                 notify.send(
                    sender=sender,
                    recipient=sender,
                    verb=template.title,
                    description=template.message
                )
                 NotificationLog.objects.create(
                     user=sender,
                     notification_key=template.title,
                     tags=notification_type,
                     state="sent"
                 )
        except User.DoesNotExist:
            return
        if notification_type=='article':
            sender = Article.objects.get(id=id)
        elif notification_type == 'survey':
            sender = Survey.objects.get(id=id)

        if notification_type != 'signup':
            article_or_survey_tags_id = list(sender.notification_tags.values_list('id', flat=True))
            for notification_preference in NotificationPreference.objects.filter(receive_notifications=True,                                                                                 content_tags__in=article_or_survey_tags_id).select_related('user').distinct():
                try:
                    notify.send(
                        sender=sender,
                        url=url,
                        recipient=notification_preference.user,
                        verb=template.title,
                        description=template.message
                    )
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
                                "url": url,
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