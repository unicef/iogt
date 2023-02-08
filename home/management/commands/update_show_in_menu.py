from django.core.management.base import BaseCommand

from wagtail.core.models import Page

from home.models import HomePage, Section, Article, PageLinkPage
from questionnaires.models import Poll, Quiz, Survey


class Command(BaseCommand):

    def handle(self, *args, **options):
        Page.objects.type(HomePage, Section, Article, PageLinkPage, Poll, Quiz, Survey).update(show_in_menus=True)
