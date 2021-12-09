from django.core.exceptions import ValidationError
from django.core.management.base import BaseCommand
from wagtail.core.models import Page
from wagtail_localize.models import TranslationSource


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument(
            '--publish',
            action='store_true',
            help='This will publish immediately, before any new translations happen.'
        )

    def handle(self, *args, **options):
        publish = options.get('publish')

        for page in Page.objects.all().specific():
            source = TranslationSource.objects.get_for_instance_or_none(page)
            if source:
                source.update_from_db()
                if publish:
                    for translation in source.translations.filter(enabled=True).select_related("target_locale"):
                        try:
                            translation.save_target(publish=True)
                        except ValidationError:
                            pass

        self.stdout.write(self.style.SUCCESS('Translated pages synced.'))
