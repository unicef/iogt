from datetime import datetime, timezone
from io import BytesIO

from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from django.core import management
from django.core.files.images import ImageFile
from django.core.management.base import BaseCommand
from wagtail.models import Site, Page
from wagtail.rich_text import RichText
from wagtail.images.models import Image

import home.models as models
from comments.models import CommentStatus

User = get_user_model()


class Command(BaseCommand):

    def clear(self):
        models.MiscellaneousIndexPage.objects.all().delete()
        models.BannerIndexPage.objects.all().delete()
        models.Article.objects.all().delete()
        models.Section.objects.all().delete()
        models.SectionIndexPage.objects.all().delete()
        Image.objects.all().delete()
        Page.objects.filter(id=2).delete()

    def create_image(self):
        """
        Generate a simple placeholder image locally using only stdlib/Pillow.
        This avoids any external network request (the original code fetched
        from via.placeholder.com which has SSL issues in some environments).
        """
        try:
            # Try to use Pillow if available (it is in the project requirements)
            from PIL import Image as PilImage, ImageDraw, ImageFont
            img = PilImage.new('RGB', (729, 576), color=(28, 171, 226))
            draw = ImageDraw.Draw(img)
            # Draw a simple label in the centre
            text = 'Youth'
            try:
                # Pillow 10+
                bbox = draw.textbbox((0, 0), text)
                w, h = bbox[2] - bbox[0], bbox[3] - bbox[1]
            except AttributeError:
                w, h = draw.textsize(text)
            draw.text(((729 - w) / 2, (576 - h) / 2), text, fill=(255, 255, 255))
            buf = BytesIO()
            img.save(buf, format='JPEG')
            buf.seek(0)
        except Exception:
            # Fallback: create a minimal 1x1 white JPEG without any library
            # JFIF/JPEG binary for a 1x1 white pixel
            buf = BytesIO(
                b'\xff\xd8\xff\xe0\x00\x10JFIF\x00\x01\x01\x00\x00\x01\x00\x01\x00\x00'
                b'\xff\xdb\x00C\x00\x08\x06\x06\x07\x06\x05\x08\x07\x07\x07\t\t'
                b'\x08\n\x0c\x14\r\x0c\x0b\x0b\x0c\x19\x12\x13\x0f\x14\x1d\x1a'
                b'\x1f\x1e\x1d\x1a\x1c\x1c $.\' ",#\x1c\x1c(7),01444\x1f\'9=82<.342\x1e\x1b'
                b'453739\x1b\x22LXeC\x1dB=0\x1a...\x1e\x1d\x1f\x1c\x1c'
                b'\xff\xc0\x00\x0b\x08\x00\x01\x00\x01\x01\x01\x11\x00'
                b'\xff\xc4\x00\x1f\x00\x00\x01\x05\x01\x01\x01\x01\x01\x01\x00\x00'
                b'\x00\x00\x00\x00\x00\x00\x01\x02\x03\x04\x05\x06\x07\x08\t\n\x0b'
                b'\xff\xc4\x00\xb5\x10\x00\x02\x01\x03\x03\x02\x04\x03\x05\x05\x04'
                b'\x04\x00\x00\x01}\x01\x02\x03\x00\x04\x11\x05\x12!1A\x06\x13Qa'
                b'\x07"q\x142\x81\x91\xa1\x08#B\xb1\xc1\x15R\xd1\xf0$3br\x82\t\n'
                b'\x16\x17\x18\x19\x1a%&\'()*456789:CDEFGHIJSTUVWXYZ'
                b'cdefghijstuvwxyz\x83\x84\x85\x86\x87\x88\x89\x8a\x92\x93\x94\x95'
                b'\x96\x97\x98\x99\x9a\xa2\xa3\xa4\xa5\xa6\xa7\xa8\xa9\xaa\xb2\xb3'
                b'\xb4\xb5\xb6\xb7\xb8\xb9\xba\xc2\xc3\xc4\xc5\xc6\xc7\xc8\xc9\xca'
                b'\xd2\xd3\xd4\xd5\xd6\xd7\xd8\xd9\xda\xe1\xe2\xe3\xe4\xe5\xe6\xe7'
                b'\xe8\xe9\xea\xf1\xf2\xf3\xf4\xf5\xf6\xf7\xf8\xf9\xfa'
                b'\xff\xda\x00\x08\x01\x01\x00\x00?\x00\xfb\xd4P\x00\x00\x00\x1f\xff\xd9'
            )

        title = 'youth_banner.jpg'
        image_file = ImageFile(buf, name=title)
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
                   RichText('Someone sent me a friend request - but I don\u2019t know this person, what should I do?'))],
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
            first_published_at=datetime.now(timezone.utc),
            commenting_status=CommentStatus.OPEN,
        )
        footer_index_page.add_child(instance=footer)

        miscellaneous_index_page = models.MiscellaneousIndexPage(title='Miscellaneous')
        home.add_child(instance=miscellaneous_index_page)

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

        # Create RapidPro Bot User
        management.call_command('sync_rapidpro_bot_user')
