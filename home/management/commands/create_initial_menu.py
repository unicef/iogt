from pathlib import Path

from django.conf import settings
from django.contrib.contenttypes.models import ContentType
from django.core.files import File
from django.core.management.base import BaseCommand
from wagtail.core.models import Site, Locale
from wagtailmenus.models import FlatMenu
from wagtailsvg.models import Svg

from home.models import IogtFlatMenuItem, HomePage, LocaleDetail


class Command(BaseCommand):
    def handle(self, *args, **options):
        site = Site.objects.filter(is_default_site=True).first()
        if not site:
            self.stdout.write(self.style.ERROR('Default site not found.'))
            return

        locale_detail = LocaleDetail.objects.filter(is_main_language=True).first()
        if not locale_detail:
            self.stdout.write(self.style.ERROR('Main language not found.'))
            return

        home_page = HomePage.objects.filter(locale=locale_detail.locale).first()
        if not home_page:
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
