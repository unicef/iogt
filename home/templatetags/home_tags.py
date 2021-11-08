from django import template
from django.urls import translate_url
from wagtail.core.models import Locale, Site

from home.models import SectionIndexPage, Section, Article, FooterIndexPage
from iogt.settings.base import LANGUAGES

register = template.Library()


@register.inclusion_tag('home/tags/language_switcher.html', takes_context=True)
def language_switcher(context, page):
    if page:
        context.update({
            'translations': page.get_translations(inclusive=True).all(),
        })
    context.update({'default_locales': Locale.objects.all()})

    return context


@register.inclusion_tag('home/tags/previous-next-buttons.html')
def render_previous_next_buttons(page):
    return {
        'next_sibling': page.get_next_siblings().live().first(),
        'previous_sibling': page.get_prev_siblings().live().first()
    }


@register.inclusion_tag('home/tags/footer.html', takes_context=True)
def render_footer(context):
    return {
        'pages': FooterIndexPage.get_active_footers(),
        'request': context['request'],
    }


@register.inclusion_tag('home/tags/top_level_sections.html', takes_context=True)
def render_top_level_sections(context):
    return {
        'pages': SectionIndexPage.get_top_level_sections(),
        'request': context['request'],
    }


@register.inclusion_tag('home/tags/section_progress.html')
def render_user_progress(user_progress, show_count=True):
    return {
        **user_progress,
        'show_count': show_count,
    }


@register.inclusion_tag('home/tags/is_completed.html', takes_context=True)
def render_is_content_completed(context, content):
    content = content.specific
    if isinstance(content, (Section, Article)):
        context.update({
            'is_completed': content.is_completed(context['request'])
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
def get_menu_icon(menu_item):
    if hasattr(menu_item.icon, 'url'):
        return menu_item.icon.url
    elif hasattr(menu_item, 'link_page') and isinstance(menu_item.link_page, Section) and hasattr(menu_item.link_page.icon, 'url'):
        return menu_item.link_page.specific.icon.url

    return ''


@register.simple_tag
def is_first_content(value):
    is_first_content = False
    if value == 0:
        is_first_content = True

    return is_first_content
