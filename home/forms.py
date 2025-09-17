from django.apps import apps
from wagtail.admin.forms import WagtailAdminPageForm

class SectionPageForm(WagtailAdminPageForm):

    def clean(self):
        cleaned_data = super().clean()

        if cleaned_data['show_progress_bar']:
            Section = apps.get_model('home', 'Section')
            if self.instance not in Section.get_progress_bar_eligible_sections():
                progress_bar_enabled_ancestor_title = self.instance.get_progress_bar_enabled_ancestor().title
                self.add_error(
                    'show_progress_bar',
                    f'This section is not eligible for showing the progress bar. '
                    f'Disable "Show Progress Bar" on "{progress_bar_enabled_ancestor_title}" section first.')

        return cleaned_data