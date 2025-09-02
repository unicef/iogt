from wagtail.users.views.users import UserViewSet as WagtailUserViewSet
from .forms import WagtailAdminUserCreateForm, WagtailAdminUserEditForm
class UserViewSet(WagtailUserViewSet):
    def get_form_class(self, for_update=False):
        if for_update:
            return WagtailAdminUserEditForm
        return WagtailAdminUserCreateForm