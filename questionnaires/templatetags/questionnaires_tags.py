from django import template
from django.db.models import Q
from wagtail.core.models import Page

from questionnaires.models import Poll
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
def render_field(field):
    return {'field': field}


@register.inclusion_tag('questionnaires/tags/field_counter.html')
def field_counter(form, forloop, form_length, fields_step, questionnaire):
    if form_length != None:
        if form.errors:
            counter = forloop.get("counter")
        else:
            counter = forloop.get("counter") + int(form_length or 0)
    else:
        counter = forloop.get("counter")

    if hasattr(questionnaire, "multi_step") and (questionnaire.multi_step or questionnaire.has_page_breaks):
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


@register.inclusion_tag('blocks/embedded_questionnaires_wrapper.html', takes_context=True)
def render_questionnaire_form(context, questionnaire):
    request = context['request']

    form_class = questionnaire.get_form_class()

    if isinstance(questionnaire, Poll):
        template = 'blocks/embedded_poll.html'
        context.update({
            'results': questionnaire.specific.get_results(),
        })
    else:
        template = 'blocks/embedded_questionnaire.html'
        paginator = SkipLogicPaginator(questionnaire.get_form_fields(), {}, {})
        step = paginator.page(1)
        if hasattr(questionnaire, 'multi_step') and questionnaire.multi_step:
            form_class = questionnaire.get_form_class_for_step(step)
        context.update({
            'fields_step': step,
        })

    context.update({
        'template': template,
        'page': questionnaire,
    })

    multiple_submission_filter = (
        Q(session_key=request.session.session_key) if request.user.is_anonymous else Q(user__pk=request.user.pk)
    )
    multiple_submission_check = (
            not questionnaire.allow_multiple_submissions
            and questionnaire.get_submission_class().objects.filter(multiple_submission_filter,
                                                                    page=questionnaire).exists()
    )
    anonymous_user_submission_check = request.user.is_anonymous and not questionnaire.allow_anonymous_submissions
    if multiple_submission_check or anonymous_user_submission_check:
        return context

    form = form_class(page=questionnaire, user=context['request'].user)

    context.update({
        'form': form,
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
