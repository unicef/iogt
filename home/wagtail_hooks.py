from abc import ABC
from urllib.parse import urlparse, urlunparse, urlencode

from django.core.exceptions import PermissionDenied
from django.urls import resolve, Resolver404
from django.urls import reverse
from django.utils.html import escape
from django.utils.translation import gettext_lazy as _
from wagtail.contrib.redirects.models import Redirect
from wagtail.core import hooks
from wagtail.core.models import Page
from wagtail.core.models import PageViewRestriction
from wagtail.core.rich_text import LinkHandler
from wagtail.admin.forms.choosers import ExternalLinkChooserForm

from home.models import FooterIndexPage, BannerIndexPage, Section, \
    SectionIndexPage


class ExternalLinkHandler(LinkHandler, ABC):
    identifier = "external"

    @classmethod
    def expand_db_attributes(cls, attrs):
        next_page = escape(attrs["href"])
        parsed_url = urlparse(next_page)
        try:
            resolve(parsed_url.path)
            unparsed_url = urlunparse(('', '', parsed_url.path, parsed_url.params, parsed_url.query, parsed_url.fragment))
            return f'<a href="{unparsed_url}">'
        except Resolver404:
            external_link_page = reverse("external-link")
            return f'<a href="{external_link_page}?{urlencode({"next": next_page})}">'


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
                    if not any(group in current_user_groups for group in
                               restriction.groups.all()):
                        raise PermissionDenied


@hooks.register('construct_explorer_page_queryset')
def sort_page_listing_by_path(parent_page, pages, request):
    if isinstance(parent_page, (
            BannerIndexPage, FooterIndexPage, Section, SectionIndexPage)):
        pages = pages.order_by('path')

    return pages


@hooks.register('construct_main_menu')
def rename_forms_menu_item(request, menu_items):
    for item in menu_items:
        if item.name == "forms":
            item.label = _("Form Data")


@hooks.register('construct_page_chooser_queryset')
def limit_page_chooser(pages, request):
    """
    For featured content page chooser panel in section start from current section
    otherwise don't change wagtail page queryset
    :param pages:
    :param request:
    :return: wagtail page queryset
    """
    current_path_match = resolve(request.path)
    if current_path_match.kwargs:
        # This is for the child pages access in page chooser panel
        page_id = current_path_match.kwargs.get('parent_page_id')
    else:
        # This is for the initial loading of children of current section
        parsed_referer_url = urlparse(request.META.get('HTTP_REFERER'))
        referer_path_match = resolve(parsed_referer_url.path)
        page_id = referer_path_match.kwargs.get('page_id')

    # If parent page is a section then return its children otherwise skip filtering
    if Section.objects.filter(id=page_id).exists():
        pages = Page.objects.get(id=page_id).get_children()

    return pages


Redirect._meta.get_field("old_path").help_text = _(
    'A relative path to redirect from e.g. /en/youth. '
    'See https://docs.wagtail.io/en/stable/editor_manual/managing_redirects.html for more details')

ExternalLinkChooserForm.base_fields['url'].help_text = _(
    'If you are linking back to a URL on your own IoGT site, be sure to remove the domain and everything before it. '
    'For example "http://sd.goodinternet.org/url/" should instead be "/url/".'
)
