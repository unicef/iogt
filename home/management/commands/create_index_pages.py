from django.contrib.contenttypes.models import ContentType
from django.core.management.base import BaseCommand

from home.models import HomePage, BannerIndexPage, FooterIndexPage, SectionIndexPage


class Command(BaseCommand):

    def handle(self, *args, **options):
        homepage_content_type, __ = ContentType.objects.get_or_create(
            model='homepage', app_label='home')
        homepage, __ = HomePage.objects.update_or_create(slug='home', defaults={
            'title': "Home",
            'draft_title': "Home",
            'content_type': homepage_content_type,
            'path': '00010001',
            'depth': 2,
            'numchild': 0,
            'url_path': '/home/',
            'show_in_menus': True,
        })
        banner_index_page = BannerIndexPage(title='Banners')
        footer_index_page = FooterIndexPage(title='Footers')
        section_index_page = SectionIndexPage(title='Sections')
        homepage.add_child(instance=banner_index_page)
        homepage.add_child(instance=footer_index_page)
        homepage.add_child(instance=section_index_page)
        self.stdout.write(self.style.SUCCESS('Index pages added.'))
