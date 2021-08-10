from wagtail.contrib.forms.views import SubmissionsListView


class CustomSubmissionsListView(SubmissionsListView):
    def get_filename(self):
        return self.form_page.get_export_filename()
