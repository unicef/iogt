import csv

from django.http import HttpResponse
from wagtail.contrib.forms.views import SubmissionsListView, FormPagesListView as WagtailFormPagesListView


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

    def process_csv_row(self, row_dict):
        processed_row = {}
        for field, value in row_dict.items():
            preprocess_function = self.get_preprocess_function(
                field, value, self.FORMAT_CSV
            )
            processed_value = (
                preprocess_function(value) if preprocess_function else value
            )
            processed_row[field] = processed_value
        return processed_row.values()

    def write_csv_response(self, queryset):
        response = HttpResponse(
            content_type='text/csv',
        )
        response["Content-Disposition"] = 'attachment; filename="{}.csv"'.format(
            self.get_filename()
        )
        writer = csv.writer(response)
        writer.writerow({field: self.get_heading(queryset, field) for field in self.list_export})
        items = []
        for item in queryset:
            items.append(self.process_csv_row(self.to_row_dict(item)))
        writer.writerows(items)
        return response
