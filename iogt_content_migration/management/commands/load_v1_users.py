import json

import psycopg2
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import MultipleObjectsReturned
from django.core.management import BaseCommand
from django.core.serializers.json import DjangoJSONEncoder
from django_comments_xtd.models import XtdComment

from home.models import Article, SectionIndexPage
from questionnaires.models import Survey, UserSubmission, SurveyIndexPage


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
            '--skip-locales',
            action='store_true',
            help='Skip data of locales other than default language'
        )

        parser.add_argument(
            '--delete-users',
            action='store_true',
            help='Delete existing Users and their associated data. Use carefully'
        )

    def handle(self, *args, **options):
        self.db_connect(options)
        self.delete_users = options.get('delete_users')

        self.content_type_map = dict()
        self.comments_map = dict()
        self.articles_map = dict()
        self.surveys_map = dict()
        self.users_map = dict()

        self.clear()
        self.stdout.write('Existing site structure cleared')

        self.migrate()

    def clear(self):
        if self.delete_users:
            self.stdout.write('Deleted Existing Users')
            get_user_model().objects.all().delete()

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

    def migrate(self):
        self.populate_content_type_map()
        self.populate_articles_map()
        self.populate_surveys_map()

        self.migrate_user_groups()
        self.migrate_user_accounts()
        self.populate_users_map()

        self.migrate_user_comments()
        self.migrate_user_submissions()

    def get_mapping_from_title(self, klass, title):
        return klass.objects.get(title=title)

    def get_mapping_from_path(self, klass, path, title):
        section_index_pages = SectionIndexPage.objects.all()
        survey_index_pages = SurveyIndexPage.objects.all()
        all_parents = list(section_index_pages) + list(survey_index_pages)

        possible_paths = [f'{parent.path}{path}' for parent in all_parents]

        return klass.objects.filter(title=title, path__in=possible_paths).first()

    def populate_surveys_map(self):
        sql = f'select * from surveys_molosurveypage msp inner join wagtailcore_page wp on msp.page_ptr_id = wp.id'
        cur = self.db_query(sql)

        for row in cur:
            try:
                survey = self.get_mapping_from_title(Survey, row['title'])
            except MultipleObjectsReturned:
                survey = self.get_mapping_from_path(Survey, row['path'][12:], row['title'])

            if survey:
                self.surveys_map.update({
                    row['id']: survey
                })
                print(f'SURVEY | ({row["id"]}) {row["title"]} -> ({survey.page_ptr_id}) {survey.title}')
            else:
                self.stdout.write(self.style.ERROR(f'Found no match for ({row["id"]}) - {row["title"]}'))

        cur.close()

    def populate_users_map(self):
        sql = 'select * from auth_user'
        cur = self.db_query(sql)

        for row in cur:
            self.users_map.update({
                row["id"]: get_user_model().objects.get(username=row['username'])
            })

        cur.close()

    def populate_articles_map(self):
        sql = f'select * from core_articlepage cap inner join wagtailcore_page wp on cap.page_ptr_id = wp.id'
        cur = self.db_query(sql)

        for row in cur:
            partial_path = row['path'][12:]
            section_index_pages = SectionIndexPage.objects.all()

            for sip in section_index_pages:
                new_path = f'{sip.path}{partial_path}'

                article = Article.objects.filter(path=new_path).first()
                if article:
                    self.articles_map.update({
                        str(row['id']): article
                    })
                    print(f'ARTICLE | ({row["id"]}) {row["title"]} -> ({article.page_ptr_id}) {article.title}')

    def populate_content_type_map(self):
        sql = f'select * from django_content_type'
        cur = self.db_query(sql)

        for row in cur:
            new_content_type = ContentType.objects.filter(model=row["model"]).first()
            if not new_content_type:
                self.stdout.write(self.style.ERROR(f'Content Type missing for {row["model"]}'))
            print(f'Old {row["model"]} -> New {new_content_type}')
            self.content_type_map.update({
                row["model"]: new_content_type
            })

        self.content_type_map.update({
            'articlepage': ContentType.objects.filter(app_label='home', model='article').first()
        })

        cur.close()

    def migrate_user_accounts(self):
        self.stdout.write(self.style.SUCCESS('Starting User Migration'))

        sql = f'select * from auth_user'
        cur = self.db_query(sql)

        for row in cur:
            v1_user_id = row.pop('id')

            user = get_user_model().objects.filter(username=row['username']).first()
            if not user:
                user = get_user_model().objects.create(**row)

            user_groups_sql = f'select * from auth_user_groups aug ' \
                              f'inner join auth_group ag on aug.group_id = ag.id ' \
                              f'where user_id={v1_user_id}'

            user_groups_cursor = self.db_query(user_groups_sql)

            user.groups.through.objects.all().delete()
            for row_ in user_groups_cursor:
                group = Group.objects.get(name=row_['name'])
                user.groups.add(group)

            user_groups_cursor.close()

        self.stdout.write(self.style.SUCCESS('Completed User Migration'))

    def migrate_user_groups(self):
        self.stdout.write(self.style.SUCCESS('Starting User Groups Migration'))

        sql = f'select * from auth_group'
        cur = self.db_query(sql)

        for row in cur:
            Group.objects.get_or_create(name=row['name'])

        self.stdout.write(self.style.SUCCESS('Completed User Groups Migration'))

    def migrate_user_comments(self):
        self.stdout.write(self.style.SUCCESS('Starting Comment migration'))

        sql = f'select * from django_comments dc inner join django_content_type dct on dc.content_type_id = dct.id'
        cur = self.db_query(sql)

        for row in cur:
            row.pop('id')
            content_type = self.content_type_map[row['model']]

            if not content_type:
                self.stdout.write(self.style.ERROR(f'Content Type for {row["model"]} not found.'))
                continue

            try:
                new_article = self.articles_map[row["object_pk"]]
            except KeyError:
                new_article

            max_thread_id_comment = XtdComment.objects.filter(
                content_type_id=content_type.id, object_pk=new_article.pk).order_by('-thread_id').first()

            max_thread_id = 0
            if max_thread_id_comment:
                max_thread_id = max_thread_id_comment.id

            XtdComment.objects.create(
                content_type_id=content_type.id, object_pk=new_article.pk, user_name=row['user_name'],
                user_email=row['user_email'], submit_date=row['submit_date'],
                comment=row['comment'], is_public=True, is_removed=False, thread_id=max_thread_id + 1,
                user=self.users_map[row['user_id']], order=1, followup=0, nested_count=0, site_id=1)

        self.stdout.write(self.style.SUCCESS('Completing Comment migration'))

    def migrate_user_submissions(self):
        self.stdout.write(self.style.SUCCESS('Started Survey Migration'))

        sql = 'select * from surveys_molosurveysubmission mss ' \
              'inner join surveys_molosurveypage msp on mss.page_id = msp.page_ptr_id'
        cur = self.db_query(sql)

        for row in cur:
            try:
                new_survey = self.surveys_map[row['page_id']]
            except KeyError:
                self.stdout.write(self.style.ERROR(f'Skipping Page: {row["page_id"]}'))
                continue

            form_data = json.loads(row['form_data'])
            altered_form_data = dict()

            for key, value in form_data.items():
                new_key = key.replace('-', '_')
                altered_form_data.update({
                    new_key: value
                })

            UserSubmission.objects.create(
                form_data=json.dumps(altered_form_data, cls=DjangoJSONEncoder),
                page=new_survey,
                user=self.users_map[row['user_id']] if row['user_id'] else None,
            )

        self.stdout.write(self.style.SUCCESS('Completed Survey Migration'))
