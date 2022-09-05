import csv
import datetime
import json
from collections import defaultdict

from django.conf import settings
from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from django.utils import timezone
from wagtail.admin.views.mixins import SpreadsheetExportMixin, Echo
from wagtail.contrib.forms.forms import SelectDateForm
from wagtail.contrib.forms.utils import get_forms_for_user
from wagtail.contrib.forms.views import (
    SubmissionsListView,
    FormPagesListView as WagtailFormPagesListView,
    SafePaginateListView,
)
from xlsxwriter.workbook import Workbook

from questionnaires.models import UserSubmission, SurveyFormField, PollFormField, QuizFormField

User = get_user_model()


class FormPagesListView(WagtailFormPagesListView):
    def get_queryset(self):
        from home.models import SiteSettings

        queryset = super().get_queryset()
        registration_survey = SiteSettings.get_for_default_site().registration_survey
        if registration_survey:
            ids = registration_survey.get_translations(inclusive=True).values_list('id', flat=True)
            if ids:
                queryset = queryset.exclude(id__in=ids)
        return queryset


class CustomSubmissionsListView(SubmissionsListView):
    def get_filename(self):
        return self.form_page.get_export_filename()

    def get_queryset(self):
        return super().get_queryset().select_related('page', 'user')


class FormDataPerUserView(SpreadsheetExportMixin, SafePaginateListView):
    """
    This view is taking inspiration from `wagtail.contrib.forms.views.FormPagesListView` and
    `wagtail.contrib.forms.views.SubmissionsListView`
    """
    template_name = "questionnaires/form_data.html"
    context_object_name = 'form_pages'
    list_export = ['ID', 'Name', 'Submission Date', 'Field', 'Value']
    select_date_form = SelectDateForm
    page_ids = []
    user = None

    def dispatch(self, request, *args, **kwargs):
        self.is_export = (self.request.GET.get('export') in self.FORMATS)
        user_id = self.request.GET.get('user_id')
        self.user = get_object_or_404(User, pk=user_id)
        if self.is_export:
            page_ids = self.request.GET.get('page_ids')
            self.page_ids = page_ids.split(',') if page_ids else []
            self.paginate_by = None
        return super().dispatch(request, *args, **kwargs)

    def get_queryset(self):
        queryset = get_forms_for_user(self.request.user)
        queryset = queryset.filter(
            usersubmission__user_id=self.user.id
        ).distinct().order_by('-last_published_at')

        filtering = self.get_filtering()
        if filtering and isinstance(filtering, dict):
            queryset = queryset.filter(**filtering)

        return queryset

    def get_filtering(self, for_form_pages=True):
        filter_name = 'usersubmission__submit_time__date' if for_form_pages else 'submit_time__date'
        self.select_date_form = SelectDateForm(self.request.GET)
        result = dict()
        if self.select_date_form.is_valid():
            date_from = self.select_date_form.cleaned_data.get('date_from')
            date_to = self.select_date_form.cleaned_data.get('date_to')
            if date_to:
                if date_from:
                    result[f'{filter_name}__range'] = [date_from, date_to]
                else:
                    result[f'{filter_name}__lte'] = date_to
            elif date_from:
                result[f'{filter_name}__gte'] = date_from
        return result

    def render_to_response(self, context, **response_kwargs):
        if self.is_export:
            return self.as_spreadsheet(context['submissions'], self.request.GET.get('export'))
        return super().render_to_response(context, **response_kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        form_pages = context[self.context_object_name]
        if self.is_export:
            if self.page_ids:
                form_pages = form_pages.filter(id__in=self.page_ids)
            context['submissions'] = UserSubmission.objects.select_related('page', 'user').filter(
                user_id=self.user.id, page__in=form_pages, **self.get_filtering(for_form_pages=False)
            ).order_by('-submit_time')
        context.update({
            'select_date_form': self.select_date_form,
            'user_id': self.user.id,
        })
        return context

    def get_form_fields_dict(self):
        context = self.get_context_data()
        form_fields_dict = defaultdict(dict)
        for form_field in [PollFormField, SurveyFormField, QuizFormField]:
            for (page_id, clean_name, admin_label) in form_field.objects.filter(
                    page__in=context[self.context_object_name]).values_list('page_id', 'clean_name', 'admin_label'):
                form_fields_dict[page_id].update({
                    clean_name: admin_label or clean_name
                })
        return form_fields_dict

    def get_rows(self, item, form_fields_dict):
        data = {
            'User': item.user.username,
            'URL': item.page.full_url,
        }
        for clean_name, answer in json.loads(item.form_data).items():
            data.update({
                form_fields_dict.get(item.page_id, {}).get(clean_name): answer,
            })
        return [dict(zip(self.list_export, [item.id, item.page.title, item.submit_time, field, value]))
                for field, value in data.items()]

    def stream_csv(self, queryset):
        writer = csv.DictWriter(Echo(), fieldnames=self.list_export)
        yield writer.writerow(dict(zip(self.list_export, self.list_export)))

        form_fields_dict = self.get_form_fields_dict()

        for item in queryset:
            rows = self.get_rows(item, form_fields_dict)
            for row in rows:
                yield self.write_csv_row(writer, row)

    def write_xlsx(self, queryset, output):
        workbook = Workbook(
            output,
            {
                "in_memory": True,
                "constant_memory": True,
                "remove_timezone": True,
                "default_date_format": "dd/mm/yy hh:mm:ss",
            },
        )
        worksheet = workbook.add_worksheet()
        row_number = 0
        for col_number, field in enumerate(self.list_export):
            worksheet.write(row_number, col_number, self.get_heading(queryset, field))

        form_fields_dict = self.get_form_fields_dict()

        row_number += 1
        for item in queryset:
            rows = self.get_rows(item, form_fields_dict)
            for row in rows:
                self.write_xlsx_row(worksheet, row, row_number)
                row_number += 1

        workbook.close()

    def get_filename(self):
        timestamp = timezone.now().strftime(settings.EXPORT_FILENAME_TIMESTAMP_FORMAT)
        return f'{self.user.username}-submission_{timestamp}'
