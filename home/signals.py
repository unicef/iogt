from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from .models import ArticleFeedback

@receiver(post_save, sender=ArticleFeedback)
@receiver(post_delete, sender=ArticleFeedback)
def update_article_feedback_metrics(sender, instance, **kwargs):
    """
    Update the article's feedback metrics whenever a feedback entry is added, updated, or deleted.
    """
    if instance.article:
        instance.article.update_feedback_metrics()
