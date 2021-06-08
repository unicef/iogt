from abc import ABC

from django.urls import reverse
from django.utils.html import escape
from wagtail.core import hooks
from wagtail.core.rich_text import LinkHandler


class ExternalLinkHandler(LinkHandler, ABC):
    identifier = "external"

    @classmethod
    def expand_db_attributes(cls, attrs):
        external_link_page = reverse("external-link")
        next_page = escape(attrs["href"])
        return f'<a href="{external_link_page}?next={next_page}">'


@hooks.register("register_rich_text_features")
def register_external_link(features):
    features.register_link_type(ExternalLinkHandler)
