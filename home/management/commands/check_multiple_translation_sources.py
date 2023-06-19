from django.core.management import BaseCommand
from wagtail.core.models import Page
from wagtail_localize.models import TranslationSource


class Command(BaseCommand):
    def handle(self, *args, **options):
        for page in Page.objects.all():
            translation_sources = TranslationSource.objects.filter(
                object_id=page.translation_key,
                specific_content_type=page.content_type_id,
                translations__target_locale=page.locale,
            )

            if translation_sources.count() > 1:
                self.stdout.write(f"Multiple translation sources found for page: {page.id}, title: {page.title}")
                for translation_source in translation_sources:
                    self.stdout.write(f" - Translation source: {translation_source.id}, locale: {translation_source.locale}")
