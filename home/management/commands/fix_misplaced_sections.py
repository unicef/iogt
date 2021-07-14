from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.sites.models import Site
from django.core.management.base import BaseCommand

from home.models import HomePage, Section, SectionIndexPage

User = get_user_model()


class Command(BaseCommand):
    """
    This command picks all the Sections that are direct children of HomePage
    and moves them as children of the SectionIndexPage.
    """

    def handle(self, *args, **options):
        home_pages = HomePage.objects.all()

        for home_page in home_pages:
            misplaced_sections = home_page.get_children().type(Section)
            section_index_page = home_page.get_children().type(SectionIndexPage).first()

            for section in misplaced_sections:
                section.move(section_index_page, pos='last-child')
                self.stdout.write(self.style.SUCCESS(f'Successfully moved {section} to {section_index_page}'))
