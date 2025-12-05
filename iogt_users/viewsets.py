from wagtail.users.views.users import UserViewSet as WagtailUserViewSet
from .forms import WagtailAdminUserCreateForm, WagtailAdminUserEditForm
from wagtail.users.views.users import IndexView as WagtailIndexView
from django.utils.functional import cached_property
from django.db.models import DateField, OuterRef, Subquery
from django.db.models.fields.json import KeyTextTransform
from django.db.models.functions import Cast
from .views import RegistrationSurveyMixin
from wagtail.admin.ui.tables import Column, BooleanColumn
from questionnaires.models import UserSubmission

class ContentTagsColumn(Column):
    def __init__(self, name="content_tags", **kwargs):
        super().__init__(name, label=kwargs.get("label", "Preferences"), **kwargs)

    def get_value(self, obj):
        pref = getattr(obj, "notificationpreference", None)
        if pref:
            tags = ", ".join(tag.name for tag in pref.content_tags.all())
            return tags or "—"
        return "—"


class GenderColumn(Column):
    def __init__(self, name="gender", **kwargs):
        super().__init__(name, label=kwargs.get("label", "Gender"), **kwargs)
    def get_value(self, obj):
        return getattr(obj, "gender_from_submission", None) or "—"


class DOBColumn(Column):
    def __init__(self, name="dob", **kwargs):
        super().__init__(name, label=kwargs.get("label", "Date of Birth"), **kwargs)
    def get_value(self, obj):
        return getattr(obj, "dob_from_submission", None) or "—"


class LocationColumn(Column):
    def __init__(self, name="location", **kwargs):
        super().__init__(name, label=kwargs.get("label", "Location"), **kwargs)
    def get_value(self, obj):
        return getattr(obj, "location_from_submission", None) or "—"


class CustomUserIndexView(WagtailIndexView):
    def get_queryset(self):
        qs = super().get_queryset().order_by("id")
        latest_qs  = UserSubmission.objects.filter(
            user_id=OuterRef("pk"),
            page__slug="registration-survey"
        ).order_by("-submit_time")
        gender_qs = latest_qs.annotate(
            _gender=KeyTextTransform("gender", "form_data")
        ).values("_gender")[:1]
        dob_qs = latest_qs.annotate(
            _dob=KeyTextTransform("date_of_birth", "form_data")
        ).values("_dob")[:1]
        location_qs = latest_qs.annotate(
            _loc=KeyTextTransform("location", "form_data")
        ).values("_loc")[:1]
        return qs.annotate(
            gender_from_submission=Subquery(gender_qs),
            dob_from_submission=Cast(Subquery(dob_qs), output_field=DateField()),
            location_from_submission=Subquery(location_qs),
        )

    @cached_property
    def columns(self):
        return super().columns + [
            BooleanColumn("notification_opt_in", label="Notifications Opt-In"),
            # ContentTagsColumn(),
            GenderColumn(),
            DOBColumn(),
            LocationColumn(),
        ]


class UserViewSet(WagtailUserViewSet):
    index_view_class = CustomUserIndexView
    def get_form_class(self, for_update=False):
        if for_update:
            return WagtailAdminUserEditForm
        return WagtailAdminUserCreateForm