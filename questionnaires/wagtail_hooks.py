from django.urls import path
from django.utils.html import format_html_join
from django.templatetags.static import static

from wagtail import hooks
from wagtail.models import Locale
# myapp/wagtail_hooks.py
from wagtail_transfer.field_adapters import ForeignKeyAdapter

old_get_dependencies = ForeignKeyAdapter.get_dependencies

from questionnaires.views import FormPagesListView, FormDataPerUserView, generate_dashboard


@hooks.register('insert_editor_js', order=0)
def editor_js():
    language_code = Locale.get_active().language_code
    js_files = [
        'js/surveys.js',
    ]
    js_includes = format_html_join('\n', '<script src="{0}"></script>',
        ((static(filename),) for filename in js_files)
    )
    js_includes = f'{js_includes}\n<script src="/{language_code}/jsi18n/"></script>'
    return js_includes


@hooks.register('register_admin_urls')
def register_custom_form_pages_list_view():
    return [
      path('forms/', FormPagesListView.as_view(), name='index'),
      path('form-data/', FormDataPerUserView.as_view(), name='form_data_per_user'),
      path('generate-dashboard/<int:pk>/', generate_dashboard, name='generate_dashboard'),
  ]







def safe_get_dependencies(self, value):
    if not value:
        return set()
    if isinstance(value, int):
        return {(self.related_base_model, value, False)}
    return old_get_dependencies(self, value)

ForeignKeyAdapter.get_dependencies = safe_get_dependencies
