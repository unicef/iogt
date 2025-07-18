from django.dispatch import receiver
from wagtail.signals import page_published
from wagtail.models import Site
from urllib.parse import urlparse
from .models import Survey
from user_notifications.tasks import send_app_notifications
import os


def get_site_for_locale(locale):
    """
    Return the Wagtail Site object matching the given locale.
    """
    for site in Site.objects.all():
        if site.root_page.locale.language_code == locale.language_code:
            return site
    return None


@receiver(page_published)
def trigger_survey_notification(sender, instance, **kwargs):
    if not isinstance(instance, Survey):
        return
    site = get_site_for_locale(instance.locale)
    if not site:
        print("No matching site for locale:", instance.locale)
        return

    parsed = urlparse(site.root_url)
    hostname = parsed.hostname
    scheme = parsed.scheme or "http"
    port = os.getenv("DJANGO_RUN_PORT")
    host_with_port = f"{scheme}://{hostname}:{port}"
    relative = instance.relative_url(site)
    if not relative:
        print("Could not get relative URL for instance.")
        return
    full_url = host_with_port + relative
    send_app_notifications.delay(instance.id, 'survey', full_url)