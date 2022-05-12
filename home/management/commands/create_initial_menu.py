from pathlib import Path

from django.conf import settings
from django.contrib.contenttypes.models import ContentType
from django.core.files import File
from django.core.management.base import BaseCommand
from wagtail.core.models import Site, Locale
from wagtailmenus.models import FlatMenu
from wagtailsvg.models import Svg

from home.models import IogtFlatMenuItem, HomePage


class Command(BaseCommand):
    def handle(self, *args, **options):
        site = Site.objects.get(is_default_site=True)
        if not site:
            self.stdout.write(self.style.SUCCESS('Default site not found.'))

        home_page_content_type, __ = ContentType.objects.get_or_create(
            model='homepage', app_label='home')
        home_page, __ = HomePage.objects.get_or_create(slug='home', defaults={
            'title': "Home",
            'draft_title': "Home",
            'content_type': home_page_content_type,
            'path': '00010001',
            'depth': 2,
            'numchild': 0,
            'url_path': '/home/',
            'show_in_menus': True,
        })

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
                IogtFlatMenuItem.objects.create(link_page=translated_home_page, menu=menu, url_append='#home')

            IogtFlatMenuItem.objects.create(
                link_url='#', menu=menu, link_text='Sections', url_append='top-level-sections')
            IogtFlatMenuItem.objects.get_or_create(link_url='#menu', menu=menu, defaults={
                'link_text': 'Menu',
                'icon': icon,
                'display_only_in_single_column_view': True,
            })
