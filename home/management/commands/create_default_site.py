from django.conf import settings
from django.contrib.sites.models import Site as DjangoSite
from django.core.management.base import BaseCommand
from home.models import HomePage
from wagtail.core.models import Site as WagtailSite


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument(
            "--domain",
            default="localhost",
            help="Site domain; default: 'localhost'",
        )
        parser.add_argument(
            "--port",
            default=8000,
            help="HTTP port; default: '8000'",
            type=int,
        )

    def handle(self, *args, **options):
        domain = options.get("domain")
        port = options.get("port")

        django_site, created = DjangoSite.objects.update_or_create(
            pk=settings.SITE_ID,
            defaults={
                "domain": domain if port in [80, 443] else f"{domain}:{port}",
                "name": "default",
            },
        )
        self.stdout.write(
            f"Django site, name={django_site.name}, domain={django_site.domain}, "
            f"created={created}"
        )
        wagtail_site, created = WagtailSite.objects.update_or_create(
            is_default_site=True,
            defaults={
                "hostname": domain,
                "port": port,
                "site_name": "default",
                "root_page": HomePage.objects.all().order_by("id").first(),
            },
        )
        self.stdout.write(
            f"Wagtail site, name={wagtail_site.site_name}, "
            f"host={wagtail_site.hostname}, port={wagtail_site.port}, "
            f"created={created}"
        )
