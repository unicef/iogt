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
    return {'field': field}


@register.inclusion_tag('questionnaires/tags/textarea.html')
def render_textarea(field):
    return {'field': field}


@register.inclusion_tag('questionnaires/tags/text_field.html')
def render_text_field(field):
    return {'field': field}


@register.inclusion_tag("questionnaires/tags/select.html")
def render_select(field):
    return {"field": field}


@register.inclusion_tag('questionnaires/tags/polls_radios.html')
def render_polls_radios(field):
    return {"field": field}


@register.inclusion_tag('questionnaires/tags/field_description.html')
def field_description(field):
    return {"field": field}


@register.inclusion_tag('questionnaires/tags/render_fields.html')
def render_fields(field, type):
    return {'field': field, "type": type}


@register.inclusion_tag('questionnaires/tags/field_counter.html')
def field_counter(field, form, forloop, form_length, fields_step, self):
    return {"field": field, "form": form, "forloop": forloop,
            "form_length": form_length, "fields_step": fields_step,
            "self": self}


@register.inclusion_tag('questionnaires/tags/submit_button.html')
def render_submit_button(fields_step, page):
    return {"fields_step": fields_step, "page": page}


@register.inclusion_tag('questionnaires/tags/action_url.html')
def get_action_url(page, self, fields_step, request, form):
    return {"page": page, "self": self, "fields_step": fields_step,
            "request": request, "form": form}


@register.filter
def get_item(dictionary, key):
    return dictionary.get(key)


@register.filter
def get_value_from_querydict(querydict, key):
    dictionary = dict(querydict)
    print(dictionary)
    print(key)
    return dictionary.get(key)[0]


@register.simple_tag
def snake_case(text):
    return text.lower().replace(" ", "_").replace("__", "_").replace('?',
                                                                     '')


@register.simple_tag
def subtract(value, arg):
    return int(value) - int(arg)
