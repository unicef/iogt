from urllib.parse import urlparse
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from .models import ArticleFeedback
from wagtail.signals import page_published
from wagtail.models import Site
import os
from .models import Article
from user_notifications.tasks import send_app_notifications


@receiver(post_save, sender=ArticleFeedback)
@receiver(post_delete, sender=ArticleFeedback)
def update_article_feedback_metrics(sender, instance, **kwargs):
    """
    Update the article's feedback metrics whenever a feedback entry is added, updated, or deleted.
    """
    if instance.article:
        instance.article.update_feedback_metrics()


def get_site_for_locale(instance):
    """
    Return the Wagtail Site object matching the given locale.
    """
    for site in Site.objects.all():
        if site.root_page.locale.language_code == instance.locale.language_code:
            if not site:
                print("No matching site for locale:", instance.locale)
                return

            parsed = urlparse(site.root_url)
            hostname = parsed.hostname
            scheme = parsed.scheme or "http"
            port = os.getenv("DJANGO_RUN_PORT")
            if hostname in ("localhost", "127.0.0.1"):
                host_with_port = f"{scheme}://{hostname}:{port}"
            else:
                host_with_port = f"{scheme}://{hostname}"
            relative = instance.relative_url(site)
            if not relative:
                print("Could not get relative URL for instance.")
                return
            full_url = host_with_port + relative
            return full_url
    return None


@receiver(page_published)
def trigger_article_notification(sender, instance, **kwargs):
    if not isinstance(instance, Article):
        return
    full_url = get_site_for_locale(instance)
    send_app_notifications.delay(instance.id, 'article', full_url)

