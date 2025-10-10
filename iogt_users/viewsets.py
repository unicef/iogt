from wagtail.users.views.users import UserViewSet as WagtailUserViewSet
from .forms import WagtailAdminUserCreateForm, WagtailAdminUserEditForm
from wagtail.users.views.users import IndexView as WagtailIndexView
from django.utils.functional import cached_property

from wagtail.admin.ui.tables import Column, BooleanColumn


class ContentTagsColumn(Column):
    def __init__(self, name="content_tags", **kwargs):
        super().__init__(name, label=kwargs.get("label", "Preferences"), **kwargs)

    def get_value(self, obj):
        pref = getattr(obj, "notificationpreference", None)
        if pref:
            tags = ", ".join(tag.name for tag in pref.content_tags.all())
            return tags or "—"
        return "—"



class CustomUserIndexView(WagtailIndexView):

    @cached_property
    def columns(self):
        # append custom column to the default columns
        return super().columns + [
            BooleanColumn(
                "notification_opt_in",  # internal column name
                label="Notifications Opt-In",
            ),
            ContentTagsColumn(),
        ]
    
class UserViewSet(WagtailUserViewSet):
    index_view_class = CustomUserIndexView
    def get_form_class(self, for_update=False):
        if for_update:
            return WagtailAdminUserEditForm
        return WagtailAdminUserCreateForm