from django.dispatch import receiver
from wagtail.signals import page_published
from .models import Survey
from user_notifications.tasks import send_app_notifications


@receiver(page_published)
def trigger_survey_notification(sender, instance, **kwargs):
    if isinstance(instance, Survey):
        print("📢 Article published:", instance.title)
        send_app_notifications.delay(instance.id, 'survey')
