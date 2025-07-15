from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from .models import ArticleFeedback
from wagtail.signals import page_published
from .models import Article
from user_notifications.tasks import send_signup_notifications


@receiver(post_save, sender=ArticleFeedback)
@receiver(post_delete, sender=ArticleFeedback)
def update_article_feedback_metrics(sender, instance, **kwargs):
    """
    Update the article's feedback metrics whenever a feedback entry is added, updated, or deleted.
    """
    if instance.article:
        instance.article.update_feedback_metrics()


@receiver(page_published)
def trigger_article_notification(sender, instance, **kwargs):
    if isinstance(instance, Article):
        send_signup_notifications.delay(instance.id, 'article')
