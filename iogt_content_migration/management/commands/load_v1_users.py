import json
from collections import defaultdict
from time import sleep

import psycopg2
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.contrib.contenttypes.models import ContentType
from django.core.management import BaseCommand
from django.core.serializers.json import DjangoJSONEncoder
from django_comments.models import CommentFlag
from django_comments_xtd.models import XtdComment
from pip._vendor.distlib.compat import raw_input
from wagtail.contrib.forms.utils import get_field_clean_name

from tqdm import tqdm
from wagtail.core.models import Page, PageViewRestriction

from comments.models import CannedResponse
from home.models import Article, V1ToV2ObjectMap
from questionnaires.models import Survey, UserSubmission, Poll


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

        parser.add_argument(
            '--group-ids',
            nargs='+',
            type=int,
            help='Groups IDs to mark registration survey mandatory for'
        )

    def handle(self, *args, **options):
        self.db_connect(options)

        mandatory_survey_group_ids = options.get('group_ids')

        self.registration_survey_mandatory_group_ids = mandatory_survey_group_ids or \
                                                       self.request_registration_survey_mandatory_groups()
        self.content_type_map = dict()
        self.delete_users = options.get('delete_users')
        self.post_migration_report_messages = defaultdict(list)

        self.clear()

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

    def get_query_results_count(self, sql):
        sql = f'select count(*) from ({sql}) as count_table'
        cur = self.db_query(sql).fetchone()
        return cur['count']

    def with_progress(self, sql, iterable, title):
        self.stdout.write(title)
        return tqdm(iterable, total=self.get_query_results_count(sql))

    def request_registration_survey_mandatory_groups(self):
        sql = f'select * from auth_group'
        cur = self.db_query(sql)

        self.stdout.write('==============================')
        self.stdout.write('User Groups in v1:')
        [self.stdout.write(f'{group["id"]} - {group["name"]}') for group in cur]

        self.stdout.write('\n Please mention the groups for which you want to mark the registration survey'
                          'mandatory?')
        group_ids = raw_input('(Use comma separated ids, leave blank to make it optional)')

        if group_ids:
            group_ids = group_ids.split(',')
            self.stdout.write(f'\n The script will mark registration survey mandatory for all'
                              f' users of group_ids: {group_ids}')
        else:
            self.stdout.write(f'\n The script will mark registration survey optional for all users')
            group_ids = []

        sleep(5)
        return group_ids

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

        self.migrate_user_groups()
        self.migrate_user_accounts()
        self.mark_user_registration_survey_required()

        self.migrate_user_comments()
        self.migrate_comment_flags()
        self.migrate_canned_responses()

        self.migrate_user_survey_submissions()
        self.migrate_user_poll_submissions()
        self.migrate_user_freetext_poll_submissions()

        self.migrate_page_view_restrictions()

        self.print_post_migration_report()

    def populate_content_type_map(self):
        sql = f'select * from django_content_type'
        cur = self.db_query(sql)

        for row in cur:
            new_content_type = ContentType.objects.filter(model=row["model"]).first()
            if not new_content_type:
                self.stdout.write(self.style.ERROR(f'Content Type missing for {row["model"]}'))
            self.content_type_map.update({
                row["model"]: new_content_type
            })

        self.content_type_map.update({
            'articlepage': ContentType.objects.filter(app_label='home', model='article').first()
        })

        cur.close()

    def migrate_user_accounts(self):
        sql = f'select lower(username), count(*) from auth_user group by lower(username) having count(*) > 1'
        cur = self.db_query(sql)

        colliding_usernames = [row['lower'] for row in cur]
        self.post_migration_report_messages['colliding_users_in_v1'].append(','.join(colliding_usernames))

        sql = f'select lower(alias), count(*) ' \
              f'from profiles_userprofile ' \
              f'where alias is not null ' \
              f'group by lower(alias) ' \
              f'having count(*) > 1'
        cur = self.db_query(sql)

        colliding_display_names = [row['lower'] for row in cur]
        self.post_migration_report_messages['colliding_display_names_in_v1'].append(','.join(colliding_display_names))

        sql = f'select * ' \
              f'from auth_user au, profiles_userprofile pup ' \
              f'where au.id = pup.user_id'
        cur = self.db_query(sql)

        renamed_users = []
        for row in self.with_progress(sql, cur, 'User Migration in progress'):
            v1_user_id = row.pop('id')

            user_data = {
                'password': row['password'],
                'last_login': row['last_login'],
                'is_superuser': row['is_superuser'],
                'username': row['username'],
                'first_name': row['first_name'],
                'last_name': row['last_name'],
                'email': row['email'],
                'is_staff': row['is_staff'],
                'is_active': row['is_active'],
                'date_joined': row['date_joined'],
                'display_name': row['alias'] or row['username'],
                'has_filled_registration_survey': True,
            }

            migrated_user = V1ToV2ObjectMap.get_v2_obj(get_user_model(), v1_user_id)

            if not migrated_user:
                if get_user_model().objects.filter(username=row['username']).exists():
                    existing_user = get_user_model().objects.get(username=row['username'])
                    modified_username = f'{existing_user}_v2'
                    renamed_users.append(f'{existing_user} -> {modified_username}')
                    existing_user.username = modified_username
                    existing_user.save()

                user = get_user_model().objects.create(**user_data)
                V1ToV2ObjectMap.create_map(user, v1_user_id)

                user_groups_sql = f'select * from auth_user_groups aug ' \
                                  f'inner join auth_group ag on aug.group_id = ag.id ' \
                                  f'where user_id={v1_user_id}'

                user_groups_cursor = self.db_query(user_groups_sql)

                user.groups.clear()
                for row_ in user_groups_cursor:
                    group = Group.objects.get(name=row_['name'])
                    group.user_set.add(user)

                user_groups_cursor.close()

        if renamed_users:
            self.post_migration_report_messages['renamed_users'].append(','.join(renamed_users))

    def migrate_user_groups(self):
        self.stdout.write(self.style.SUCCESS('Starting User Groups Migration'))

        sql = f'select * from auth_group'
        cur = self.db_query(sql)

        for row in cur:
            group, __ = Group.objects.get_or_create(name=row['name'])
            V1ToV2ObjectMap.create_map(group, row['id'])

        self.stdout.write(self.style.SUCCESS('Completed User Groups Migration'))

    def mark_user_registration_survey_required(self):
        users = get_user_model().objects.filter(groups__id__in=self.registration_survey_mandatory_group_ids)
        users.update(has_filled_registration_survey=False)

    def migrate_root_level_user_comments(self):
        sql = f'select dc.id as comment_id, wcp.id as wagtailpage_id, wcp.title, comment, * ' \
              f'from django_comments dc ' \
              f'inner join commenting_molocomment mc on dc.id = mc.comment_ptr_id ' \
              f'inner join wagtailcore_page wcp on CAST (dc.object_pk as int) = wcp.id ' \
              f'inner join django_content_type dct on dc.content_type_id = dct.id where parent_id is null ' \
              f'order by submit_date'
        cur = self.db_query(sql)

        for row in self.with_progress(sql, cur, 'User [root] comments migration in progress'):
            comment_id = row.pop('comment_id')
            content_type = self.content_type_map[row['model']]

            if not content_type:
                self.stdout.write(self.style.ERROR(f'Content Type for {row["model"]} not found.'))
                continue

            new_article = V1ToV2ObjectMap.get_v2_obj(Article, row['object_pk'])

            if not new_article:
                self.stdout.write(self.style.ERROR(f'New Article for object_pk:{row["object_pk"]} not found.'))
                continue

            max_thread_id_comment = XtdComment.objects.filter(
                content_type_id=content_type.id, object_pk=new_article.pk).order_by('-thread_id').first()

            max_thread_id = 0
            if max_thread_id_comment:
                max_thread_id = max_thread_id_comment.id

            migrated_comment = V1ToV2ObjectMap.get_v2_obj(XtdComment, comment_id)

            if not migrated_comment:
                comment = XtdComment.objects.create(
                    content_type_id=content_type.id, object_pk=new_article.pk, user_name=row['user_name'],
                    user_email=row['user_email'], submit_date=row['submit_date'],
                    comment=row['comment'], is_public=row['is_public'], is_removed=row['is_removed'],
                    thread_id=max_thread_id + 1, user=V1ToV2ObjectMap.get_v2_obj(get_user_model(), row['user_id']),
                    order=1, followup=0, nested_count=0, ip_address=row['ip_address'], site_id=1)
                V1ToV2ObjectMap.create_map(comment, comment_id)

    def migrate_nested_user_comments(self):
        sql = f'select dc.id as comment_id, wcp.id as wagtailpage_id, wcp.title, comment, * ' \
              f'from django_comments dc ' \
              f'inner join commenting_molocomment mc on dc.id = mc.comment_ptr_id ' \
              f'inner join wagtailcore_page wcp on CAST (dc.object_pk as int) = wcp.id ' \
              f'inner join django_content_type dct on dc.content_type_id = dct.id where parent_id is not null ' \
              f'order by submit_date'
        cur = self.db_query(sql)

        for row in self.with_progress(sql, cur, 'User [nested] comments migration in progress...'):
            comment_id = row.pop('comment_id')
            content_type = self.content_type_map[row['model']]

            if not content_type:
                self.stdout.write(self.style.ERROR(f'Content Type for {row["model"]} not found.'))
                continue

            parent_comment = V1ToV2ObjectMap.get_v2_obj(XtdComment, row['parent_id'])

            if not parent_comment:
                self.stdout.write(self.style.ERROR(f'Parent comment for Comment ID:{comment_id} not found in V2'))

            migrated_comment = V1ToV2ObjectMap.get_v2_obj(XtdComment, comment_id)

            if not migrated_comment:
                max_order_value = XtdComment.objects.filter(thread_id=parent_comment.thread_id) \
                    .values_list('order', flat=True).first()
                comment = XtdComment.objects.create(
                    content_type_id=content_type.id, object_pk=parent_comment.object_pk, user_name=row['user_name'],
                    user_email=row['user_email'], submit_date=row['submit_date'],
                    comment=row['comment'], is_public=row['is_public'], is_removed=row['is_removed'],
                    thread_id=parent_comment.thread_id,
                    user=V1ToV2ObjectMap.get_v2_obj(get_user_model(), row['user_id']),
                    level=parent_comment.level + 1, order=max_order_value + 1, followup=0, nested_count=0,
                    ip_address=row['ip_address'],
                    parent_id=parent_comment.pk,
                    site_id=1)
                V1ToV2ObjectMap.create_map(comment, comment_id)

    def migrate_user_comments(self):
        self.migrate_root_level_user_comments()
        self.migrate_nested_user_comments()

    def migrate_comment_flags(self):
        sql = f'select * from django_comment_flags'
        cur = self.db_query(sql)

        for row in cur:
            migrated_comment = V1ToV2ObjectMap.get_v2_obj(XtdComment, row['comment_id'])
            migrated_user = V1ToV2ObjectMap.get_v2_obj(get_user_model(), row['user_id'])

            migrated_comment_flag = V1ToV2ObjectMap.get_v2_obj(CommentFlag, row['id'])

            if not migrated_comment_flag:
                comment_flag = CommentFlag.objects.create(
                    flag=row['flag'], flag_date=row['flag_date'], comment_id=migrated_comment.id,
                    user_id=migrated_user.id)
                V1ToV2ObjectMap.create_map(comment_flag, row['id'])

    def migrate_canned_responses(self):
        sql = f'select * from commenting_cannedresponse'
        cur = self.db_query(sql)

        for row in cur:
            migrated_canned_response = V1ToV2ObjectMap.get_v2_obj(CannedResponse, row['id'])
            if not migrated_canned_response:
                canned_response = CannedResponse.objects.create(header=row['response_header'], text=row['response'])
                V1ToV2ObjectMap.create_map(canned_response, row['id'])

    def migrate_user_survey_submissions(self):
        sql = 'select * from surveys_molosurveysubmission mss ' \
              'inner join surveys_molosurveypage msp on mss.page_id = msp.page_ptr_id'
        cur = self.db_query(sql)

        for row in self.with_progress(sql, cur, 'User Survey migration in progress...'):
            try:
                new_survey = V1ToV2ObjectMap.get_v2_obj(Survey, row['page_id'])
                new_survey_page = Page.objects.get(pk=new_survey.id)
            except (KeyError, AttributeError):
                self.stdout.write(self.style.ERROR(f'Skipping Page: {row["page_id"]}'))
                continue

            form_data = json.loads(row['form_data'])
            altered_form_data = dict()

            for key, value in form_data.items():
                new_key = key.replace('-', '_')
                altered_form_data.update({
                    new_key: value
                })

            migrated_submission = V1ToV2ObjectMap.get_v2_obj(UserSubmission, row['id'], extra='survey')

            if not migrated_submission:
                submission = UserSubmission.objects.create(
                    form_data=json.dumps(altered_form_data, cls=DjangoJSONEncoder),
                    page=new_survey_page,
                    user=V1ToV2ObjectMap.get_v2_obj(get_user_model(), row['user_id']) if row['user_id'] else None,
                )
                submission.submit_time = row['created_at']
                submission.save()
                V1ToV2ObjectMap.create_map(submission, row['id'], extra='survey')

    def migrate_user_poll_submissions(self):
        sql = 'select  pcv.user_id, pcv.question_id, wcp_question.title, wcp_question.id, wcp_question.path \
                from polls_choice pc \
                    inner join wagtailcore_page wcp on pc.page_ptr_id = wcp.id \
                inner join polls_choice_choice_votes pccv on pc.page_ptr_id = pccv.choice_id \
                inner join polls_choicevote pcv on pccv.choicevote_id = pcv.id \
                right outer join wagtailcore_page wcp_question on pcv.question_id = wcp_question.id \
                where pcv.question_id is not null \
                group by pcv.user_id, pcv.question_id, wcp_question.title, wcp_question.id,  wcp_question.path'
        cur = self.db_query(sql)

        for unique_submission in self.with_progress(sql, cur, 'User poll submissions migration in progress'):
            question_id = unique_submission['question_id']
            user_id = unique_submission['user_id']
            title = unique_submission['title']
            page_id = unique_submission['id']

            user_submissions_sql = f'select wcp.id as id, wcp.title as answer_title, pccv.choicevote_id, pcv.*, wcp_question.title \
                                    from polls_choice pc \
                                        inner join wagtailcore_page wcp on pc.page_ptr_id = wcp.id \
                                    inner join polls_choice_choice_votes pccv on pc.page_ptr_id = pccv.choice_id \
                                    inner join polls_choicevote pcv on pccv.choicevote_id = pcv.id \
                                    right outer join wagtailcore_page wcp_question on pcv.question_id = wcp_question.id \
                                    where pcv.question_id is not null and pcv.question_id={question_id} and ' \
                                   f'pcv.user_id={user_id}'
            cursor = self.db_query(user_submissions_sql)

            v2_poll = V1ToV2ObjectMap.get_v2_obj(Poll, page_id)
            v2_poll_page = Page.objects.get(pk=v2_poll.page_ptr_id)

            answers = []
            for row in cursor:
                answers.append(row['answer_title'])

            form_title = get_field_clean_name(title)
            form_data = {
                form_title: answers
            }

            migrated_submission = V1ToV2ObjectMap.get_v2_obj(UserSubmission, row['id'], extra='poll')

            if not migrated_submission:
                submission = UserSubmission.objects.create(
                    form_data=json.dumps(form_data, cls=DjangoJSONEncoder),
                    page=v2_poll_page,
                    user=V1ToV2ObjectMap.get_v2_obj(get_user_model(), row['user_id']) if row['user_id'] else None,
                )
                submission.submit_time = row['submission_date']
                submission.save()
                V1ToV2ObjectMap.create_map(submission, row['id'], extra='poll')

    def migrate_user_freetext_poll_submissions(self):
        sql = f'select wcp.id, wcp.title, pftv.answer, pftv.id as submission_id, pftv.user_id, pftv.submission_date ' \
              f'from polls_freetextquestion pftq ' \
              f'inner join wagtailcore_page wcp on pftq.question_ptr_id = wcp.id ' \
              f'inner join polls_freetextvote pftv on pftv.question_id = wcp.id'

        cur = self.db_query(sql)

        for freetext_submission in self.with_progress(sql, cur, 'User freetext poll submissions migration in progress'):
            title = freetext_submission['title']
            answer = freetext_submission['answer']
            submission_id = freetext_submission['submission_id']

            form_title = get_field_clean_name(title)
            form_data = {
                form_title: answer
            }

            migrated_submission = V1ToV2ObjectMap.get_v2_obj(UserSubmission, freetext_submission['id'],
                                                             extra='freetext_poll')

            v2_poll = V1ToV2ObjectMap.get_v2_obj(Poll, freetext_submission['id'])
            v2_poll_page = Page.objects.get(pk=v2_poll.id)

            if not migrated_submission:
                submission = UserSubmission.objects.create(
                    form_data=json.dumps(form_data, cls=DjangoJSONEncoder),
                    page=v2_poll_page,
                    user=V1ToV2ObjectMap.get_v2_obj(get_user_model(), freetext_submission['user_id']) if
                    freetext_submission['user_id'] else None
                )
                submission.submit_time = freetext_submission['submission_date']
                submission.save()
                V1ToV2ObjectMap.create_map(submission, submission_id, extra='freetext_poll')

    def migrate_page_view_restrictions(self):
        sql = f'select * from wagtailcore_pageviewrestriction'
        cur = self.db_query(sql)

        for row in self.with_progress(sql, cur, 'User Page View Restrictions migration in progress'):
            if not V1ToV2ObjectMap.get_v2_obj(PageViewRestriction, row['id']):
                for klass in [Page, Article, Survey, Poll]:
                    migrated_page = V1ToV2ObjectMap.get_v2_obj(klass, row['page_id'])
                    if migrated_page:
                        break

                pvr = PageViewRestriction.objects.create(
                    page=migrated_page, restriction_type=row['restriction_type'], password=row['password'])
                V1ToV2ObjectMap.create_map(pvr, row['id'])

                pvr_groups_sql = f'select * from wagtailcore_pageviewrestriction_groups ' \
                                 f'where pageviewrestriction_id={row["id"]}'
                pvr_groups_cur = self.db_query(pvr_groups_sql)

                for pvr_group in pvr_groups_cur:
                    migrated_group = V1ToV2ObjectMap.get_v2_obj(Group, pvr_group['group_id'])
                    PageViewRestriction.groups.add(migrated_group)

    def print_post_migration_report(self):
        self.stdout.write(self.style.ERROR('====================='))
        self.stdout.write(self.style.ERROR('POST MIGRATION REPORT'))
        self.stdout.write(self.style.ERROR('====================='))

        for k, v in self.post_migration_report_messages.items():
            self.stdout.write(self.style.ERROR(f"===> {k.replace('_', ' ').upper()}"))
            self.stdout.write(self.style.ERROR('\n'.join(v)))
