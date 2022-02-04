from pathlib import Path

from django.conf import settings
from django.core.files import File
from django.core.management.base import BaseCommand
from wagtail.core.models import Site, Locale
from wagtailmenus.models import FlatMenu
from wagtailsvg.models import Svg

from home.models import IogtFlatMenuItem


class Command(BaseCommand):
    def handle(self, *args, **options):
        site = Site.objects.get(is_default_site=True)
        if not site:
            self.stdout.write(self.style.SUCCESS('Default site not found.'))

        locales = Locale.objects.all()
        file = File(open(Path(settings.BASE_DIR) / 'iogt/static/icons/burger.svg'), name='burger.svg')
        icon = Svg.objects.create(title='burger', file=file)
        for locale in locales:
            menu, __ = FlatMenu.objects.get_or_create(handle=f'{locale.language_code}_menu_live', defaults={
                'title': f'{locale.language_code} main menu',
                'site': site,
                'heading': 'Main Menu',
            })
            IogtFlatMenuItem.objects.get_or_create(link_url='#menu', menu=menu, defaults={
                'link_text': 'Menu',
                'icon': icon,
                'display_only_in_single_column_view': True,
            })
