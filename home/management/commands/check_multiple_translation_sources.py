from django.core.management import BaseCommand
from wagtail.core.models import Page
from wagtail_localize.models import TranslationSource


class Command(BaseCommand):
    def handle(self, *args, **options):
        for page in Page.objects.filter(translation_key__isnull=False):
            try:
                TranslationSource.objects.get(
                    object_id=page.translation_key,
                    specific_content_type=page.content_type_id,
                    translations__target_locale=page.locale,
                )
            except TranslationSource.DoesNotExist:
                pass
            except TranslationSource.MultipleObjectsReturned:
                self.stdout.write(f"=======> {page.id} {page.title}")
