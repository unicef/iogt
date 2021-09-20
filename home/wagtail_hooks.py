from abc import ABC
from urllib.parse import urlparse, urlunparse, urlencode

from django.contrib.admin import SimpleListFilter
from django.core.exceptions import PermissionDenied
from django.db.models import Q
from django.urls import resolve, Resolver404
from django.urls import reverse
from django.utils.html import escape
from django.utils.translation import gettext_lazy as _
from translation_manager.models import TranslationEntry
from wagtail.contrib.modeladmin.options import ModelAdmin, modeladmin_register
from wagtail.contrib.redirects.models import Redirect
from wagtail.core import hooks
from wagtail.core.models import Page
from wagtail.core.models import PageViewRestriction
from wagtail.core.rich_text import LinkHandler

from home.models import FooterIndexPage, BannerIndexPage, Section, \
    SectionIndexPage
from home.views import TranslationEditView


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


class LimitedTranslatableStringsFilter(SimpleListFilter):
    title = _('limited translatable strings')
    parameter_name = 'limited'

    def lookups(self, request, model_admin):
        return (
            ('yes', 'Yes'),
            ('no', 'No'),
        )

    def queryset(self, request, queryset):
        if self.value() in ['yes', None]:
            translatable_strings = [
                'Are you sure you want to report this comment as inappropriate?',
                'moderator',
                'If you cannot view the above video, perhaps would you like to %(start_link)s download it? %(end_link)s.',
                "Sorry, '%(page_title)s' is not available in [language]. If you want to keep browsing in [language] you can click  <a href=\"%(url)s\">here</a> to return the homepage.",
                'Sections',
                'This appears to be your first visit here. Our website is also available as a downloadable app.',
                'Would you like to download it?',
                'Download',
                "Your app is now ready to install. If you are using a iOS device, you can install it by clicking 'Share', scrolling down and tapping 'Add to Home Screen. If using Android choose 'Add to home screen' and you should be all set!",
                'Install this website as an app on your device?',
                'Are you sure you want to delete this conversation?',
                'Are you sure you want to delete this comment?',
                'Delete',
                'You are leaving the <b>Internet of Good Things</b> to visit an external website and standard data charges by your network provider might apply',
                'Continue to external site',
                'Check if apply',
                'Required',
                'Log Out',
                'This field is required.',
                'Enter a valid username. This value may contain only letters, numbers, and @/./+/-/_ characters.',
                'This password is too short. It must contain at least %(min_length)d character.',
                'This password is too short. It must contain at least %(min_length)d characters.',
                'Remember me',
                'You have signed out.',
            ]
            translatable_string_filter = Q()
            for translatable_string in translatable_strings:
                translatable_string_filter |= Q(original__iexact=translatable_string)
            queryset = queryset.filter(translatable_string_filter)

        return queryset


class TranslationEntryAdmin(ModelAdmin):
    model = TranslationEntry
    menu_label = 'Translations'
    menu_icon = 'edit'
    list_display = ('original', 'language', 'translation',)
    list_filter = ('language', LimitedTranslatableStringsFilter)
    search_fields = ('original', 'translation',)
    edit_view_class = TranslationEditView
    index_template_name = 'modeladmin/translation_manager/translationentry/index.html'
    menu_order = 601


modeladmin_register(TranslationEntryAdmin)
