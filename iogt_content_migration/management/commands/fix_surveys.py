import json

from django.core.management.base import BaseCommand
from questionnaires.models import Survey, SurveyFormField
from wagtail.models import PageRevision


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument(
            "--fix",
            action="store_true",
            help="Fix problems identified by the report",
        )

    def handle(self, *args, **options):
        if problems_report := report():
            for entry in problems_report:
                self.stdout.write(str(entry))
        else:
            self.stdout.write("No problems found")

        if options.get("fix"):
            self.stdout.write("Fix application started")
            fix(problems_report)
            self.stdout.write("Fix application completed")


class ReportEntry:
    def __init__(self, survey):
        self.survey = survey
        self.problems = report_on_revision(survey)

    @property
    def id(self):
        return self.survey.id

    @property
    def has_problems(self):
        return len(self.problems) > 0

    def __str__(self):
        status = "live " if self.survey.live else "draft"
        return f'{status}, {self.survey.id}, "{self.survey.title}", {self.problems}'


class SurveyRevision:
    def __init__(self, revision):
        self.revision = revision
        self.content = json.loads(revision.content_json)

    @property
    def pk(self):
        return self.content.get("pk")

    @property
    def fields(self):
        return [
            SurveyRevisionField(field)
            for field in self.content.get("survey_form_fields", [])
        ]


class SurveyRevisionField:
    def __init__(self, field):
        self._raw = field

    @property
    def pk(self):
        return self._raw.get("pk")

    @property
    def label(self):
        return self._raw.get("label")


def report():
    return [
        entry
        for survey in Survey.objects.all()
        if (entry := ReportEntry(survey)).has_problems
    ]


def report_on_revision(survey):
    try:
        return identify_problems(survey, get_latest_revision(survey))
    except PageRevision.DoesNotExist:
        return {}


def get_latest_revision(page):
    return SurveyRevision(PageRevision.objects.filter(page=page).latest("created_at"))


def identify_problems(survey, revision):
    return {
        problem
        for p in [
            field_ids_mismatch,
            id_mismatch,
            labels_mismatch,
            no_questions,
            no_revision_questions,
        ]
        if (problem := p(survey, revision))
    }


def no_questions(survey, revision):
    return "no_qs" if len(survey.get_form_fields()) < 1 else None


def no_revision_questions(survey, revision):
    return "no_rev_qs" if len(revision.fields) < 1 else None


def id_mismatch(survey, revision):
    return "id" if revision.pk != survey.id else None


def field_ids_mismatch(survey, revision):
    survey_field_ids = {field.id for field in survey.get_form_fields()}
    revision_field_ids = {field.pk for field in revision.fields if field.pk}

    return "field_ids" if survey_field_ids != revision_field_ids else None


def labels_mismatch(survey, revision):
    survey_field_labels = {field.label for field in survey.get_form_fields()}
    revision_field_labels = {field.label for field in revision.fields if field.label}

    return "labels" if survey_field_labels != revision_field_labels else None


def fix(problems_report):
    for entry in problems_report:
        if {"id", "field_ids"}.issubset(entry.problems):
            print(f"Revision update required, survey={entry.survey}")
            entry.survey.save_revision(log_action=True)
        elif "no_qs" in entry.problems:
            print(
                f"Restore fields from previous revision required, survey={entry.survey}"
            )
            for field in find_first_restorable_revision(entry.survey).fields:
                create_field(entry.survey, field._raw).save()
            latest_revision = entry.survey.save_revision(log_action=True)
            latest_revision.publish()
        else:
            print(f"No action taken, survey={entry.survey}")


def find_first_restorable_revision(page):
    return next(
        sr
        for revision in PageRevision.objects.filter(page=page).order_by("-created_at")
        if is_restorable_v1(((sr := SurveyRevision(revision))), page)
    )


def is_restorable_v1(revision, page):
    """Identifies a v1 PageRevision that can be used to restore a v2 Survey.
    PageRevisions from v1 reference primary keys that do not match the v2 database
    because revisions were copied verbatim from v1. It is possible, though unlikely
    that the primary keys might be the same across v1 and v2. The alternative would be
    to read the surveys directly from the v1 database. This method was chosen for the
    sake of convenience.
    """
    return revision.pk != page.id and len(revision.fields) > 0


def create_field(survey, data):
    return SurveyFormField(
        admin_label=data.get("admin_label"),
        choices="|".join(
            choice.strip() for choice in data.get("choices", "").split(",")
        ),
        default_value=data.get("default_value"),
        field_type=(
            "positivenumber"
            if (ftype := data.get("field_type")) == "positive_number"
            else ftype
        ),
        help_text=data.get("help_text"),
        label=data.get("label"),
        page=survey,
        page_break=data.get("page_break"),
        required=data.get("required"),
        skip_logic=[
            create_answer_option(item)
            for item in json.loads(data.get("skip_logic", "[]"))
        ],
        sort_order=data.get("sort_order"),
    )


def create_answer_option(item):
    value = item.get("value", {})

    return (
        "skip_logic",
        {
            "choice": value.get("choice"),
            "skip_logic": value.get("skip_logic"),
            "question": value.get("question"),
        },
    )
