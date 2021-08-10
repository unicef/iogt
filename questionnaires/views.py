from django.utils import timezone
from wagtail.contrib.forms.views import SubmissionsListView


class CustomSubmissionsListView(SubmissionsListView):
    def get_filename(self):
        from questionnaires.models import Poll, Quiz, Survey

        object_type = ''
        if isinstance(self.form_page, Poll):
            object_type = 'poll'
        elif isinstance(self.form_page, Quiz):
            object_type = 'quiz'
        elif isinstance(self.form_page, Survey):
            object_type = 'survey'

        return f'{object_type}-{self.form_page.title}_{timezone.now().strftime("%Y-%m-%dT%H%M%S")}'
