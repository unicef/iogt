from django.utils.html import format_html
from django_comments_xtd.models import XtdComment
from wagtail.contrib.modeladmin.options import ModelAdminGroup, ModelAdmin, modeladmin_register

from .button_helpers import XtdCommentAdminButtonHelper
from .filters import FlaggedFilter
from .urls import urlpatterns as urls
from wagtail.core import hooks
from django.conf.urls import include, url


@hooks.register('register_admin_urls')
def register_admin_urls():
    return [
        url(r'^comments/', include(urls)),
    ]


class XtdCommentAdmin(ModelAdmin):
    model = XtdComment
    menu_label = 'All Comments'
    menu_icon = 'edit'
    list_display = ('comment', 'user', 'is_removed', 'is_public', 'num_flags', 'num_replies', 'status')
    list_filter = (FlaggedFilter, 'is_removed', 'is_public', 'submit_date',)
    search_fields = ('comment',)
    list_export = ('comment', 'user', 'is_removed', 'is_public', 'num_flags')
    button_helper_class = XtdCommentAdminButtonHelper

    def status(self, obj):
        if not obj.is_public:
            button_html = f'<span class ="status-tag" > Deleted </span>'
        elif obj.is_removed:
            button_html = f'<span class ="status-tag" > Hidden </span>'
        else:
            button_html = f'<span class ="status-tag primary"> Public </span>'
        return format_html(button_html)

    def get_queryset(self, request):
        return super().get_queryset(request).prefetch_related('flags')

    def num_replies(self, obj):
        return obj.nested_count

    def num_flags(self, obj):
        return obj.flags.count()


class CommentsGroup(ModelAdminGroup):
    menu_label = 'Comments'
    menu_icon = 'openquote'
    menu_order = 600
    items = (XtdCommentAdmin,)


modeladmin_register(CommentsGroup)
