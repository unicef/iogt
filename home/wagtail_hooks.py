from abc import ABC
from django.urls import reverse
from django.utils.html import escape
from wagtail.core import hooks
from wagtail.core.rich_text import LinkHandler
from wagtail.core.models import PageViewRestriction
from django.core.exceptions import PermissionDenied


class ExternalLinkHandler(LinkHandler, ABC):
    identifier = "external"

    @classmethod
    def expand_db_attributes(cls, attrs):
        next_page = escape(attrs["href"])
        external_link_page = reverse("external-link")
        return f'<a href="{external_link_page}?next={next_page}">'


@hooks.register("register_rich_text_features")
def register_external_link(features):
    features.register_link_type(ExternalLinkHandler)

@hooks.register('before_serve_page', order=-1)
def check_group(page, request, serve_args, serve_kwargs):
    if request.user.is_authenticated:
        for restriction in page.get_view_restrictions():
            if not restriction.accept_request(request):
                if restriction.restriction_type == PageViewRestriction.GROUPS:
                    current_user_groups = request.user.groups.all()
                    if not any(group in current_user_groups for group in restriction.groups.all()):
                        raise PermissionDenied
