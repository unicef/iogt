from datetime import datetime, timezone
from io import BytesIO

import requests
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from django.core import management
from django.core.files.images import ImageFile
from django.core.management.base import BaseCommand
from wagtail.core.models import Site, Page
from wagtail.core.rich_text import RichText
from wagtail.images.models import Image

import home.models as models
from comments.models import CommentStatus

User = get_user_model()


class Command(BaseCommand):

    def clear(self):
        models.BannerPage.objects.all().delete()
        models.BannerIndexPage.objects.all().delete()
        models.Article.objects.all().delete()
        models.Section.objects.all().delete()
        models.SectionIndexPage.objects.all().delete()
        Image.objects.all().delete()
        Page.objects.filter(id=2).delete()

    def create_image(self):
        response = requests.get('https://via.placeholder.com/729x576.png?text=Youth')

        title = 'youth_banner.jpg'
        image_file = ImageFile(BytesIO(response.content), name=title)

        return Image.objects.create(title=title, file=image_file)

    def create_homepage(self):
        homepage_content_type, __ = ContentType.objects.get_or_create(
            model='homepage', app_label='home')

        # Create a new homepage
        homepage, __ = models.HomePage.objects.update_or_create(slug='home', defaults={
            'title': "Home",
            'draft_title': "Home",
            'content_type': homepage_content_type,
            'path': '00010001',
            'depth': 2,
            'numchild': 0,
            'url_path': '/home/',
            'show_in_menus': True,
        })

        # Create a site with the new homepage set as the root
        Site.objects.get_or_create(hostname='localhost', defaults={
            'root_page': homepage,
            'is_default_site': True,
        })

    def create(self, owner, home):
        article = models.Article(
            title='Do you know the person adding you?',
            body=[('paragraph',
                   RichText('Someone sent me a friend request - but I don’t know this person, what should I do?'))],
            owner=owner,
            first_published_at=datetime.now(timezone.utc),
            commenting_status=CommentStatus.OPEN
        )
        internet_safety = models.Section(
            title='Internet Safety',
            show_in_menus=True,
        )
        youth = models.Section(
            title='Youth',
            show_in_menus=True,
            font_color='1CABE2'
        )
        section_index_page = models.SectionIndexPage(title='Sections')

        home.add_child(instance=section_index_page)
        section_index_page.add_child(instance=youth)
        youth.add_child(instance=internet_safety)
        internet_safety.add_child(instance=article)

        models.FeaturedContent.objects.create(source=home, content=youth)

        banner_index_page = models.BannerIndexPage(title='Banners')
        home.add_child(instance=banner_index_page)

        image = self.create_image()

        banner_page = models.BannerPage(title='Youth', banner_image=image, banner_link_page=youth)
        banner_index_page.add_child(instance=banner_page)

        models.HomePageBanner.objects.create(source=home, banner_page=banner_page)

        footer_index_page = models.FooterIndexPage(title='Footers')
        home.add_child(instance=footer_index_page)

        footer = models.FooterPage(
            title='Footer1?',
            body=[('paragraph',
                   RichText('Footer1 paragraph1'))],
            owner=owner,
            first_published_at=datetime.now(timezone.utc)
        )
        footer_index_page.add_child(instance=footer)

        # Create RapidPro Bot User
        management.call_command('sync_rapidpro_bot_user')

    def populate_group_permissions(self):
        self.stdout.write('Adding group permissions')

        permissions = Permission.objects.filter(codename__in=['can_moderate', 'delete_xtdcomment'])

        group = Group.objects.get(name='Moderators')
        for permission in permissions:
            group.permissions.add(permission)

    def handle(self, *args, **options):
        self.clear()
        self.stdout.write('Existing site structure cleared')

        self.create_homepage()

        owner = User.objects.first()
        home = models.HomePage.objects.first()
        if home:
            self.stdout.write(f"Home page found, title={home.title}")
            self.create(owner, home)
        else:
            self.stdout.write('No home page found. Quitting.')

        self.populate_group_permissions()

        management.call_command('create_default_site')
