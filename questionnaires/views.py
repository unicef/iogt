import csv
import datetime
import json

from django.utils.decorators import method_decorator
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import status
from rest_framework.generics import ListAPIView, RetrieveAPIView
from wagtail.admin.views.mixins import SpreadsheetExportMixin, Echo
from wagtail.contrib.forms.forms import SelectDateForm
from wagtail.contrib.forms.utils import get_forms_for_user
from wagtail.contrib.forms.views import (
    SubmissionsListView,
    FormPagesListView as WagtailFormPagesListView,
    SafePaginateListView,
)
from wagtail.core.models import Page
from xlsxwriter.workbook import Workbook

from questionnaires.filters import QuestionnaireFilter, UserSubmissionFilter
from questionnaires.models import QuestionnairePage, Survey, Poll, Quiz, UserSubmission
from iogt.paginators import IoGTPagination
from questionnaires.serializers import (
    QuestionnairePageSerializer,
    SurveyPageDetailSerializer,
    PollPageDetailSerializer,
    QuizPageDetailSerializer,
    UserSubmissionSerializer,
    QuestionnairePageDetailSerializer,
)


class FormPagesListView(WagtailFormPagesListView):
    def get_queryset(self):
        from home.models import SiteSettings

        queryset = super().get_queryset()
        registration_survey = SiteSettings.get_for_default_site().registration_survey
        if registration_survey:
            ids = registration_survey.get_translations(inclusive=True).values_list('id', flat=True)
            if ids:
                queryset = queryset.exclude(id__in=ids)
        return queryset


class CustomSubmissionsListView(SubmissionsListView):
    def get_filename(self):
        return self.form_page.get_export_filename()

    def get_queryset(self):
        return super().get_queryset().select_related('page', 'user')


class UserSubmissionFormsView(SpreadsheetExportMixin, SafePaginateListView):
    template_name = "questionnaires/form_pages.html"
    context_object_name = 'form_pages'
    list_export = ['ID', 'Name', 'Submission Date', 'Field', 'Value']
    select_date_form = SelectDateForm

    def dispatch(self, request, *args, **kwargs):
        self.is_export = (self.request.GET.get('export') in self.FORMATS)
        if self.is_export:
            self.paginate_by = None
        return super().dispatch(request, *args, **kwargs)

    def get_queryset(self):
        """ Return the queryset of form pages for this view """
        queryset = get_forms_for_user(self.request.user)
        queryset = queryset.filter(
            usersubmission__user_id=self.request.GET.get('user_id')
        ).distinct().order_by('-last_published_at')

        filtering = self.get_filtering()
        if filtering and isinstance(filtering, dict):
            queryset = queryset.filter(**filtering)

        return queryset

    def get_filtering(self, for_form_pages=True):
        """ Return filering as a dict for form pages or submissions queryset """
        filter_name = 'usersubmission__submit_time' if for_form_pages else 'submit_time'
        self.select_date_form = SelectDateForm(self.request.GET)
        result = dict()
        if self.select_date_form.is_valid():
            date_from = self.select_date_form.cleaned_data.get('date_from')
            date_to = self.select_date_form.cleaned_data.get('date_to')
            if date_to:
                # careful: date_to must be increased by 1 day
                # as submit_time is a time so will always be greater
                date_to += datetime.timedelta(days=1)
                if date_from:
                    result[f'{filter_name}__range'] = [date_from, date_to]
                else:
                    result[f'{filter_name}__lte'] = date_to
            elif date_from:
                result[f'{filter_name}__gte'] = date_from
        return result

    def render_to_response(self, context, **response_kwargs):
        if self.is_export:
            return self.as_spreadsheet(context['submissions'], self.request.GET.get('export'))
        return super().render_to_response(context, **response_kwargs)

    def get_context_data(self, **kwargs):
        """ Return context for view """
        context = super().get_context_data(**kwargs)
        form_pages = context[self.context_object_name]
        if self.is_export:
            context['submissions'] = UserSubmission.objects.select_related('page', 'user').filter(
                user_id=self.request.GET.get('user_id'), page__in=form_pages, **self.get_filtering(for_form_pages=False)
            ).order_by('-submit_time')
        context.update({
            'select_date_form': self.select_date_form,
            'user_id': self.request.GET.get('user_id'),
        })
        return context

    def stream_csv(self, queryset):
        """ Generate a csv file line by line from queryset, to be used in a StreamingHTTPResponse """
        writer = csv.DictWriter(Echo(), fieldnames=self.list_export)
        yield writer.writerow(
            {field: self.get_heading(queryset, field) for field in self.list_export}
        )

        for item in queryset:
            row_dict = dict(zip(self.list_export, [item.id, item.page.title, item.submit_time, 'User', item.user.username]))
            yield self.write_csv_row(writer, row_dict)
            row_dict = dict(zip(self.list_export, [item.id, item.page.title, item.submit_time, 'URL', item.page.full_url]))
            yield self.write_csv_row(writer, row_dict)
            form_data = json.loads(item.form_data)
            for k, v in form_data.items():
                row_dict = dict(zip(self.list_export, [item.id, item.page.title, item.submit_time, k, v]))
                yield self.write_csv_row(writer, row_dict)

    def write_xlsx(self, queryset, output):
        """ Write an xlsx workbook from a queryset"""
        workbook = Workbook(
            output,
            {
                "in_memory": True,
                "constant_memory": True,
                "remove_timezone": True,
                "default_date_format": "dd/mm/yy hh:mm:ss",
            },
        )
        worksheet = workbook.add_worksheet()
        row_number = 0
        for col_number, field in enumerate(self.list_export):
            worksheet.write(row_number, col_number, self.get_heading(queryset, field))

        row_number += 1
        for item in queryset:
            row_dict = dict(zip(self.list_export, [item.id, item.page.title, item.submit_time, 'User', item.user.username]))
            self.write_xlsx_row(worksheet, row_dict, row_number)
            row_number += 1
            row_dict = dict(zip(self.list_export, [item.id, item.page.title, item.submit_time, 'URL', item.page.full_url]))
            self.write_xlsx_row(worksheet, row_dict, row_number)
            row_number += 1
            form_data = json.loads(item.form_data)
            for k, v in form_data.items():
                row_dict = dict(zip(self.list_export, [item.id, item.page.title, item.submit_time, k, v]))
                self.write_xlsx_row(worksheet, row_dict, row_number)
                row_number += 1

        workbook.close()


