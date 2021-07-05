from django import template

register = template.Library()


@register.inclusion_tag('questionnaires/tags/radios.html')
def render_radios(field):
    return {'field': field}


@register.inclusion_tag('questionnaires/tags/polls_list.html')
def render_polls_list(polls):
    return {'polls': polls}


@register.inclusion_tag('questionnaires/tags/quizzes_list.html')
def render_quizzes_list(quizzes):
    return {'quizzes': quizzes}


@register.filter
def get_item(dictionary, key):
    return dictionary.get(key)
