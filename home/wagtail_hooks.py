from urllib.parse import urlparse

from django.urls import resolve
from wagtail.core.models import Page
from abc import ABC
from django.urls import reverse
from django.utils.html import escape
from wagtail.core import hooks
from wagtail.core.rich_text import LinkHandler
from wagtail.core.models import PageViewRestriction
from django.core.exceptions import PermissionDenied
from home.models import FooterIndexPage


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

@hooks.register('construct_explorer_page_queryset')
def sort_footer_page_listing_by_path(parent_page, pages, request):
    if isinstance(parent_page, FooterIndexPage):
        pages = pages.order_by('path')

    return pages


@hooks.register('construct_page_chooser_queryset')
def limit_page_chooser(pages, request):
    # TODO: add section check otherwise page chooser will break in other places like banner etc.
    current_url_match = resolve(urlparse(request.path)[2])
    if current_url_match.kwargs:
        page_id = current_url_match.kwargs.get('parent_page_id')
    else:
        referer_url_match = resolve(urlparse(request.META.get('HTTP_REFERER'))[2])
        page_id = referer_url_match.kwargs.get('page_id')

    return Page.objects.get(id=page_id).get_children()