from pathlib import Path
from django.core.management.base import BaseCommand
from wagtail.core.models import Page, Site, Locale
from django.core.files.images import ImageFile
from wagtail.images.models import Image
from wagtail_localize.models import Translation
from wagtail_localize.views.submit_translations import TranslationCreator

import home.models as models
from questionnaires.models import Poll, PollFormField, Survey, SurveyFormField, Quiz, QuizFormField
import psycopg2
import psycopg2.extras
import json

from questionnaires.models import PollIndexPage, SurveyIndexPage, QuizIndexPage


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
            '--media-dir',
            required=True,
            help='Path to IoGT v1 media directory'
        )
        parser.add_argument(
            '--skip-locales',
            action='store_true',
            help='Skip data of locales other than default language'
        )

    def handle(self, *args, **options):
        self.db_connect(options)
        self.media_dir = options.get('media_dir')
        self.skip_locales = options.get('skip_locales')

        self.image_map = {}
        self.page_translation_map = {}
        self.v1_to_v2_page_map = {}

        self.clear()
        self.stdout.write('Existing site structure cleared')

        root = Page.get_first_root_node()
        self.migrate(root)

    def clear(self):
        PollFormField.objects.all().delete()
        Poll.objects.all().delete()
        SurveyFormField.objects.all().delete()
        Survey.objects.all().delete()
        QuizFormField.objects.all().delete()
        Quiz.objects.all().delete()
        models.FooterPage.objects.all().delete()
        models.FooterIndexPage.objects.all().delete()
        models.BannerPage.objects.all().delete()
        models.BannerIndexPage.objects.all().delete()
        models.Article.objects.all().delete()
        models.Section.objects.all().delete()
        models.SectionIndexPage.objects.all().delete()
        models.HomePage.objects.all().delete()
        Site.objects.all().delete()
        Image.objects.all().delete()

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

    def migrate(self, root):
        self.migrate_images()
        self.load_page_translation_map()
        home = self.create_home_page(root)
        index_pages = self.create_index_pages(home)
        self.migrate_sections(index_pages['section_index_page'])
        self.migrate_articles(index_pages['section_index_page'])
        self.migrate_banners(index_pages['banner_index_page'])
        self.migrate_footers(index_pages['footer_index_page'])
        self.migrate_polls(index_pages['poll_index_page'])
        self.migrate_surveys(index_pages['survey_index_page'])
        self.stop_translations()
        Page.fix_tree()

    def create_home_page(self, root):
        sql = 'select * from core_main main join wagtailcore_page page on main.page_ptr_id = page.id'
        cur = self.db_query(sql)
        main = cur.fetchone()
        cur.close()
        home = None
        if main:
            home = models.HomePage(
                title=main['title'],
                draft_title=main['draft_title'],
                seo_title=main['seo_title'],
                slug=main['slug'],
                live=main['live'],
                latest_revision_created_at=main['latest_revision_created_at'],
                first_published_at=main['first_published_at'],
                last_published_at=main['last_published_at'],
            )
            root.add_child(instance=home)
        else:
            raise Exception('Could not find a main page in v1 DB')
        cur.close()

        cur = self.db_query('select * from wagtailcore_site')
        v1_site = cur.fetchone()
        cur.close()
        if v1_site:
            Site.objects.create(
                hostname=v1_site['hostname'],
                port=v1_site['port'],
                root_page=home,
                is_default_site=True,
                site_name=v1_site['site_name'] if v1_site['site_name'] else 'Internet of Good Things',
            )
        else:
            raise Exception('Could not find site in v1 DB')
        return home

    def create_index_pages(self, homepage):
        section_index_page = models.SectionIndexPage(title='Sections')
        homepage.add_child(instance=section_index_page)

        banner_index_page = models.BannerIndexPage(title='Banners')
        homepage.add_child(instance=banner_index_page)

        footer_index_page = models.FooterIndexPage(title='Footers')
        homepage.add_child(instance=footer_index_page)

        poll_index_page = PollIndexPage(title='Polls')
        homepage.add_child(instance=poll_index_page)

        survey_index_page = SurveyIndexPage(title='Survey')
        homepage.add_child(instance=survey_index_page)

        quiz_index_page = QuizIndexPage(title='Quizzes')
        homepage.add_child(instance=quiz_index_page)

        return {
            'section_index_page': section_index_page,
            'banner_index_page': banner_index_page,
            'footer_index_page': footer_index_page,
            'poll_index_page': poll_index_page,
            'survey_index_page': survey_index_page,
            'quiz_index_page': quiz_index_page,
        }

    def migrate_images(self):
        cur = self.db_query('select * from wagtailimages_image')
        content_type = self.find_content_type_id('wagtailimages', 'image')
        for row in cur:
            image_file = self.open_image_file(row['file'])
            if image_file:
                image = Image.objects.create(
                    title=row['title'],
                    file=ImageFile(image_file, name=row['file'].split('/')[-1]),
                    focal_point_x=row['focal_point_x'],
                    focal_point_y=row['focal_point_y'],
                    focal_point_width=row['focal_point_width'],
                    focal_point_height=row['focal_point_height'],
                    # uploaded_by_user='',
                )
                image.get_file_size()
                image.get_file_hash()
                tags = self.find_tags(content_type, row['id'])
                if tags:
                    image.tags.add(*tags)
                self.image_map.update({ row['id']: image })
        cur.close()
        self.stdout.write('Images migrated')

    def find_content_type_id(self, app_label, model):
        cur = self.db_query(f"select id from django_content_type where app_label = '{app_label}' and model = '{model}'")
        content_type = cur.fetchone()
        cur.close()
        return content_type.get('id')

    def open_image_file(self, file):
        file_path = Path(self.media_dir) / file
        try:
            return open(file_path, 'rb')
        except:
            self.stdout.write(f"Image file not found: {file_path}")

    def find_tags(self, content_type, object_id):
        tags_query = 'select t.name from taggit_tag t join taggit_taggeditem ti on t.id = ti.tag_id where ti.content_type_id = {} and ti.object_id = {}'
        cur = self.db_query(tags_query.format(content_type, object_id))
        tags = [tag['name'] for tag in cur]
        cur.close()
        return tags

    def migrate_sections(self, section_index_page):
        sql = "select * " \
              "from core_sectionpage csp, wagtailcore_page wcp, core_languagerelation clr, core_sitelanguage csl " \
              "where csp.page_ptr_id = wcp.id " \
              "and wcp.id = clr.page_id " \
              "and clr.language_id = csl.id "
        if self.skip_locales:
            sql += " and locale = 'en' "
        sql += 'order by wcp.path'
        cur = self.db_query(sql)
        section_page_translations = []
        for row in cur:
            if row['page_ptr_id'] in self.page_translation_map:
                section_page_translations.append(row)
            else:
                self.create_section(section_index_page, row)
        else:
            for row in section_page_translations:
                section = self.v1_to_v2_page_map.get(self.page_translation_map[row['page_ptr_id']])
                locale, __ = Locale.objects.get_or_create(language_code=row['locale'])

                self.translate_page(locale=locale, page=section)

                translated_section = section.get_translation_or_none(locale)
                if translated_section:
                    translated_section.title = row['title']
                    translated_section.draft_title = row['draft_title']
                    translated_section.live = row['live']
                    translated_section.save()

                self.stdout.write(f"Translated section, title={row['title']}")
        cur.close()

    def create_section(self, section_index_page, row):
        section = models.Section(
            title=row['title'],
            draft_title=row['draft_title'],
            show_in_menus=True,
            font_color='1CABE2',
            slug=row['slug'],
            path=section_index_page.path + row['path'][12:],
            depth=row['depth'],
            numchild=row['numchild'],
            live=row['live'],
        )
        section.save()

        self.v1_to_v2_page_map.update({
            row['page_ptr_id']: section
        })
        self.stdout.write(f"saved section, title={section.title}")

    def migrate_articles(self, section_index_page):
        sql = "select * " \
              "from core_articlepage cap, wagtailcore_page wcp, core_languagerelation clr, core_sitelanguage csl " \
              "where cap.page_ptr_id = wcp.id " \
              "and wcp.id = clr.page_id " \
              "and clr.language_id = csl.id "
        if self.skip_locales:
            sql += "and locale = 'en' "
        sql += " and wcp.path like '000100010002%'order by wcp.path"
        cur = self.db_query(sql)

        article_page_translations = []
        for row in cur:
            if row['page_ptr_id'] in self.page_translation_map:
                article_page_translations.append(row)
            else:
                self.create_article(section_index_page, row)
        else:
            for row in article_page_translations:
                article = self.v1_to_v2_page_map.get(self.page_translation_map[row['page_ptr_id']])
                locale, __ = Locale.objects.get_or_create(language_code=row['locale'])

                self.translate_page(locale=locale, page=article)

                translated_article = article.get_translation_or_none(locale)
                if translated_article:
                    translated_article.lead_image = self.image_map.get(row['image_id'])
                    translated_article.title = row['title']
                    translated_article.draft_title = row['draft_title']
                    translated_article.live = row['live']
                    translated_article.body = self.map_article_body(row['body'])
                    translated_article.save()

                self.stdout.write(f"Translated article, title={row['title']}")
        cur.close()

    def create_article(self, section_index_page, row):
        article = models.Article(
            lead_image=self.image_map.get(row['image_id']),
            title=row['title'],
            draft_title=row['draft_title'],
            slug=row['slug'],
            path=section_index_page.path + row['path'][12:],
            depth=row['depth'],
            numchild=row['numchild'],
            live=row['live'],
            body=self.map_article_body(row['body']),
        )
        try:
            article.save()
            self.v1_to_v2_page_map.update({
                row['page_ptr_id']: article
            })
        except Page.DoesNotExist:
            self.stdout.write(f"Skipping page with missing parent: title={row['title']}")
            return
        self.stdout.write(f"saved article, title={article.title}")

    def map_article_body(self, v1_body):
        v2_body = json.loads(v1_body)
        for block in v2_body:
            if block['type'] == 'paragraph':
                block['type'] = 'markdown'
        return json.dumps(v2_body)

    def migrate_banners(self, banner_index_page):
        sql = "select * " \
              "from core_bannerpage cbp, wagtailcore_page wcp, core_languagerelation clr, core_sitelanguage csl " \
              "where cbp.page_ptr_id = wcp.id " \
              "and wcp.id = clr.page_id " \
              "and clr.language_id = csl.id "
        if self.skip_locales:
            sql += " and locale = 'en' "
        sql += ' order by wcp.path'
        cur = self.db_query(sql)
        banner_page_translations = []
        for row in cur:
            if row['page_ptr_id'] in self.page_translation_map:
                banner_page_translations.append(row)
            else:
                self.create_banner(banner_index_page, row)
        else:
            for row in banner_page_translations:
                banner = self.v1_to_v2_page_map.get(self.page_translation_map[row['page_ptr_id']])
                locale, __ = Locale.objects.get_or_create(language_code=row['locale'])

                try:
                    self.translate_page(locale=locale, page=banner)
                except:
                    continue

                translated_banner = banner.get_translation_or_none(locale)
                if translated_banner:
                    translated_banner.banner_image = self.image_map.get(row['banner_id'])
                    translated_banner.banner_link_page = self.v1_to_v2_page_map.get(row['banner_link_page_id'])
                    translated_banner.title = row['title']
                    translated_banner.draft_title = row['draft_title']
                    translated_banner.live = row['live']
                    translated_banner.save()

                self.stdout.write(f"Translated banner, title={row['title']}")
        cur.close()

    def create_banner(self, banner_index_page, row):
        banner = models.BannerPage(
            banner_image=self.image_map.get(row['banner_id']),
            banner_link_page=self.v1_to_v2_page_map.get(row['banner_link_page_id']),
            title=row['title'],
            draft_title=row['draft_title'],
            slug=row['slug'],
            path=banner_index_page.path + row['path'][12:],
            depth=row['depth'],
            numchild=row['numchild'],
            live=row['live'],
            banner_description=''
        )
        banner.save()
        self.v1_to_v2_page_map.update({
            row['page_ptr_id']: banner
        })
        self.stdout.write(f"saved banner, title={banner.title}")

    def migrate_footers(self, footer_index_page):
        sql = "select * " \
              "from core_footerpage cfp, core_articlepage cap, wagtailcore_page wcp, core_languagerelation clr, core_sitelanguage csl " \
              "where cfp.articlepage_ptr_id = cap.page_ptr_id " \
              "and cap.page_ptr_id = wcp.id " \
              "and wcp.id = clr.page_id " \
              "and clr.language_id = csl.id "
        if self.skip_locales:
            sql += " and locale = 'en' "
        sql += ' order by wcp.path'
        cur = self.db_query(sql)
        footer_page_translations = []
        for row in cur:
            if row['page_ptr_id'] in self.page_translation_map:
                footer_page_translations.append(row)
            else:
                self.create_footer(footer_index_page, row)
        else:
            for row in footer_page_translations:
                footer = self.v1_to_v2_page_map.get(self.page_translation_map[row['page_ptr_id']])
                locale, __ = Locale.objects.get_or_create(language_code=row['locale'])

                self.translate_page(locale=locale, page=footer)

                translated_footer = footer.get_translation_or_none(locale)
                if translated_footer:
                    translated_footer.lead_image = self.image_map.get(row['image_id'])
                    translated_footer.title = row['title']
                    translated_footer.draft_title = row['draft_title']
                    translated_footer.live = row['live']
                    translated_footer.body = self.map_article_body(row['body'])
                    translated_footer.save()

                self.stdout.write(f"Translated footer, title={row['title']}")
        cur.close()

    def create_footer(self, footer_index_page, row):
        footer = models.FooterPage(
            lead_image=self.image_map.get(row['image_id']),
            title=row['title'],
            draft_title=row['draft_title'],
            slug=row['slug'],
            path=footer_index_page.path + row['path'][12:],
            depth=row['depth'],
            numchild=row['numchild'],
            live=row['live'],
            body=self.map_article_body(row['body']),
        )
        footer.save()
        self.v1_to_v2_page_map.update({
            row['page_ptr_id']: footer
        })
        self.stdout.write(f"saved footer, title={footer.title}")

    def load_page_translation_map(self):
        sql = "select * " \
              "from core_pagetranslation"
        cur = self.db_query(sql)
        for row in cur:
            self.page_translation_map.update({
                row['translated_page_id']: row['page_id'],
            })
        cur.close()
        self.stdout.write('Page translation map loaded.')

    def translate_page(self, locale, page):
        translator = TranslationCreator(user=None, target_locales=[locale])
        translator.create_translations(page)

    def stop_translations(self):
        Translation.objects.update(enabled=False)

        self.stdout.write('Translations stopped.')

    def migrate_polls(self, poll_index_page):
        sql = "select * " \
              "from polls_question pq, wagtailcore_page wcp, core_languagerelation clr, core_sitelanguage csl " \
              "where pq.page_ptr_id = wcp.id " \
              "and wcp.id = clr.page_id " \
              "and clr.language_id = csl.id "
        if self.skip_locales:
            sql += " and locale = 'en' "
        sql += 'order by wcp.path'
        cur = self.db_query(sql)
        poll_page_translations = []
        for row in cur:
            if row['page_ptr_id'] in self.page_translation_map:
                poll_page_translations.append(row)
            else:
                self.create_poll(poll_index_page, row)
        else:
            for row in poll_page_translations:
                poll = self.v1_to_v2_page_map.get(self.page_translation_map[row['page_ptr_id']])
                locale, __ = Locale.objects.get_or_create(language_code=row['locale'])

                self.translate_page(locale=locale, page=poll)

                translated_poll = poll.get_translation_or_none(locale)
                if translated_poll:
                    translated_poll.title = row['title']
                    translated_poll.draft_title = row['draft_title']
                    translated_poll.live = row['live']
                    translated_poll.result_as_percentage = row['result_as_percentage']
                    translated_poll.save()

                    row['path'] = row['path'][:-4]
                    self.migrate_poll_questions(translated_poll, row)

                self.stdout.write(f"Translated poll, title={row['title']}")
        cur.close()

    def create_poll(self, poll_index_page, row):
        poll = Poll(
            title=row['title'],
            draft_title=row['draft_title'],
            show_in_menus=True,
            slug=row['slug'],
            live=row['live'],
            result_as_percentage=row['result_as_percentage'],
        )
        poll_index_page.add_child(instance=poll)

        self.migrate_poll_questions(poll, row)

        self.v1_to_v2_page_map.update({
            row['page_ptr_id']: poll
        })
        self.stdout.write(f"saved poll, title={poll.title}")

    def migrate_poll_questions(self, poll, poll_row):
        sql = f'select * ' \
              f'from polls_choice pc, wagtailcore_page wcp, core_languagerelation clr, core_sitelanguage csl ' \
              f'where pc.page_ptr_id = wcp.id ' \
              f'and wcp.path like \'{poll_row["path"]}%\' ' \
              f'and wcp.id = clr.page_id ' \
              f'and clr.language_id = csl.id ' \
              f'and csl.locale = \'{poll_row["locale"]}\''
        cur = self.db_query(sql)
        self.create_poll_question(poll, poll_row, cur)
        cur.close()

    def create_poll_question(self, poll, poll_row, cur):
        PollFormField.objects.filter(page=poll).delete()
        choices = []
        for row in cur:
            choices.append(row['title'])

        choices_length = len(choices)

        if choices_length == 2:
            field_type = 'radio'
        elif choices_length > 2:
            if poll_row['allow_multiple_choice']:
                field_type = 'checkboxes'
            else:
                field_type = 'dropdown'
        else:
            self.stdout.write(f'Unable to determine filed type for poll={poll_row["title"]}')
            return

        choices = ','.join(choices)

        PollFormField.objects.create(page=poll, label=poll.title, field_type=field_type, choices=choices)
        self.stdout.write(f"saved poll question, label={poll.title}")

    def migrate_surveys(self, survey_index_page):
        sql = "select * " \
              "from surveys_molosurveypage smsp, wagtailcore_page wcp, core_languagerelation clr, core_sitelanguage csl " \
              "where smsp.page_ptr_id = wcp.id " \
              "and wcp.id = clr.page_id " \
              "and clr.language_id = csl.id "
        if self.skip_locales:
            sql += "and locale = 'en' "
        sql += 'order by wcp.path'
        cur = self.db_query(sql)
        survey_page_translations = []
        for row in cur:
            if row['page_ptr_id'] in self.page_translation_map:
                survey_page_translations.append(row)
            else:
                self.create_survey(survey_index_page, row)
        else:
            for row in survey_page_translations:
                survey = self.v1_to_v2_page_map.get(self.page_translation_map[row['page_ptr_id']])
                locale, __ = Locale.objects.get_or_create(language_code=row['locale'])

                self.translate_page(locale=locale, page=survey)

                translated_survey = survey.get_translation_or_none(locale)
                if translated_survey:
                    translated_survey.title = row['title']
                    translated_survey.draft_title = row['draft_title']
                    translated_survey.live = row['live']
                    translated_survey.description = self.map_survey_description(row['description'])
                    translated_survey.thank_you_text = self.map_survey_thank_you_text(row)
                    translated_survey.allow_anonymous_submissions = row['allow_anonymous_submissions']
                    translated_survey.allow_multiple_submissions = row['allow_multiple_submissions_per_user']
                    translated_survey.submit_button_text = row['submit_text'] or 'Submit'
                    translated_survey.direct_display = row['display_survey_directly']
                    translated_survey.multi_step = row['multi_step']
                    translated_survey.save()

                    self.migrate_survey_questions(translated_survey, row)

                self.stdout.write(f"Translated survey, title={row['title']}")
        cur.close()

    def create_survey(self, survey_index_page, row):
        survey = Survey(
            title=row['title'],
            draft_title=row['draft_title'],
            show_in_menus=True,
            live=row['live'],
            description=self.map_survey_description(row['description']),
            thank_you_text=self.map_survey_thank_you_text(row),
            allow_anonymous_submissions=row['allow_anonymous_submissions'],
            allow_multiple_submissions=row['allow_multiple_submissions_per_user'],
            submit_button_text=row['submit_text'] or 'Submit',
            direct_display=row['display_survey_directly'],
            multi_step=row['multi_step'],
        )
        survey_index_page.add_child(instance=survey)

        self.migrate_survey_questions(survey, row)

        self.v1_to_v2_page_map.update({
            row['page_ptr_id']: survey
        })
        self.stdout.write(f"saved survey, title={survey.title}")

    def map_survey_description(self, v1_survey_description):
        v1_survey_description = json.loads(v1_survey_description)
        v2_survey_description = []
        for block in v1_survey_description:
            if block['type'] in ['paragraph', 'image']:
                v2_survey_description.append(block)
        return json.dumps(v2_survey_description)

    def map_survey_thank_you_text(self, row):
        return json.dumps([
            {'type': 'paragraph', 'value': row['thank_you_text']},
            {'type': 'image', 'value': self.image_map.get(row['image_id'])}
        ])

    def migrate_survey_questions(self, survey, survey_row):
        sql = f'select * ' \
              f'from surveys_molosurveyformfield smsff, surveys_molosurveypage smsp, wagtailcore_page wcp, core_languagerelation clr, core_sitelanguage csl ' \
              f'where smsff.page_id = smsp.page_ptr_id ' \
              f'and smsp.page_ptr_id = wcp.id ' \
              f'and wcp.id = clr.page_id ' \
              f'and clr.language_id = csl.id ' \
              f'and wcp.id = {survey_row["page_ptr_id"]} '
        if self.skip_locales:
            sql += "and locale = 'en' "
        sql += 'order by wcp.path'
        cur = self.db_query(sql)
        self.create_survey_question(survey, survey_row, cur)
        cur.close()

    def create_survey_question(self, survey, survey_row, cur):
        SurveyFormField.objects.filter(page=survey).delete()

        for row in cur:
            SurveyFormField.objects.create(
                page=survey, sort_order=row['sort_order'], label=row['label'], required=row['required'],
                default_value=row['default_value'], help_text=row['help_text'], field_type=row['field_type'],
                admin_label=row['admin_label'], page_break=row['page_break'], choices=row['choices'],
                skip_logic=row['skip_logic']
            )
            self.stdout.write(f"saved survey question, label={row['label']}")
