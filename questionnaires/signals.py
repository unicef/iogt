from django.dispatch import receiver
from wagtail.signals import page_published
from .models import Survey
from user_notifications.tasks import send_signup_notifications


@receiver(page_published)
def trigger_survey_notification(sender, instance, **kwargs):
    if isinstance(instance, Survey):
        send_signup_notifications.delay(instance.id, 'survey')