from django import template
from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import get_object_or_404
from django.urls import translate_url, reverse, resolve, Resolver404
from wagtail.core.models import Locale, Site, Page

from home.models import SectionIndexPage, Section, Article, FooterIndexPage, PageLinkPage, LocaleDetail, HomePage
from iogt.settings.base import LANGUAGES

register = template.Library()


@register.inclusion_tag('home/tags/language_switcher.html', takes_context=True)
def language_switcher(context, page):
    """
    This template tag has evolved over time. The current requirement for this is really tricky.
    See https://github.com/unicef/iogt/pull/955#issuecomment-1008277982 for more context on why this logic is
    complicated.
    """

    switcher_locales = list()
    locales = Locale.objects.select_related('locale_detail').all()

    try:
        if resolve(context.request.path_info).url_name == 'translation-not-found':
            page = get_object_or_404(Page, pk=context.request.GET.get('page'), live=True)
    except Resolver404:
        pass

    for locale in locales:
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
                    translated_url = translate_url(reverse('translation-not-found'), locale.language_code)
                    url = f'{translated_url}?page={page.id}'
            else:  # If the current URL belongs to a django view
                url = translate_url(context.request.path_info, locale.language_code)

            switcher_locales.append((locale, url))

    context.update({
        'locales': switcher_locales,
        'page': page
    })

    return context


@register.inclusion_tag('home/tags/previous-next-buttons.html')
def render_previous_next_buttons(page):
    return {
        'next_sibling': page.get_next_siblings().not_type(PageLinkPage).live().first(),
        'previous_sibling': page.get_prev_siblings().not_type(PageLinkPage).live().first()
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


@register.simple_tag
def is_first_content(page, value):
    is_first_content = False
    if value == 0 and page.get_parent().specific.larger_image_for_top_page_in_list_as_in_v1:
        is_first_content = True

    return is_first_content


@register.inclusion_tag('wagtailadmin/shared/field_as_li.html')
def render_external_link_with_help_text(field):
    field.help_text = f'If you are linking back to a URL on your own IoGT site, be sure to remove the domain and ' \
                      f'everything before it. For example "http://sd.goodinternet.org/url/" should instead be "/url/".'

    return {'field': field, 'red_help_text': True}


@register.inclusion_tag('wagtailadmin/shared/field_as_li.html')
def render_redirect_from_with_help_text(field):
    field.help_text = f'A relative path to redirect from e.g. /en/youth. ' \
                      f'See "https://docs.wagtail.io/en/stable/editor_manual/managing_redirects.html" for more details.'

    return {'field': field, 'red_help_text': True}
