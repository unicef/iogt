from pathlib import Path

from django.conf import settings
from django.core.files import File
from django.core.management.base import BaseCommand
from wagtail.core.models import Site, Locale
from wagtailmenus.models import FlatMenu
from wagtailsvg.models import Svg

from home.models import IogtFlatMenuItem, HomePage


class Command(BaseCommand):
    def handle(self, *args, **options):
        site = Site.objects.filter(is_default_site=True).first()
        if not site:
            self.stdout.write(self.style.ERROR('Default site not found.'))
            return

        home_page = HomePage.objects.first()
        if not home_page:
            self.stdout.write(self.style.ERROR('Homepage not found.'))
            return

        locales = Locale.objects.all()
        file = File(open(Path(settings.BASE_DIR) / 'iogt/static/icons/burger.svg'), name='burger.svg')
        icon = Svg.objects.create(title='burger', file=file)
        for locale in locales:
            menu, __ = FlatMenu.objects.get_or_create(handle=f'{locale.language_code}_menu_live', defaults={
                'title': f'{locale.language_code} main menu',
                'site': site,
                'heading': 'Main Menu',
            })

            translated_home_page = home_page.get_translation_or_none(locale)
            if translated_home_page:
                IogtFlatMenuItem.objects.get_or_create(
                    link_page=translated_home_page,
                    menu=menu,
                    defaults={
                        'link_text': translated_home_page.title.split(' ')[0],
                    }
                )

            IogtFlatMenuItem.objects.get_or_create(
                link_url='#',
                menu=menu,
                url_append='top-level-sections',
                defaults={
                    'link_text': 'Sections',
                }
            )
            IogtFlatMenuItem.objects.get_or_create(
                link_url='#menu',
                menu=menu,
                defaults={
                    'link_text': 'Menu',
                    'icon': icon,
                    'display_only_in_single_column_view': True,
                }
            )

        self.stdout.write(self.style.SUCCESS('Menu items created.'))
