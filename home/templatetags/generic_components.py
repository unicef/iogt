from urllib.parse import urlencode, parse_qs, urlparse

from django import template
from django.conf import settings
from django.urls import reverse
from google_analytics import CAMPAIGN_TRACKING_PARAMS

import iogt.iogt_globals as globals_


register = template.Library()


@register.inclusion_tag('generic_components/primary_button.html')
def primary_button(title, extra_classnames='', href=None, icon_path=None, icon=None, font_color=None,
                   background_color=None):
    theme_settings = globals_.theme_settings

    font_color = font_color or theme_settings.primary_button_font_color
    background_color = background_color or theme_settings.primary_button_background_color

    return {
        'title': title,
        'href': href,
        'icon_path': icon_path,
        'icon': icon,
        'font_color': font_color,
        'background_color': background_color,
        'extra_classnames': extra_classnames,
    }


@register.inclusion_tag('generic_components/article_card.html', takes_context=True)
def render_article_card(context, page, is_first_content=False, display_section_title=False, background_color=None, font_color=None):
    theme_settings = globals_.theme_settings

    font_color = font_color or theme_settings.article_card_font_color
    background_color = background_color or theme_settings.article_card_background_color

    context.update({
        'article': page,
        'is_first_content': is_first_content,
        'display_section_title': display_section_title,
        'background_color': background_color,
        'font_color': font_color
    })
    return context


@register.inclusion_tag('generic_components/section_card.html', takes_context=True)
def render_section_card(context, page, is_first_content=False, background_color=None, font_color=None):
    theme_settings = globals_.theme_settings

    font_color = font_color or theme_settings.section_card_font_color
    background_color = background_color or theme_settings.section_card_background_color

    context.update({
        'section': page,
        'is_first_content': is_first_content,
        'background_color': background_color,
        'font_color': font_color
    })
    return context


@register.inclusion_tag('generic_components/questionnaire_card.html', takes_context=True)
def render_questionnaire_card(context, page, background_color=None, font_color=None):
    theme_settings = globals_.theme_settings

    font_color = font_color or theme_settings.section_listing_questionnaire_font_color
    background_color = background_color or theme_settings.section_listing_questionnaire_background_color

    context.update({
        'questionnaire': page,
        'background_color': background_color,
        'font_color': font_color
    })
    return context


@register.inclusion_tag('generic_components/interactive_card.html', takes_context=True)
def render_interactive_card(context, page=None, background_color=None, font_color=None):

    context.update({
        'interactive': page,
        'background_color': background_color,
        'font_color': font_color,
    })
    return context


@register.simple_tag
def language_picker_style():
    theme_settings = globals_.theme_settings
    return f"color:{theme_settings.language_picker_font_color};background-color:" \
           f"{theme_settings.language_picker_background_color}"


@register.simple_tag(takes_context=True)
def google_analytics(context, tracking_code=None, debug=False):
    if not tracking_code:
        try:
            assert settings.GOOGLE_ANALYTICS['google_analytics_id']
        except KeyError:
            return ''
    # attempt get the request from the context
    request = context.get('request', None)
    if request is None:
        raise RuntimeError("Request context required")
    # intialise the parameters collection
    params = {}
    # collect the campaign tracking parameters from the request
    for param in CAMPAIGN_TRACKING_PARAMS.values():
        value = request.GET.get(param, None)
        if value:
            params[param] = value
    # pass on the referer if present
    referer = request.META.get('HTTP_REFERER', None)
    if referer:
        params['r'] = referer
    # remove collected parameters from the path and pass it on
    path = request.get_full_path()
    parsed_url = urlparse(path)
    query = parse_qs(parsed_url.query, keep_blank_values=True)
    for param in params:
        if param in query:
            del query[param]
    query = urlencode(query, doseq=True)
    new_url = parsed_url._replace(query=query)
    params['p'] = new_url.geturl()
    params['tracking_code'] = tracking_code or settings.GOOGLE_ANALYTICS[
        'google_analytics_id']
    # append the debug parameter if requested
    if debug:
        params['utmdebug'] = 1
    # build and return the url
    url = reverse('google-analytics')
    if params:
        url += '?&' + urlencode(params)
    return url
