from django import template
from wagtail.core.models import Page

from questionnaires.utils import SkipLogicPaginator

register = template.Library()


@register.inclusion_tag('questionnaires/tags/surveys_list.html', takes_context=True)
def render_surveys_list(context, surveys):
    context.update({'surveys': surveys})
    return context


@register.inclusion_tag('questionnaires/tags/polls_list.html', takes_context=True)
def render_polls_list(context, polls):
    context.update({'polls': polls})
    return context


@register.inclusion_tag('questionnaires/tags/quizzes_list.html', takes_context=True)
def render_quizzes_list(context, quizzes):
    context.update({'quizzes': quizzes})
    return context


@register.inclusion_tag('questionnaires/tags/checkbox.html')
def render_checkbox(field):
    return {'field': field}


@register.inclusion_tag('questionnaires/tags/checkboxes.html')
def render_checkboxes(field):
    return {'field': field}


@register.inclusion_tag("questionnaires/tags/select.html")
def render_select(field, is_multiselect=False):
    return {"field": field, "is_multiselect": is_multiselect}


@register.inclusion_tag('questionnaires/tags/textarea.html')
def render_textarea(field):
    return {'field': field}


@register.inclusion_tag('questionnaires/tags/radios.html')
def render_radios(field):
    return {'field': field}


@register.inclusion_tag('questionnaires/tags/text_field.html')
def render_text_field(field):
    return {'field': field}


@register.inclusion_tag('questionnaires/tags/field_description.html')
def field_description(field):
    return {"field": field}


@register.inclusion_tag('questionnaires/tags/render_fields.html')
def render_fields(field, type):
    return {'field': field, "type": type}


@register.inclusion_tag('questionnaires/tags/field_counter.html')
def field_counter(field, form, forloop, form_length, fields_step, questionnaire):
    if form_length != None:
        if form.errors:
            counter = forloop.get("counter")
        else:
            counter = forloop.get("counter") + int(form_length)
    else:
        counter = forloop.get("counter")

    if hasattr(questionnaire, "multi_step") and questionnaire.multi_step or questionnaire.has_page_breaks:
        total = fields_step.paginator.count
    else:
        total = len(form.fields)

    return {"counter": counter, "total": total}


@register.inclusion_tag('questionnaires/tags/submit_button.html')
def render_submit_button(fields_step, page):
    return {"fields_step": fields_step, "page": page}


@register.inclusion_tag('questionnaires/tags/action_url.html')
def get_action_url(page, self, fields_step, request, form):
    return {"page": page, "self": self, "fields_step": fields_step,
            "request": request, "form": form}


@register.inclusion_tag('blocks/embedded_questionnaire.html', takes_context=True)
def render_questionnaire_form(context, questionnaire):
    paginator = SkipLogicPaginator(questionnaire.get_form_fields(), {}, {})
    step = paginator.page(1)
    if hasattr(questionnaire, 'multi_step') and questionnaire.multi_step:
        form_class = questionnaire.get_form_class_for_step(step)
    else:
        form_class = questionnaire.get_form_class()

    form = form_class(page=questionnaire, user=context['request'].user)
    context.update({
        'type': questionnaire.__class__.__name__,
        'form': form,
        'fields_step': step,
        'page': questionnaire
    })
    return context


@register.filter
def get_item(dictionary, key):
    return dictionary.get(key)


@register.filter
def get_value_from_querydict(querydict, key):
    dictionary = dict(querydict)
    return dictionary.get(key)[0]


@register.simple_tag
def snake_case(text):
    return text.lower().replace(" ", "_").replace("__", "_").replace('?',
                                                                     '')


@register.simple_tag
def subtract(value, arg):
    return int(value) - int(arg)
