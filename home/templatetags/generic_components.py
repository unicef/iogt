from django import template
from wagtail.core.models import Site

from home.models import ThemeSettings
from iogt import settings

register = template.Library()


@register.inclusion_tag('generic_components/primary_button.html')
def primary_button(title, extra_classnames='', href=None, icon_path=None,
                   font_color=None, background_color=None):
    theme_settings = ThemeSettings.for_site(Site.objects.filter(is_default_site=True).first())

    font_color = font_color or theme_settings.primary_button_font_color
    background_color = background_color or theme_settings.primary_button_background_color
    return {
        'title': title,
        'href': href,
        'icon_path': icon_path,
        'font_color': font_color,
        'background_color': background_color,
        'extra_classnames': extra_classnames
    }


@register.inclusion_tag('generic_components/article_card.html')
def article_card(article, background_color=None, font_color=None):
    theme_settings = ThemeSettings.for_site(Site.objects.filter(is_default_site=True).first())

    font_color = font_color or theme_settings.article_card_font_color
    background_color = background_color or theme_settings.article_card_background_color
    return {
        'article': article,
        'background_color': background_color,
        'font_color': font_color
    }


@register.simple_tag
def section_questionnaire_style(section):
    theme_settings = ThemeSettings.for_site(Site.objects.filter(is_default_site=True).first())

    font_color = section.font_color or theme_settings.section_listing_questionnaire_font_color
    background_color = section.background_color or theme_settings.section_listing_questionnaire_background_color

    return f"color:{font_color};background-color:{background_color}"


@register.simple_tag
def language_picker_style():
    theme_settings = ThemeSettings.for_site(Site.objects.filter(is_default_site=True).first())
    return f"color:{theme_settings.language_picker_font_color};background-color:" \
           f"{theme_settings.language_picker_background_color}"


@register.simple_tag
def mobile_navbar_style():
    theme_settings = ThemeSettings.for_site(Site.objects.filter(is_default_site=True).first())
    return f"background-color:{theme_settings.mobile_navbar_background_color}"
