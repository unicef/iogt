from django.core.cache import cache
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from translation_manager.models import TranslationEntry
from wagtailcache.cache import clear_cache
from .models import ArticleFeedback


@receiver(post_save, sender=ArticleFeedback)
@receiver(post_delete, sender=ArticleFeedback)
def update_article_feedback_metrics(sender, instance, **kwargs):
    """
    Update the article's feedback metrics whenever a feedback entry is added, updated, or deleted.
    """
    if instance.article:
        instance.article.update_feedback_metrics()


@receiver(post_save, sender=TranslationEntry)
@receiver(post_delete, sender=TranslationEntry)
def invalidate_translation_cache(sender, instance, **kwargs):
    """
    Invalidate the language translation map cache and wagtail cache
    whenever a TranslationEntry is added, updated, or deleted.
    """
    if instance.language:
        cache.delete(f'{instance.language}_translation_map')
    clear_cache()
