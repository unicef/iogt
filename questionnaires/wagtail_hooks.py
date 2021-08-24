from django.utils.html import format_html_join
from django.templatetags.static import static

from wagtail.core import hooks


@hooks.register('insert_editor_js', order=100)
def editor_js():
    js_files = [
        'js/index.js',
    ]
    js_includes = format_html_join('\n', '<script src="{0}"></script>',
        ((static(filename),) for filename in js_files)
    )
    return js_includes