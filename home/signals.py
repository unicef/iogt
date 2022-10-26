from django.dispatch import receiver
from wagtail.core.models import Site
from django.db.models.signals import pre_save, pre_delete


@receiver(pre_save, sender=Site)
def save_site(instance, **kwargs):
    if Site.objects.exclude(pk=instance.pk).count() == 0:
        instance.is_default_site = True

@receiver(pre_delete, sender=Site)
def delete_site(instance, **kwargs):
    if Site.objects.exclude(pk=instance.pk).count() == 1:
        Site.objects.exclude(pk=instance.pk).update(is_default_site=True)
