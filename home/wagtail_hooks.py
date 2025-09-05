from urllib.parse import urlparse

from django.conf import settings
from django.contrib.admin import SimpleListFilter
from django.core.exceptions import PermissionDenied
from django.db.models import Q
from django.templatetags.static import static
from django.urls import resolve, reverse
from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _
from wagtail import __version__
from wagtail.admin import widgets as wagtailadmin_widgets
from wagtail.admin.menu import MenuItem, SubmenuMenuItem, Menu
from wagtail_modeladmin.options import ModelAdmin, modeladmin_register
from wagtail.documents.models import Document
from wagtail import hooks
from wagtail.models import Page, PageViewRestriction
from wagtailcache.cache import clear_cache

from home.models import (BannerIndexPage, FooterIndexPage, LocaleDetail,
                         Section, SectionIndexPage, BannerPage, HomePageBanner, HomePage)
from home.translatable_strings import translatable_strings
from translation_manager.models import TranslationEntry
from wagtail.signals import page_published
from django.dispatch import receiver
from iogt.utils import NotifyAndPublishMenuItem, notify_and_publish_view
from .models import Article
from django.urls import path


@hooks.register('after_publish_page')
def clear_cache_on_publish(request, page):
    # Clear only the updated page from cache
    clear_cache(page.url)  # or clear_cache(page) in newer wagtailcache
    

@hooks.register('after_unpublish_page')
@hooks.register('after_delete_page')
def clear_cache_on_unpublish_or_delete(request, page):
    clear_cache(page.url)


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
def update_menu_items(request, menu_items):
    for item in menu_items:
        if item.name == "forms":
            item.label = _("Form Data")
        if item.name == 'translations':
            item.url = f'{TranslationEntryAdmin().url_helper.get_action_url("index")}?limited=yes'
        if item.name == 'community-comment-moderations':
            menu_items.remove(item)


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


@hooks.register("insert_global_admin_css", order=100)
def global_admin_css():
    return format_html(
        '<link rel="stylesheet" href="{}">',
        static("css/global/admin.css"),
    )

@hooks.register("insert_global_admin_css")
def import_fontawesome_stylesheets():
    return "\n".join(
        [
            format_html(
                '<link rel="stylesheet" href="{}">',
                static("css/fontawesome/css/fontawesome.min.css"),
            ),
            format_html(
                '<link rel="stylesheet" href="{}">',
                static("css/fontawesome/css/solid.min.css"),
            ),
        ]
    )


@hooks.register('insert_global_admin_js', order=100)
def global_admin_js():
    return format_html(
        '<script src="{}"></script>',
        static("js/admin.js")
    )


@hooks.register('register_page_listing_buttons')
def page_listing_buttons(page, is_parent=False, next_url=None, user=None, **kwargs):
    if is_parent:
        yield wagtailadmin_widgets.PageListingButton(
            _('Sort child pages'),
            '?ordering=ord',
            attrs={'title': _("Change ordering of child pages of '%(title)s'") % {'title': page.get_admin_display_title()}},
            priority=60
        )


@hooks.register("register_admin_menu_item")
def about():
    items = [
        MenuItem(
            label=f"IoGT {settings.SITE_VERSION}",
            url=f"http://github.com/unicef/iogt/releases/tag/{settings.SITE_VERSION}",
        ),
        MenuItem(
            label=f"Wagtail {__version__}",
            url=f"http://github.com/wagtail/wagtail/releases/tag/v{__version__}"
        )
    ]
    return SubmenuMenuItem(
        label="About",
        menu=Menu(register_hook_name=None, items=items),
        icon_name="info-circle",
        order=999999,
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



class DocumentAdmin(ModelAdmin):
    model = Document
    menu_label = "Documents"
    menu_icon = "doc-full"
    list_display = ("title", "collection", "created_at")
    search_fields = ("title",)
    list_filter = ("collection",)  # ensures collection dropdown in listing page

modeladmin_register(DocumentAdmin)


@hooks.register("insert_global_admin_css")
def hide_add_article_button():
    """
    Inject custom CSS to hide the "Add Article" button in the Wagtail admin.
    """
    return format_html('<link rel="stylesheet" href="/static/css/custom_admin.css">')


@receiver(page_published, sender=BannerPage)
def create_home_page_banner(sender, instance, **kwargs):
    """Ensure a HomePageBanner entry is created after a BannerPage is published."""
    parent = instance.get_parent().specific
    parent = parent.get_parent().specific
    if parent:
        HomePageBanner.objects.get_or_create(source=parent, banner_page=instance)


@hooks.register('register_admin_urls')
def register_custom_form_pages_list_view():
    return [
      path("notify-and-publish/<int:page_id>/", notify_and_publish_view, name="notify_and_publish"),
  ]


@hooks.register('register_page_action_menu_item')
def register_notify_and_publish_menu_item():
    return NotifyAndPublishMenuItem(order=100, allowed_models=Article)  #

@hooks.register('register_page_action_menu_item')
def register_notify_and_publish_menu_item():
    return NotifyAndPublishMenuItem(order=100, allowed_models=Section)  #



@hooks.register("register_context_modifier")
def enable_url_generator(context, request):
    # only apply on image edit views
    if request.resolver_match and request.resolver_match.url_name == "wagtailimages_edit":
        context["url_generator_enabled"] = True



@hooks.register('register_page_listing_more_buttons')
def page_listing_more_buttons(page, user, next_url=None):
    page_perms = page.permissions_for_user(user)
    url = reverse('notify_and_publish', args=[page.id]) 
    print('classname', page.specific_class.__name__)
    if page_perms.can_publish():
        if page.specific_class.__name__=='Article' or page.specific_class.__name__=='Survey' or page.specific_class.__name__=='Section':
            yield wagtailadmin_widgets.Button(
                'Notify & Publish',
                url,
                priority=40,
                attrs={'icon': 'mail'}
            )