class QuestionnairesListAPIView(ListAPIView):
    serializer_class = QuestionnairePageSerializer
    filterset_class = QuestionnaireFilter
    pagination_class = IoGTPagination

    def get_queryset(self):
        accessible_page_ids = self.request.user.get_accessible_page_ids
        return Page.objects.filter(id__in=accessible_page_ids).type(QuestionnairePage).order_by('-last_published_at')


@method_decorator(name='get', decorator=swagger_auto_schema(
    responses={
        status.HTTP_200_OK: openapi.Response(
            description="Questionnaire Page Detail Serializer",
            schema=QuestionnairePageDetailSerializer,
        )
    }
))
class QuestionnaireDetailAPIView(RetrieveAPIView):
    queryset = Page.objects.type(QuestionnairePage).specific()

    def get_queryset(self):
        accessible_page_ids = self.request.user.get_accessible_page_ids
        return Page.objects.filter(id__in=accessible_page_ids).type(QuestionnairePage).specific().order_by(
            '-last_published_at')

    def get_serializer_class(self):
        page = self.get_object()
        if isinstance(page, Poll):
            return PollPageDetailSerializer
        elif isinstance(page, Survey):
            return SurveyPageDetailSerializer
        elif isinstance(page, Quiz):
            return QuizPageDetailSerializer


class QuestionnaireSubmissionsAPIView(ListAPIView):
    serializer_class = UserSubmissionSerializer
    filterset_class = UserSubmissionFilter
    pagination_class = IoGTPagination

    def get_queryset(self):
        accessible_page_ids = self.request.user.get_accessible_page_ids
        return UserSubmission.objects.filter(
            page_id=self.kwargs.get(self.lookup_field),
            page_id__in=accessible_page_ids
        ).select_related(
            'user', 'page'
        ).order_by('-submit_time')
