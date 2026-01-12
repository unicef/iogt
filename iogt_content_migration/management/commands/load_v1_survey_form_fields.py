from collections import defaultdict

from django.contrib.contenttypes.models import ContentType
from django.core.management.base import BaseCommand
import psycopg2
import psycopg2.extras
import json

from home.models import V1ToV2ObjectMap
from questionnaires.models import Survey, SurveyFormField


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument(
            '--host',
            default='0.0.0.0',
            help='IoGT V1 database host'
        )
        parser.add_argument(
            '--port',
            default='5432',
            help='IoGT V1 database port'
        )
        parser.add_argument(
            '--name',
            default='postgres',
            help='IoGT V1 database name'
        )
        parser.add_argument(
            '--user',
            default='postgres',
            help='IoGT V1 database user'
        )
        parser.add_argument(
            '--password',
            default='',
            help='IoGT V1 database password'
        )
        parser.add_argument(
            '--v2-survey-ids',
            nargs='+',
            required=True,
            help='IoGT V2 survey ids, --v2-survey-ids 1 2'
        )

    def handle(self, *args, **options):
        self.db_connect(options)
        self.v2_survey_ids = map(int, options.get('v2_survey_ids'))
        self.post_migration_report_messages = defaultdict(list)

        for v2_survey_id in self.v2_survey_ids:
            self.migrate_survey(v2_survey_id)
        self.print_post_migration_report()

    def db_connect(self, options):
        connection_string = self.create_connection_string(options)
        self.stdout.write(f'DB connection string created, string={connection_string}')
        self.v1_conn = psycopg2.connect(connection_string)
        self.stdout.write('Connected to v1 DB')

    def __del__(self):
        try:
            self.v1_conn.close()
            self.stdout.write('Closed connection to v1 DB')
        except AttributeError:
            pass

    def create_connection_string(self, options):
        host = options.get('host', '0.0.0.0')
        port = options.get('port', '5432')
        name = options.get('name', 'postgres')
        user = options.get('user', 'postgres')
        password = options.get('password', '')
        return f"host={host} port={port} dbname={name} user={user} password={password}"

    def db_query(self, q):
        cur = self.v1_conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        cur.execute(q)
        return cur

    def migrate_survey(self, page_id):
        try:
            survey = Survey.objects.get(id=page_id)
        except:
            self.stdout.write(f"Survey doesn't exist, id={page_id}")
        else:
            content_type = ContentType.objects.get_for_model(Survey)
            v1_survey_id = V1ToV2ObjectMap.objects.get(content_type=content_type, object_id=page_id).v1_object_id
            self.migrate_survey_questions(survey, v1_survey_id)
            self.stdout.write(f"Migrated survey form fields, title={survey.title}")

    def migrate_survey_questions(self, survey, v1_survey_id):
        self._migrate_survey_questions(survey, v1_survey_id, 'surveys_molosurveyformfield')
        self._migrate_survey_questions(survey, v1_survey_id, 'surveys_personalisablesurveyformfield')

    def _migrate_survey_questions(self, survey, v1_survey_id, formfield_table):
        sql = f'select *, smsff.id as smsffid ' \
              f'from {formfield_table} smsff, surveys_molosurveypage smsp, wagtailcore_page wcp, core_languagerelation clr, core_sitelanguage csl ' \
              f'where smsff.page_id = smsp.page_ptr_id ' \
              f'and smsp.page_ptr_id = wcp.id ' \
              f'and wcp.id = clr.page_id ' \
              f'and clr.language_id = csl.id ' \
              f'and wcp.id = {v1_survey_id} ' \
              f'order by wcp.path'
        cur = self.db_query(sql)
        self.create_survey_question(survey, cur)
        cur.close()

    def create_survey_question(self, survey, cur):
        for row in cur:
            field_type = 'positivenumber' if row['field_type'] == 'positive_number' else row['field_type']
            if row['skip_logic']:
                skip_logics = json.loads(row['skip_logic'])
                for skip_logic in skip_logics:
                    skip_logic.get('value', {}).pop('survey')
                row['skip_logic'] = json.dumps(skip_logics)

            content_type = ContentType.objects.get_for_model(SurveyFormField)
            try:
                object_map = V1ToV2ObjectMap.objects.get(content_type=content_type, v1_object_id=row['smsffid'])
            except:
                self.stdout.write(f"Survey form field doesn't exist, title={survey.title}, id={survey.id}, form_field_id={row['smsffid']}")
            else:
                if not SurveyFormField.objects.filter(id=object_map.object_id).exists():
                        survey_form_field = SurveyFormField.objects.create(
                            page=survey, sort_order=row['sort_order'], label=row['label'], required=row['required'],
                            default_value=row['default_value'], help_text=row['help_text'], field_type=field_type,
                            admin_label=row['admin_label'], page_break=row['page_break'],
                            choices='|'.join(row['choices'].split(',')), skip_logic=row['skip_logic']
                        )

                        object_map.object_id = survey_form_field.id
                        object_map.save(update_fields=["object_id"])
                        skip_logic_next_actions = [logic['value']['skip_logic'] for logic in json.loads(row['skip_logic'])]
                        if not survey.multi_step and (
                                'end' in skip_logic_next_actions or 'question' in skip_logic_next_actions):
                            self.post_migration_report_messages['survey_multistep'].append(
                                f'skip logic without multi step'
                            )
                        self.stdout.write(f"saved survey question, label={row['label']}")

    def print_post_migration_report(self):
        self.stdout.write(self.style.ERROR('====================='))
        self.stdout.write(self.style.ERROR('POST MIGRATION REPORT'))
        self.stdout.write(self.style.ERROR('====================='))

        for k, v in self.post_migration_report_messages.items():
            self.stdout.write(self.style.ERROR(f"===> {k.replace('_', ' ').upper()}"))
            self.stdout.write(self.style.ERROR('\n'.join(v)))
