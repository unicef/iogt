from urllib.parse import urlparse

from django.contrib.admin import SimpleListFilter
from django.core.exceptions import PermissionDenied
from django.db.models import Q
from django.urls import resolve
from django.utils.translation import gettext_lazy as _
from translation_manager.models import TranslationEntry
from wagtail.contrib.modeladmin.options import ModelAdmin, modeladmin_register
from django.templatetags.static import static
from django.utils.html import format_html
from wagtail.core import hooks
from wagtail.core.models import Page
from wagtail.core.models import PageViewRestriction

from home.models import FooterIndexPage, BannerIndexPage, Section, \
    SectionIndexPage, LocaleDetail
from home.translatable_strings import translatable_strings


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
        if item.name == 'translations':
            item.url = f'{TranslationEntryAdmin().url_helper.get_action_url("index")}?limited=yes'


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


@hooks.register('insert_global_admin_css', order=100)
def global_admin_css():
    return format_html('<link rel="stylesheet" href="{}">', static('css/global/admin.css'))


@hooks.register('insert_global_admin_js', order=100)
def global_admin_js():
    return format_html(
        '<script src="{}"></script>',
        static("js/global/admin.js")
    )


class LimitedTranslatableStringsFilter(SimpleListFilter):
    title = _('limited translatable strings')
    parameter_name = 'limited'

    def lookups(self, request, model_admin):
        return (
            ('yes', 'Yes'),
            ('no', 'No'),
        )

    def queryset(self, request, queryset):
        if self.value() in ['yes']:
            translatable_string_filter = Q()
            for translatable_string in translatable_strings:
                translatable_string_filter |= Q(original__iexact=translatable_string)
            queryset = queryset.filter(translatable_string_filter)

        return queryset


class MissingTranslationsFilter(SimpleListFilter):
    title = _('missing translations')
    parameter_name = 'missing'

    def lookups(self, request, model_admin):
        return (
            ('yes', 'Yes'),
            ('no', 'No'),
        )

    def queryset(self, request, queryset):
        if self.value() == 'yes':
            queryset = queryset.filter(translation='')
        if self.value() == 'no':
            queryset = queryset.exclude(translation='')

        return queryset


class TranslationEntryAdmin(ModelAdmin):
    model = TranslationEntry
    menu_label = 'Translations'
    menu_icon = 'edit'
    list_display = ('original', 'language', 'translation',)
    list_filter = ('language', LimitedTranslatableStringsFilter, MissingTranslationsFilter)
    search_fields = ('original', 'translation',)
    index_template_name = 'modeladmin/translation_manager/translationentry/index.html'
    menu_order = 601


class LocaleDetailAdmin(ModelAdmin):
    model = LocaleDetail
    menu_label = 'Locale Detail'
    menu_icon = 'site'
    list_display = ('locale', 'is_active', 'is_main_language',)
    list_filter = ('is_active', 'is_main_language',)
    add_to_settings_menu = True
    menu_order = 700


modeladmin_register(TranslationEntryAdmin)
modeladmin_register(LocaleDetailAdmin)
