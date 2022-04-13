from django.contrib.auth import get_user_model
from django.core.management import BaseCommand
from django_comments_xtd.models import XtdComment

from messaging.models import Thread


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument(
            '--exclude-user-ids',
            nargs="+",
            required=False,
            type=int,
            help="IDs for users that wouldn't be cleared"
        )

    def handle(self, *args, **options):
        user_ids = options.get('exclude_user_ids') or []
        get_user_model().objects.exclude(pk__in=user_ids).delete()
        XtdComment.objects.all().delete()
        Thread.objects.all().delete()
        self.stdout.write('User data cleared.')
