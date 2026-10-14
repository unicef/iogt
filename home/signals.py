from django.core.cache import cache
from django.db import transaction
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from translation_manager.models import TranslationEntry
from wagtailcache.cache import clear_cache
from .models import ArticleFeedback


@receiver(post_save, sender=ArticleFeedback)
@receiver(post_delete, sender=ArticleFeedback)
def update_article_feedback_metrics(sender, instance, **kwargs):
    """
    Update the article's feedback metrics whenever a feedback entry
    is added, updated, or deleted.
    """
    if instance.article:
        instance.article.update_feedback_metrics()


def invalidate_translation_cache(language):
    if not language:
        return

    cache_key = f'{language}_translation_map'
    deleted = cache.delete(cache_key)

    print(
        f"[TRANSLATION CACHE] "
        f"language={language}, "
        f"key={cache_key}, "
        f"deleted={deleted}"
    )

    clear_cache()


@receiver(post_save, sender=TranslationEntry)
@receiver(post_delete, sender=TranslationEntry)
def schedule_translation_cache_invalidation(sender, instance, **kwargs):
    """
    Schedule cache invalidation after the database transaction commits.
    """
    language = instance.language

    transaction.on_commit(
        lambda: invalidate_translation_cache(language)
    )