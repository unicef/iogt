from abc import ABC
from urllib.parse import urlparse

from django.urls import reverse
from django.utils.html import escape
from iogt.settings.base import INTERNAL_DOMAIN
from wagtail.core import hooks
from wagtail.core.rich_text import LinkHandler


class ExternalLinkHandler(LinkHandler, ABC):
    identifier = "external"

    @classmethod
    def expand_db_attributes(cls, attrs):
        external_link_page = reverse("external_link")
        next_page = escape(attrs["href"])
        next_page_hostname = urlparse(next_page).hostname

        print(INTERNAL_DOMAIN)
        if next_page_hostname not in INTERNAL_DOMAIN:
            return f'<a href="{external_link_page}?next={next_page}">'
        return f'<a href="{next_page}">'


@hooks.register("register_rich_text_features")
def register_external_link(features):
    features.register_link_type(ExternalLinkHandler)
