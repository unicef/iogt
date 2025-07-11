from celery import shared_task
from django.contrib.auth import get_user_model
from notifications.signals import notify
from user_notifications.models import UserNotificationTemplate, NotificationPreference
from .models import NotificationLog
User = get_user_model()


@shared_task
def send_signup_notifications(id, notification_type):
    from home.models import Article
    from questionnaires.models import Survey
    try:
        try:
            if notification_type == 'signup':
                sender = User.objects.get(id=id)
                print('sender', sender)
            elif notification_type == 'article':
                print('notification_type-article-id', id)
                sender = Article.objects.get(id=id)
                print('sender', sender)
            elif notification_type == 'survey':
                print('notification_type-survey-id', id)
                sender = Survey.objects.get(id=id)
                print('sender', sender)
        except User.DoesNotExist:
            print(f"User with ID {id} not found")
            return
        template = UserNotificationTemplate.objects.filter(active=True, type=notification_type).latest("updated_at")
        print('template', template)
        print('preferences', NotificationPreference.objects.filter(receive_notifications=True))
        for notification_preference in NotificationPreference.objects.filter(receive_notifications=True):
            try:
                print('notification_preference record:-', notification_preference)
                print('tags-name from notification_preference record:-', list(notification_preference.content_tags.values_list("name", flat=True)))
                print('notification_type value', notification_type.capitalize())
                if (notification_type.capitalize()) not in list(notification_preference.content_tags.values_list("name", flat=True)):
                    print('if block', notification_preference.user)
                    NotificationLog.objects.create(
                        user=notification_preference.user,
                        notification_key=template.title,
                        state="type"
                    )
                else:
                    print('sending notification to user:-', notification_preference.user)
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
                        state="sent"
                    )

            except Exception as e:
                NotificationLog.objects.create(
                    user=notification_preference.user,
                    notification_key=template.title,
                    state="failed",
                    error_message=str(e)
                )
    except Exception as e:
        # Optional: log failure for user if user or template not found
        NotificationLog.objects.create(
            user_id=sender,
            notification_key=template.title,
            state="failed",
            error_message=f"Task failure: {str(e)}"
        )