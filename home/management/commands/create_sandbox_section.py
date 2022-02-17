from django.core.management.base import BaseCommand

from home.models import HomePage, Section


class Command(BaseCommand):

    def handle(self, *args, **options):
        home_page = HomePage.objects.get(slug='home')
        if not Section.objects.filter(slug='sandbox').exists():
            section = Section(title='Sandbox', live=False)
            home_page.add_child(instance=section)
            self.stdout.write(self.style.SUCCESS('Sandbox Section added.'))
        else:
            self.stdout.write(self.style.SUCCESS('Sandbox Section already exists.'))

