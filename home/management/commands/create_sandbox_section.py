from django.core.management.base import BaseCommand

from home.models import HomePage, Section


class Command(BaseCommand):

    def handle(self, *args, **options):
        home_page = HomePage.objects.get(slug='home')
        sandbox_section = home_page.get_children().filter(slug='sandbox').first()
        if sandbox_section:
            self.stdout.write(self.style.SUCCESS('Sandbox Section already exists.'))
        else:
            section = Section(title='Sandbox', live=False)
            home_page.add_child(instance=section)
            self.stdout.write(self.style.SUCCESS('Sandbox Section added.'))

