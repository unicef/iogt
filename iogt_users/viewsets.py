from wagtail.users.views.users import UserViewSet as WagtailUserViewSet
from .forms import WagtailAdminUserCreateForm, WagtailAdminUserEditForm
from wagtail.users.views.users import IndexView as WagtailIndexView
from django.utils.functional import cached_property

from wagtail.admin.ui.tables import BooleanColumn

class CustomUserIndexView(WagtailIndexView):

    @cached_property
    def columns(self):
        # append custom column to the default columns
        return super().columns + [
            BooleanColumn(
                "notification_opt_in",  # internal column name
                label="Notifications Opt-In",
            )
        ]
    
class UserViewSet(WagtailUserViewSet):
    index_view_class = CustomUserIndexView
    def get_form_class(self, for_update=False):
        if for_update:
            return WagtailAdminUserEditForm
        return WagtailAdminUserCreateForm