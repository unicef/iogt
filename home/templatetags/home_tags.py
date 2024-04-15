from django import template
import django.utils.translation as translation
from django.shortcuts import get_object_or_404
from django.urls import translate_url, reverse, resolve, Resolver404
from django.conf import settings
from wagtail.models import Locale, Site, Page

from home.models import (
    Article,
    FooterIndexPage,
    LocaleDetail,
    PageLinkPage,
    Section,
    SectionIndexPage,
)
from iogt.settings.base import LANGUAGES

register = template.Library()


@register.inclusion_tag('home/tags/language_switcher.html', takes_context=True)
def language_switcher(context, page):
    """
    The current requirement for this is really tricky.
    See https://github.com/unicef/iogt/pull/955#issuecomment-1008277982 for more
    context on why this logic is complicated.
    """

    language_options = list()
    locales = Locale.objects.select_related('locale_detail').all()
    current_language = translation.get_language_info(translation.get_language())

    try:
        if resolve(context.request.path_info).url_name == 'translation-not-found':
            page = get_object_or_404(
                Page,
                pk=context.request.GET.get('page'),
                live=True,
            )
    except Resolver404:
        pass

    for locale in locales:
        option = {}
        try:
            language = translation.get_language_info(locale.language_code)
            option['language'] = language
            option['selected'] = locale.language_code == current_language.get('code')
        except:
            continue

        try:
            should_append = locale.locale_detail.is_active
        except LocaleDetail.DoesNotExist:
            should_append = True

        if should_append:
            if page:  # If the current URL belongs to a wagtail page
                translated_page = page and page.get_translation_or_none(locale)
                if translated_page and translated_page.live:
                    url = translated_page.url
                else:
                    translated_url = translate_url(
                        reverse('translation-not-found'),
                        locale.language_code,
                    )
                    url = f'{translated_url}?page={page.id}'
            else:  # If the current URL belongs to a django view
                url = translate_url(context.request.path_info, locale.language_code)

            option['url'] = url
            language_options.append(option)

    context.update({
        'language_options': language_options,
        'current_language': current_language,
    })

    return context


@register.inclusion_tag('home/tags/previous-next-buttons.html')
def render_previous_next_buttons(page):
    return {
        'next_sibling': page.get_next_siblings().not_type(PageLinkPage).live().first(),
        'previous_sibling': (
            page.get_prev_siblings().not_type(PageLinkPage).live().first()
        )
    }


@register.inclusion_tag('home/tags/footer.html', takes_context=True)
def render_footer(context):
    return {
        'footers': FooterIndexPage.get_active_footers(),
        'request': context['request'],
    }


@register.inclusion_tag('home/tags/top_level_sections.html', takes_context=True)
def render_top_level_sections(context):
    return {
        'top_level_sections': SectionIndexPage.get_top_level_sections(),
        'request': context['request'],
    }


@register.inclusion_tag('home/tags/section_progress.html')
def render_user_progress(user_progress, show_count=True):
    return {
        **user_progress,
        'show_count': show_count,
    }


@register.inclusion_tag('home/tags/is_complete.html', takes_context=True)
def render_is_complete(context, page):
    if isinstance(page, (Section, Article)):
        context.update({
            'is_complete': page.is_complete(context['request'])
        })
    return context


@register.simple_tag
def locale_set(locale, url):
    for item in LANGUAGES:
        code = item[0]
        url = url.replace(f"/{code}/", "")
    return f'/{locale}/{url}'


@register.simple_tag
def translated_home_page_url(language_code):
    locale = Locale.objects.get(language_code=language_code)
    default_home_page = Site.objects.filter(is_default_site=True).first().root_page
    home_page = default_home_page.get_translation_or_none(locale)
    page = home_page or default_home_page
    return page.url


@register.simple_tag(takes_context=True)
def change_lang(context, lang=None, *args, **kwargs):
    path = context['request'].path
    return translate_url(path, lang)


@register.inclusion_tag('home/tags/image.html', takes_context=True)
def render_image(context, image, half_width=False, img_class=None):
    width = settings.IMAGE_SIZE_PRESET
    if half_width:
        width //= 2

    context.update({
        'image': image,
        'width': width,
        'class': img_class,
    })
    return context


@register.inclusion_tag('home/tags/social_meta_tags.html', takes_context=True)
def social_meta_tags(context):
    width = settings.IMAGE_SIZE_PRESET
    page = context.get('page')
    if hasattr(page, 'lead_image') and page.lead_image:
        lead_image = page.lead_image.get_rendition(f'width-{width}')
        context['lead_image'] = lead_image

    if page:
        context['site_name'] = page.get_site().site_name

    return context
