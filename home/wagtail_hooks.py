from wagtail.core import hooks
from wagtail.core.models import PageViewRestriction
from django.core.exceptions import PermissionDenied


@hooks.register('before_serve_page', order=-1)
def check_group(page, request, serve_args, serve_kwargs):
    if request.user.is_authenticated:
        for restriction in page.get_view_restrictions():
            if not restriction.accept_request(request):
                if restriction.restriction_type == PageViewRestriction.GROUPS:
                    current_user_groups = request.user.groups.all()
                    if not any(group in current_user_groups for group in restriction.groups.all()):
                        raise PermissionDenied
