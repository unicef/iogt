from django.dispatch import receiver
from wagtail.core.models import Site
from django.db.models.signals import pre_save


@receiver(pre_save, sender=Site)
def save_site(instance, **kwargs):
    if Site.objects.exclude(pk=instance.pk).filter(is_default_site=True).first() is None:
        instance.is_default_site = True
