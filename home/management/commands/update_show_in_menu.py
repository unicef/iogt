from django.core.management.base import BaseCommand

from wagtail.core.models import Page

class Command(BaseCommand):

    def handle(self, *args, **options):
        Page.objects.all().update(show_in_menus=True)
