from django import template
from django.db.models import Q

from questionnaires.models import Poll
from questionnaires.utils import SkipLogicPaginator
import iogt.iogt_globals as globals_

register = template.Library()


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
def render_submit_button(page, fields_step=None):
    return {'submit_button_text': page.get_submit_button_text(fields_step)}


@register.inclusion_tag('questionnaires/tags/action_url.html')
def get_action_url(page, self, fields_step, request, form):
    return {"page": page, "self": self, "fields_step": fields_step,
            "request": request, "form": form}


@register.inclusion_tag('questionnaires/tags/questionnaire_template_wrapper.html', takes_context=True)
def render_questionnaire_form(context, page, background_color=None, font_color=None):
    theme_settings = globals_.theme_settings

    font_color = font_color or theme_settings.section_listing_questionnaire_font_color
    background_color = background_color or theme_settings.section_listing_questionnaire_background_color

    request = context['request']

    form_class = page.get_form_class()

    if isinstance(page, Poll):
        template = 'questionnaires/tags/embedded_poll.html'
        context.update({
            'results': page.get_results(),
            'result_as_percentage': page.result_as_percentage,
        })
    else:
        template = 'questionnaires/tags/embedded_questionnaire.html'
        if hasattr(page, 'multi_step') and page.multi_step and page.get_form_fields():
            paginator = SkipLogicPaginator(page.get_form_fields(), {}, {})
            step = paginator.page(1)
            form_class = page.get_form_class_for_step(step)
            context.update({
                'fields_step': step,
            })

    context.update({
        'template': template,
        'font_color': font_color,
        'background_color': background_color,
        'questionnaire': page,
    })
    if request.method == 'POST':
        form = page.get_form(request.POST, page=page, user=request.user)
        if form.is_valid():
            context.update(page.get_context(request))  # This includes result & feedback
    else:
        form = page.get_form(page=page, user=request.user)

    multiple_submission_filter = (
        Q(session_key=request.session.session_key) if request.user.is_anonymous else Q(user__pk=request.user.pk)
    )
    multiple_submission_check = (
            not page.allow_multiple_submissions
            and page.get_submission_class().objects.filter(multiple_submission_filter,
                                                           page=page).exists()
    )
    anonymous_user_submission_check = request.user.is_anonymous and not page.allow_anonymous_submissions
    if multiple_submission_check or anonymous_user_submission_check:
        context.update({
            'form': None,
        })
        return context

    form = form_class(page=page, user=context['request'].user)

    context.update({
        'form': form,
    })

    return context


@register.filter
def get_item(dictionary, key):
    return dictionary.get(key)


@register.simple_tag
def subtract(value, arg):
    return int(value) - int(arg)


@register.inclusion_tag('questionnaires/tags/questionnaire_wrapper.html', takes_context=True)
def render_questionnaire_wrapper(context, page, direct_display=False, background_color=None, font_color=None):
    context.update({
        'questionnaire': page,
        'direct_display': direct_display,
        'background_color': background_color,
        'font_color': font_color,
    })
    return context


@register.simple_tag
def get_answer_options(field, field_option, fields_info):
    label = field_option.choice_label
    correct_answers = fields_info.get(field.name, {}).get('correct_answer_list', [])
    is_selected = field_option.data.get('selected', False)
    rv = ''
    if is_selected and label in correct_answers:
        rv = {
            'class': 'success',
            'aria_label': 'Checkbox with tick, indicating correct and selected',
        }
    elif is_selected and label not in correct_answers:
        rv = {
            'class': 'error',
            'aria_label': 'Checkbox with X, indicating incorrect and selected',
        }
    elif not is_selected and label in correct_answers:
        rv = {
            'class': 'clear-tick',
            'aria_label': 'Checkbox with tick, indicating correct but not selected',
        }
    elif not is_selected and label not in correct_answers:
        rv = {
            'class': 'clear-cross',
            'aria_label': 'Checkbox with X, indicating incorrect and not selected',
        }

    return rv


@register.simple_tag
def get_feedback_options(field, field_option, fields_info):
    label = field_option.choice_label
    correct_answers = fields_info.get(field.name, {}).get('correct_answer_list', [])
    selected_answer = fields_info.get(field.name, {}).get('selected_answer', [])
    is_selected =  label in selected_answer
    rv = ''
    if is_selected and label in correct_answers:
        rv = {
            'class': 'success',
            'aria_label': 'Checkbox with tick, indicating correct and selected',
        }
    elif is_selected and label not in correct_answers:
        rv = {
            'class': 'error',
            'aria_label': 'Checkbox with X, indicating incorrect and selected',
        }
    elif not is_selected and label in correct_answers:
        rv = {
            'class': 'clear-tick',
            'aria_label': 'Checkbox with tick, indicating correct but not selected',
        }
    elif not is_selected and label not in correct_answers:
        rv = {
            'class': 'clear-cross',
            'aria_label': 'Checkbox with X, indicating incorrect and not selected',
        }

    return rv