from collections import defaultdict

from django.core.exceptions import ValidationError
from django.forms.utils import ErrorList
from django.utils.translation import gettext_lazy as _

from wagtail.admin.forms import WagtailAdminPageForm

from questionnaires.blocks import VALID_SKIP_SELECTORS, SkipState, VALID_SKIP_LOGIC


class SurveyForm(WagtailAdminPageForm):
    form_field_name = 'survey_form_fields'
    _clean_errors = None

    def clean(self):
        cleaned_data = super().clean()

        question_data = {}
        for form in self.formsets[self.form_field_name]:
            form.is_valid()
            question_data[form.cleaned_data['ORDER']] = form

        for form in question_data.values():
            self._clean_errors = {}
            if form.is_valid():
                data = form.cleaned_data
                if data['field_type'] == 'checkbox':
                    if len(data['skip_logic']) != 2:
                        self.add_form_field_error(
                            'field_type',
                            _('Checkbox type questions must have 2 Answer '
                              'Options: a on and off'),
                        )
                elif data['field_type'] in VALID_SKIP_LOGIC:
                    for i, logic in enumerate(data['skip_logic']):
                        if not logic.value['choice']:
                            self.add_stream_field_error(
                                i,
                                'choice',
                                _('This field is required.'),
                            )
                if self.clean_errors:
                    form._errors = self.clean_errors

        return cleaned_data

    def save(self, commit):
        # Tidy up the skip logic when field cant have skip logic
        for form in self.formsets[self.form_field_name]:
            field_type = form.instance.field_type
            # Copy choices values from skip logic to main choices property
            if field_type in VALID_SKIP_SELECTORS:
                choices_values = []
                for skip_logic in form.instance.skip_logic:
                    choices_values.append(skip_logic.value['choice'])
                form.instance.choices = ",".join(choices_values)

            if field_type not in VALID_SKIP_SELECTORS:
                if field_type != 'checkboxes':
                    form.instance.skip_logic = []
                else:
                    for skip_logic in form.instance.skip_logic:
                        skip_logic.value['skip_logic'] = SkipState.NEXT
                        skip_logic.value['question'] = None
            elif field_type == 'checkbox':
                for skip_logic in form.instance.skip_logic:
                    skip_logic.value['choice'] = ''

        return super().save(commit)

    def add_stream_field_error(self, position, field, message):
        if position not in self._clean_errors:
            self._clean_errors[position] = defaultdict(list)
        self._clean_errors[position][field].append(message)

    @property
    def clean_errors(self):
        if self._clean_errors.keys():
            params = {
                key: ErrorList(
                    [ValidationError('Error in form', params=value)]
                )
                for key, value in self._clean_errors.items()
                if isinstance(key, int)
            }
            errors = {
                key: ValidationError(value)
                for key, value in self._clean_errors.items()
                if isinstance(key, str)
            }
            errors.update({
                'skip_logic': ErrorList([ValidationError(
                    'Skip Logic Error',
                    params=params,
                )])
            })
            return errors

    def add_form_field_error(self, field, message):
        if field not in self._clean_errors:
            self._clean_errors[field] = list()
        self._clean_errors[field].append(message)


class QuizForm(WagtailAdminPageForm):
    form_field_name = 'quiz_form_fields'
    _clean_errors = None

    def clean(self):
        cleaned_data = super().clean()

        question_data = {}
        for form in self.formsets[self.form_field_name]:
            form.is_valid()
            question_data[form.cleaned_data['ORDER']] = form

        for form in question_data.values():
            self._clean_errors = {}
            if form.is_valid():
                data = form.cleaned_data
                if data['field_type'] == 'checkbox':
                    if len(data['skip_logic']) != 2:
                        self.add_form_field_error(
                            'field_type',
                            _('Checkbox type questions must have 2 Answer '
                              'Options: a on and off'),
                        )
                elif data['field_type'] in VALID_SKIP_LOGIC:
                    for i, logic in enumerate(data['skip_logic']):
                        if not logic.value['choice']:
                            self.add_stream_field_error(
                                i,
                                'choice',
                                _('This field is required.'),
                            )
                if self.clean_errors:
                    form._errors = self.clean_errors

        return cleaned_data

    def save(self, commit):
        # Tidy up the skip logic when field cant have skip logic
        for form in self.formsets[self.form_field_name]:
            field_type = form.instance.field_type
            # Copy choices values from skip logic to main choices property
            if field_type in VALID_SKIP_SELECTORS:
                choices_values = []
                for skip_logic in form.instance.skip_logic:
                    choices_values.append(skip_logic.value['choice'])
                form.instance.choices = ",".join(choices_values)

            if field_type not in VALID_SKIP_SELECTORS:
                if field_type != 'checkboxes':
                    form.instance.skip_logic = []
                else:
                    for skip_logic in form.instance.skip_logic:
                        skip_logic.value['skip_logic'] = SkipState.NEXT
                        skip_logic.value['question'] = None
            elif field_type == 'checkbox':
                for skip_logic in form.instance.skip_logic:
                    skip_logic.value['choice'] = ''

        return super().save(commit)

    def add_stream_field_error(self, position, field, message):
        if position not in self._clean_errors:
            self._clean_errors[position] = defaultdict(list)
        self._clean_errors[position][field].append(message)

    @property
    def clean_errors(self):
        if self._clean_errors.keys():
            params = {
                key: ErrorList(
                    [ValidationError('Error in form', params=value)]
                )
                for key, value in self._clean_errors.items()
                if isinstance(key, int)
            }
            errors = {
                key: ValidationError(value)
                for key, value in self._clean_errors.items()
                if isinstance(key, str)
            }
            errors.update({
                'skip_logic': ErrorList([ValidationError(
                    'Skip Logic Error',
                    params=params,
                )])
            })
            return errors

    def add_form_field_error(self, field, message):
        if field not in self._clean_errors:
            self._clean_errors[field] = list()
        self._clean_errors[field].append(message)
