from django import template

register = template.Library()


@register.inclusion_tag('questionnaires/tags/radios.html')
def render_radios(field):
    return {'field': field}


@register.inclusion_tag('questionnaires/tags/checkboxes.html')
def render_checkboxes(field):
    print(field)
    return {'field': field}


@register.inclusion_tag('questionnaires/tags/textarea.html')
def render_textarea(field):
    print(field)
    return {'field': field}


@register.inclusion_tag('questionnaires/tags/text_field.html')
def render_text_field(field):
    return {'field': field}


@register.filter
def get_item(dictionary, key):
    return dictionary.get(key)
