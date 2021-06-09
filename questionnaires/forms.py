from django.core.exceptions import ValidationError
from modelcluster.fields import ParentalKey
from wagtail.contrib.forms.forms import FormBuilder
from wagtail.contrib.forms.models import AbstractForm, AbstractFormField
from django.db import models
from django import forms
from django.utils.translation import ugettext_lazy as _
from django.utils.html import format_html



CHARACTER_COUNT_CHOICE_LIMIT = 512


# class FormField(AbstractFormField):
#     page = ParentalKey('FormPage', on_delete=models.CASCADE, related_name='custom_form_fields')


class CharacterCountWidget(forms.TextInput):
    class Media:
        js = ('js/widgets/character_count.js',)

    def render(self, name, value, attrs=None):
        max_length = self.attrs['maxlength']
        maximum_text = _('Maximum: {max_length}').format(max_length=max_length)
        return format_html(
            u'{}<span>{}</span>',
            super(CharacterCountWidget, self).render(name, value, attrs),
            maximum_text,
        )


class MultiLineWidget(forms.Textarea):
    def render(self, name, value, attrs=None):
        return format_html(
            u'{}<span>{}</span>',
            super(MultiLineWidget, self).render(name, value, attrs),
            _('No limit'),
        )


class CharacterCountMixin(object):
    max_length = CHARACTER_COUNT_CHOICE_LIMIT

    def __init__(self, *args, **kwargs):
        self.max_length = kwargs.pop('max_length', self.max_length)
        super(CharacterCountMixin, self).__init__(*args, **kwargs)
        self.error_messages['max_length'] = _(
            'This field can not be more than {max_length} characters long'
        ).format(max_length=self.max_length)

    def validate(self, value):
        super(CharacterCountMixin, self).validate(value)
        if len(value) > self.max_length:
            raise ValidationError(
                self.error_messages['max_length'],
                code='max_length', params={'value': value},
            )


class CharacterCountMultipleChoiceField(
        CharacterCountMixin, forms.MultipleChoiceField):
    """ Limit character count for Multi choice fields """


class CharacterCountChoiceField(
        CharacterCountMixin, forms.ChoiceField):
    """ Limit character count for choice fields """


class CharacterCountCheckboxSelectMultiple(
        CharacterCountMixin, forms.CheckboxSelectMultiple):
    """ Limit character count for checkbox fields """


class CharacterCountCheckboxInput(
        CharacterCountMixin, forms.CheckboxInput):
    """ Limit character count for checkbox fields """


class SurveysFormBuilder(FormBuilder):
    def create_singleline_field(self, field, options):
        options['widget'] = CharacterCountWidget
        return super(SurveysFormBuilder, self).create_singleline_field(field,
                                                                       options)

    def create_multiline_field(self, field, options):
        options['widget'] = MultiLineWidget
        return forms.CharField(**options)

    # def create_date_field(self, field, options):
    #     options['widget'] = NaturalDateInput
    #     return super(
    #         SurveysFormBuilder, self).create_date_field(field, options)
    #
    # def create_datetime_field(self, field, options):
    #     options['widget'] = NaturalDateInput
    #     return super(
    #         SurveysFormBuilder, self).create_datetime_field(field, options)

    def create_positive_number_field(self, field, options):
        return forms.DecimalField(min_value=0, **options)

    def create_dropdown_field(self, field, options):
        options['choices'] = map(
            lambda x: (x.strip(), x.strip()),
            field.choices.split(','))
        return CharacterCountChoiceField(**options)

    def create_radio_field(self, field, options):
        options['choices'] = map(
            lambda x: (x.strip(), x.strip()),
            field.choices.split(','))
        return CharacterCountChoiceField(widget=forms.RadioSelect, **options)

    def create_checkboxes_field(self, field, options):
        options['choices'] = [
            (x.strip(), x.strip()) for x in field.choices.split(',')
        ]
        options['initial'] = [
            x.strip() for x in field.default_value.split(',')
        ]
        return CharacterCountMultipleChoiceField(
            widget=forms.CheckboxSelectMultiple, **options)
