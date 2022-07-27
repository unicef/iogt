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
