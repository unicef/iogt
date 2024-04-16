from wagtail.contrib.forms.panels import FormSubmissionsPanel as WagtailFormSubmissionsPanel


class FormSubmissionsPanel(WagtailFormSubmissionsPanel):
    def render(self):
        from home.models import SiteSettings

        registration_survey = SiteSettings.get_for_default_site().registration_survey
        if registration_survey:
            if self.instance in registration_survey.get_translations(inclusive=True):
                return ''

        return super().render()
