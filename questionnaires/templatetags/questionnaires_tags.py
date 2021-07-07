from django import template

register = template.Library()


@register.inclusion_tag('questionnaires/tags/surveys_list.html')
def render_surveys_list(surveys):
    return {'surveys': surveys}


@register.inclusion_tag('questionnaires/tags/polls_list.html')
def render_polls_list(polls):
    return {'polls': polls}


@register.inclusion_tag('questionnaires/tags/quizzes_list.html')
def render_quizzes_list(quizzes):
    return {'quizzes': quizzes}


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


@register.inclusion_tag('questionnaires/tags/polls_radios.html')
def render_polls_radios(field):
    return {"field": field}


@register.filter
def get_item(dictionary, key):
    return dictionary.get(key)


@register.filter
def get_value_from_querydict(querydict, key):
    dictionary = dict(querydict)
    return dictionary.get(key)[0]


@register.simple_tag
def snake_case(text):
    return text.lower().replace(" ", "_").replace("__", "_").replace('?', '')
