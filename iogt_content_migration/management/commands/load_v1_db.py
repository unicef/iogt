from collections import defaultdict
from pathlib import Path

import csv
from bs4 import BeautifulSoup
from django.conf import settings
from django.core.files import File
from django.core.management.base import BaseCommand
from django.urls import reverse
from wagtail.core.models import Page, Site, Locale, Collection, PageRevision
from django.core.files.images import ImageFile
from wagtail.documents.models import Document
from wagtail.images.models import Image
from wagtail_localize.models import Translation
from wagtail_localize.views.submit_translations import TranslationCreator
from wagtailmarkdown.utils import _get_bleach_kwargs
from wagtailmedia.models import Media
from wagtailsvg.models import Svg

import home.models as models
from comments.models import CommentStatus
from home.models import V1ToV2ObjectMap, V1PageURLToV2PageMap
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
            help='**RELATIVE Path** to IoGT v1 media directory'
        )
        parser.add_argument(
            '--delete-users',
            action='store_true',
            help='Delete existing Users and their associated data. Use carefully'
        )
        parser.add_argument(
            '--v1-domains',
            nargs="+",
            required=True,
            help="IoGT V1 domains for manually inserted internal links, --v1-domains domain1 domain2 ..."
        )
        parser.add_argument(
            '--sort',
            required=True,
            help='Sort page by "type1" or "type2"'
        )

    def handle(self, *args, **options):
        self.db_connect(options)
        self.media_dir = options.get('media_dir')
        self.v1_domains_list = options.get('v1_domains')
        self.sort = options.get('sort')
        self.v2_domain = options.get('v2_domain')
        self.v2_site_port = options.get('v2_site_port')

        self.collection_map = {}
        self.document_map = {}
        self.media_map = {}
        self.image_map = {}
        self.page_translation_map = {}
        self.v1_to_v2_page_map = {}
        self.post_migration_report_messages = defaultdict(list)
        self.registration_survey_translations = defaultdict()

        self.clear()
        self.stdout.write('Existing site structure cleared')

        root = Page.get_first_root_node()
        self.migrate(root)
        self.print_post_migration_report()

    def clear(self):
        PageRevision.objects.all().delete()
        models.OfflineAppPage.objects.all().delete()
        models.MiscellaneousIndexPage.objects.all().delete()
        models.PageLinkPage.objects.all().delete()
        PollFormField.objects.all().delete()
        Poll.objects.all().delete()
        SurveyFormField.objects.all().delete()
        Survey.objects.all().delete()
        QuizFormField.objects.all().delete()
        Quiz.objects.all().delete()
        models.FeaturedContent.objects.all().delete()
        models.ArticleRecommendation.objects.all().delete()
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
        Document.objects.all().delete()
        Media.objects.all().delete()
        V1ToV2ObjectMap.objects.all().delete()

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
        self.migrate_collections()
        self.migrate_documents()
        self.migrate_media()
        self.migrate_images()
        self.migrate_locales()
        self.load_page_translation_map()
        self.home_page = self.create_home_page(root)
        self.translate_home_pages()
        self.create_index_pages()
        self.translate_index_pages()
        self.migrate_sections()
        self.migrate_articles()
        self.migrate_footers()
        self.migrate_polls()
        self.migrate_surveys()
        self.migrate_banners()
        self.mark_pages_which_are_not_translated_in_v1_as_draft()
        Page.fix_tree(fix_paths=True)
        self.mark_empty_sections_as_draft()
        self.fix_articles_body()
        self.fix_footers_body()
        self.fix_survey_description()
        self.fix_banner_link_page()
        self.attach_banners_to_home_page()
        self.migrate_recommended_articles_for_article()
        self.migrate_featured_articles_for_homepage()
        self.add_surveys_from_surveys_index_page_to_footer_index_page_as_page_link_page()
        self.add_polls_from_polls_index_page_to_footer_index_page_as_page_link_page()
        self.add_polls_from_polls_index_page_to_home_page_featured_content()
        self.add_surveys_from_surveys_index_page_to_home_page_featured_content()
        self.move_footers_to_end_of_footer_index_page()
        self.migrate_article_related_sections()
        self.migrate_social_media_links()
        self.sort_pages()
        self.populate_registration_survey_translations()
        self.translate_default_survey_submit_button_text()
        self.migrate_post_registration_survey()
        self.migrate_page_revisions()
        self.stop_translations()

    def create_home_page(self, root):
        sql = 'select * ' \
              'from wagtailcore_site wcs, core_sitesettings css, core_main cm, wagtailcore_page wcp ' \
              'where wcs.id = css.site_id ' \
              'and wcs.root_page_id = cm.page_ptr_id ' \
              'and cm.page_ptr_id = wcp.id ' \
              'and wcs.is_default_site = true'
        cur = self.db_query(sql)
        main = cur.fetchone()
        cur.close()
        if not main:
            raise Exception('Could not find a main page in v1 DB')

        sql = 'select * ' \
              'from core_sitelanguage ' \
              'where is_main_language = true'
        cur = self.db_query(sql)
        language = cur.fetchone()
        cur.close()
        if not language:
            raise Exception('Could not find a main language in v1 DB')

        locale = Locale.objects.get(language_code=self._get_iso_locale(language['locale']))
        models.LocaleDetail.objects.update_or_create(
            locale=locale,
            defaults={
                'is_active': True,
                'is_main_language': True,
            }
        )

        home = models.HomePage(
            title=main['title'],
            draft_title=main['draft_title'],
            slug=main['slug'],
            live=main['live'],
            locked=main['locked'],
            go_live_at=main['go_live_at'],
            expire_at=main['expire_at'],
            first_published_at=main['first_published_at'],
            last_published_at=main['last_published_at'],
            search_description=main['search_description'],
            seo_title=main['seo_title'],
            locale=locale
        )
        root.add_child(instance=home)
        V1ToV2ObjectMap.create_map(content_object=home, v1_object_id=main['page_ptr_id'])

        Site.objects.create(
            hostname=self.v1_domains_list[0],
            port=443,
            root_page=home,
            is_default_site=True,
            site_name=main['site_name'] if main['site_name'] else 'Internet of Good Things',
        )
        logo = self.image_map.get(main['logo_id'])
        if logo:
            site_settings = models.SiteSettings.get_for_default_site()
            site_settings.logo_id = logo.id
            site_settings.save()
        else:
            self.post_migration_report_messages['other'].append(
                'Not site logo found. Using default site logo.'
            )

        sql = f'select * ' \
              f'from core_sitesettings css, wagtailcore_site wcs ' \
              f'where css.site_id = wcs.id ' \
              f'and wcs.is_default_site = true'
        cur = self.db_query(sql)
        for row in cur:
            social_media_links = json.loads(row['social_media_links_on_footer_page'])
            if social_media_links:
                links = []
                for social_media_link in social_media_links:
                    value = social_media_link.get('value')
                    if value:
                        links.append({
                            'title': value.get('title'),
                            'link': value.get('link'),
                        })

                self.post_migration_report_messages['social_media_links'].append(
                    f'site: {row["site_name"]}, hostname: {row["hostname"]} has following social media links '
                    f'{[(link["title"], link["link"]) for link in links]}.')

        cur.close()

        self.post_migration_report_messages['other'].append(
            'A default favicon has been chosen for the site.'
        )

        return home

    def create_index_pages(self):
        self.section_index_page = models.SectionIndexPage(title='Sections')
        self.home_page.add_child(instance=self.section_index_page)

        self.banner_index_page = models.BannerIndexPage(title='Banners')
        self.home_page.add_child(instance=self.banner_index_page)

        self.footer_index_page = models.FooterIndexPage(title='Footers')
        self.home_page.add_child(instance=self.footer_index_page)

        self.poll_index_page = PollIndexPage(title='Polls')
        self.home_page.add_child(instance=self.poll_index_page)

        self.survey_index_page = SurveyIndexPage(title='Surveys')
        self.home_page.add_child(instance=self.survey_index_page)

        self.quiz_index_page = QuizIndexPage(title='Quizzes')
        self.home_page.add_child(instance=self.quiz_index_page)

        self.miscellaneous_index_page = models.MiscellaneousIndexPage(title='Miscellaneous')
        self.home_page.add_child(instance=self.miscellaneous_index_page)

    def migrate_collections(self):
        cur = self.db_query('select * from wagtailcore_collection')
        for row in cur:
            collection, _ = Collection.objects.get_or_create(
                name=row['name'],
                defaults={
                    'path': row['path'],
                    'depth': row['depth'],
                    'numchild': row['numchild'],
                }
            )
            collection.save()
            self.collection_map.update({row['id']: collection})
            V1ToV2ObjectMap.create_map(content_object=collection, v1_object_id=row['id'])

        cur.close()
        self.stdout.write('Collections migrated')

    def migrate_documents(self):
        cur = self.db_query('select * from wagtaildocs_document')
        content_type = self.find_content_type_id('wagtaildocs', 'document')
        for row in cur:
            if not row['file']:
                self.post_migration_report_messages['document_file_not_found'].append(
                    f'Document file path not found, id={row["id"]}'
                )
                continue

            file = self.open_file(row['file'])
            if file:
                document = Document.objects.create(
                    title=row['title'],
                    file=File(file, name=row['file'].split('/')[-1]),
                    created_at=row['created_at'],
                    collection=self.collection_map.get(row['collection_id']),
                )
                V1ToV2ObjectMap.create_map(content_object=document, v1_object_id=row['id'])
                tags = self.find_tags(content_type, row['id'])
                if tags:
                    document.tags.add(*tags)
                self.document_map.update({row['id']: document})
        cur.close()
        self.stdout.write('Documents migrated')

    def migrate_media(self):
        cur = self.db_query('select * from core_molomedia')
        content_type = self.find_content_type_id('core', 'molomedia')
        for row in cur:
            if not row['file']:
                self.post_migration_report_messages['media_file_not_found'].append(
                    f'Media file path not found, id={row["id"]}'
                )
                continue

            file = self.open_file(row['file'])
            if file:
                thumbnail = self.open_file(row['thumbnail'])
                media = Media.objects.create(
                    title=row['title'],
                    file=File(file, name=row['file'].split('/')[-1]),
                    type=row['type'],
                    duration=row['duration'],
                    thumbnail=File(thumbnail, name=row['thumbnail'].split('/')[-1]) if thumbnail else None,
                    created_at=row['created_at'],
                    collection=self.collection_map.get(row['collection_id']),
                )
                V1ToV2ObjectMap.create_map(content_object=media, v1_object_id=row['id'])
                tags = self.find_tags(content_type, row['id'])
                if tags:
                    media.tags.add(*tags)
                self.media_map.update({row['id']: media})
        cur.close()
        self.stdout.write('Media migrated')

    def migrate_images(self):
        cur = self.db_query('select * from wagtailimages_image')
        content_type = self.find_content_type_id('wagtailimages', 'image')
        for row in cur:
            if not row['file']:
                self.post_migration_report_messages['image_file_not_found'].append(
                    f'Image file path not found, id={row["id"]}'
                )
                continue

            image_file = self.open_file(row['file'])
            if image_file:
                self.stdout.write(f"Creating image, file={row['file']}")
                image = Image.objects.create(
                    title=row['title'],
                    file=ImageFile(image_file, name=row['file'].split('/')[-1]),
                    focal_point_x=row['focal_point_x'],
                    focal_point_y=row['focal_point_y'],
                    focal_point_width=row['focal_point_width'],
                    focal_point_height=row['focal_point_height'],
                    created_at=row['created_at'],
                    collection=self.collection_map.get(row['collection_id']),
                )
                V1ToV2ObjectMap.create_map(content_object=image, v1_object_id=row['id'])
                image.get_file_size()
                image.get_file_hash()
                tags = self.find_tags(content_type, row['id'])
                if tags:
                    image.tags.add(*tags)
                self.image_map.update({row['id']: image})
        cur.close()
        self.stdout.write('Images migrated')

    def migrate_locales(self):
        sql = f'select * ' \
              f'from core_sitelanguage'
        cur = self.db_query(sql)
        should_deactivate_en_locale = True
        for row in cur:
            language_code = self._get_iso_locale(row['locale'])
            if language_code == 'en':
                should_deactivate_en_locale = False
            locale, __ = Locale.objects.get_or_create(language_code=language_code)
            models.LocaleDetail.objects.get_or_create(
                locale=locale,
                defaults={
                    'is_active': True,
                    'is_main_language': False,
                }
            )

        if should_deactivate_en_locale:
            locale, __ = Locale.objects.get_or_create(language_code='en')
            models.LocaleDetail.objects.update_or_create(
                locale=locale,
                defaults={
                    'is_active': False,
                    'is_main_language': False,
                }
            )
        cur.close()

    def find_content_type_id(self, app_label, model):
        cur = self.db_query(f"select id from django_content_type where app_label = '{app_label}' and model = '{model}'")
        content_type = cur.fetchone()
        cur.close()
        return content_type.get('id')

    def open_file(self, file):
        file_path = Path(self.media_dir) / file
        try:
            return open(file_path, 'rb')
        except:
            self.post_migration_report_messages['file_not_found'].append(
                f"File not found: {file_path}"
            )

    def find_tags(self, content_type, object_id):
        tags_query = 'select t.name from taggit_tag t join taggit_taggeditem ti on t.id = ti.tag_id where ti.content_type_id = {} and ti.object_id = {}'
        cur = self.db_query(tags_query.format(content_type, object_id))
        tags = [tag['name'] for tag in cur]
        cur.close()
        return tags

    def migrate_sections(self):
        sql = f"select * " \
              f"from core_sectionpage csp, wagtailcore_page wcp, core_languagerelation clr, core_sitelanguage csl " \
              f"where csp.page_ptr_id = wcp.id " \
              f"and wcp.id = clr.page_id " \
              f"and clr.language_id = csl.id " \
              f"order by wcp.path"
        cur = self.db_query(sql)
        section_page_translations = []
        for row in cur:
            if row['page_ptr_id'] in self.page_translation_map:
                section_page_translations.append(row)
            else:
                self.create_section(row)
        else:
            for row in section_page_translations:
                section = self.v1_to_v2_page_map.get(self.page_translation_map[row['page_ptr_id']])
                locale, __ = Locale.objects.get_or_create(language_code=self._get_iso_locale(row['locale']))

                try:
                    self.translate_page(locale=locale, page=section)
                except:
                    self.post_migration_report_messages['untranslated_sections'].append(
                        f"Unable to translate section, title={row['title']}"
                    )
                    continue

                translated_section = section.get_translation_or_none(locale)
                if translated_section:
                    commenting_status, commenting_open_time, commenting_close_time = self._get_commenting_fields(row)

                    translated_section.lead_image = self.image_map.get(row['image_id'])
                    translated_section.title = row['title']
                    translated_section.slug = row['slug']
                    translated_section.draft_title = row['draft_title']
                    translated_section.live = row['live']
                    translated_section.locked = row['locked']
                    translated_section.go_live_at = row['go_live_at']
                    translated_section.expire_at = row['expire_at']
                    translated_section.first_published_at = row['first_published_at']
                    translated_section.last_published_at = row['last_published_at']
                    translated_section.search_description = row['search_description']
                    translated_section.seo_title = row['seo_title']
                    translated_section.font_color = self.get_color_hex(row['extra_style_hints']) or section.font_color
                    translated_section.larger_image_for_top_page_in_list_as_in_v1 = True
                    translated_section.commenting_status = commenting_status
                    translated_section.commenting_starts_at = commenting_open_time
                    translated_section.commenting_ends_at = commenting_close_time
                    translated_section.latest_revision_created_at = row['latest_revision_created_at']
                    translated_section.save()
                    self.add_warning_for_sections_with_description(row, section)
                    content_type = self.find_content_type_id('core', 'sectionpage')
                    tags = self.find_tags(content_type, row['page_ptr_id'])
                    if tags:
                        translated_section.tags.add(*tags)

                    V1ToV2ObjectMap.create_map(content_object=translated_section, v1_object_id=row['page_ptr_id'])
                    V1PageURLToV2PageMap.create_map(url=row['url_path'], page=translated_section)

                    self.v1_to_v2_page_map.update({
                        row['page_ptr_id']: translated_section
                    })
                    if row['description'] is None:
                        self.post_migration_report_messages['sections_with_null_description'].append(
                            f'title: {translated_section.title}. URL: {translated_section.full_url}. '
                            f'Admin URL: {self.get_admin_url(translated_section.id)}.'
                        )

                self.stdout.write(f"Translated section, title={row['title']}")
        cur.close()

    def mark_empty_sections_as_draft(self):
        for section in models.Section.objects.all():
            if section.get_children().filter(live=True).count() == 0:
                section.live = False
                section.save(update_fields=['live'])

    def create_section(self, row):
        commenting_status, commenting_open_time, commenting_close_time = self._get_commenting_fields(row)

        section = models.Section(
            lead_image=self.image_map.get(row['image_id']),
            title=row['title'],
            draft_title=row['draft_title'],
            show_in_menus=True,
            slug=row['slug'],
            path=self.section_index_page.path + row['path'][12:],
            depth=row['depth'],
            numchild=row['numchild'],
            live=row['live'],
            locked=row['locked'],
            go_live_at=row['go_live_at'],
            expire_at=row['expire_at'],
            first_published_at=row['first_published_at'],
            last_published_at=row['last_published_at'],
            commenting_status=commenting_status,
            commenting_starts_at=commenting_open_time,
            commenting_ends_at=commenting_close_time,
            search_description=row['search_description'],
            seo_title=row['seo_title'],
            font_color=self.get_color_hex(row['extra_style_hints']),
            larger_image_for_top_page_in_list_as_in_v1=True,
            latest_revision_created_at=row['latest_revision_created_at'],
        )
        section.save()
        self.add_warning_for_sections_with_description(row, section)
        content_type = self.find_content_type_id('core', 'sectionpage')
        tags = self.find_tags(content_type, row['page_ptr_id'])
        if tags:
            section.tags.add(*tags)

        V1ToV2ObjectMap.create_map(content_object=section, v1_object_id=row['page_ptr_id'])
        V1PageURLToV2PageMap.create_map(url=row['url_path'], page=section)

        self.v1_to_v2_page_map.update({
            row['page_ptr_id']: section
        })
        if row['description'] is None:
            self.post_migration_report_messages['sections_with_null_description'].append(
                f'title: {section.title}. URL: {section.full_url}. '
                f'Admin URL: {self.get_admin_url(section.id)}.'
            )
        self.stdout.write(f"saved section, title={section.title}")

    def add_warning_for_sections_with_description(self, row, section):
        if row['description']:
            self.post_migration_report_messages['sections_with_description'].append(
                f'title: {section.title}. URL: {section.full_url}. '
                f'Admin URL: {self.get_admin_url(section.id)}. '
                f'Description (not migrated): {row["description"]}.'
            )

    def migrate_articles(self):
        sql = f"select * " \
              f"from core_articlepage cap, wagtailcore_page wcp, core_languagerelation clr, core_sitelanguage csl " \
              f"where cap.page_ptr_id = wcp.id " \
              f"and wcp.id = clr.page_id " \
              f"and clr.language_id = csl.id " \
              f"and wcp.path like '000100010002%' " \
              f"order by wcp.path"
        cur = self.db_query(sql)

        article_page_translations = []
        for row in cur:
            if row['page_ptr_id'] in self.page_translation_map:
                article_page_translations.append(row)
            else:
                self.create_article(row)
        else:
            for row in article_page_translations:
                article = self.v1_to_v2_page_map.get(self.page_translation_map[row['page_ptr_id']])
                locale, __ = Locale.objects.get_or_create(language_code=self._get_iso_locale(row['locale']))

                try:
                    self.translate_page(locale=locale, page=article)
                except:
                    self.post_migration_report_messages['untranslated_articles'].append(
                        f"Unable to translate article, title={row['title']}"
                    )
                    continue

                translated_article = article.get_translation_or_none(locale)

                if translated_article:
                    commenting_status, commenting_open_time, commenting_close_time = self._get_commenting_fields(row)

                    translated_article.lead_image = self.image_map.get(row['image_id'])
                    translated_article.title = row['title']
                    translated_article.slug = row['slug']
                    translated_article.draft_title = row['draft_title']
                    translated_article.live = row['live']
                    translated_article.locked = row['locked']
                    translated_article.go_live_at = row['go_live_at']
                    translated_article.expire_at = row['expire_at']
                    translated_article.first_published_at = row['first_published_at']
                    translated_article.last_published_at = row['last_published_at']
                    translated_article.search_description = row['search_description']
                    translated_article.seo_title = row['seo_title']
                    translated_article.index_page_description = row['subtitle']
                    translated_article.commenting_status = commenting_status
                    translated_article.commenting_starts_at = commenting_open_time
                    translated_article.commenting_ends_at = commenting_close_time
                    translated_article.latest_revision_created_at = row['latest_revision_created_at']
                    translated_article.save()
                    if row['featured_in_latest']:
                        self.post_migration_report_messages['articles_featured_in_latest'].append(
                            f'title: {article.title}. URL: {article.full_url}. '
                            f'Admin URL: {self.get_admin_url(article.id)}.'
                        )

                    content_type = self.find_content_type_id('core', 'articlepage')
                    tags = self.find_tags(content_type, row['page_ptr_id'])
                    if tags:
                        translated_article.tags.add(*tags)

                    V1ToV2ObjectMap.create_map(content_object=translated_article, v1_object_id=row['page_ptr_id'])
                    V1PageURLToV2PageMap.create_map(url=row['url_path'], page=translated_article)

                    self.v1_to_v2_page_map.update({
                        row['page_ptr_id']: translated_article
                    })

                self.stdout.write(f"Translated article, title={row['title']}")
        cur.close()

    def _get_commenting_fields(self, row):
        comments_map = {
            'O': CommentStatus.OPEN,
            'C': CommentStatus.CLOSED,
            'D': CommentStatus.DISABLED,
            'T': CommentStatus.TIMESTAMPED
        }

        commenting_status = comments_map[row['commenting_state']] if row['commenting_state'] else CommentStatus.INHERITED
        return commenting_status, row['commenting_open_time'], row['commenting_close_time']

    def create_article(self, row):
        commenting_status, commenting_open_time, commenting_close_time = self._get_commenting_fields(row)

        article = models.Article(
            lead_image=self.image_map.get(row['image_id']),
            title=row['title'],
            draft_title=row['draft_title'],
            slug=row['slug'],
            path=self.section_index_page.path + row['path'][12:],
            depth=row['depth'],
            numchild=row['numchild'],
            live=row['live'],
            locked=row['locked'],
            go_live_at=row['go_live_at'],
            expire_at=row['expire_at'],
            first_published_at=row['first_published_at'],
            last_published_at=row['last_published_at'],
            commenting_status=commenting_status,
            commenting_starts_at=commenting_open_time,
            commenting_ends_at=commenting_close_time,
            search_description=row['search_description'],
            seo_title=row['seo_title'],
            index_page_description=row['subtitle'],
            latest_revision_created_at=row['latest_revision_created_at'],
        )
        try:
            article.save()
            if row['featured_in_latest']:
                self.post_migration_report_messages['articles_featured_in_latest'].append(
                    f'title: {article.title}. URL: {article.full_url}. '
                    f'Admin URL: {self.get_admin_url(article.id)}.'
                )

            content_type = self.find_content_type_id('core', 'articlepage')
            tags = self.find_tags(content_type, row['page_ptr_id'])
            if tags:
                article.tags.add(*tags)

            V1ToV2ObjectMap.create_map(content_object=article, v1_object_id=row['page_ptr_id'])
            V1PageURLToV2PageMap.create_map(url=row['url_path'], page=article)

            self.v1_to_v2_page_map.update({
                row['page_ptr_id']: article
            })
        except Page.DoesNotExist:
            self.post_migration_report_messages['articles'].append(
                f"Skipping article with missing parent: title={row['title']}"
            )
            return
        self.stdout.write(f"saved article, title={article.title}")

    def get_unsupported_html_tags(self, value):
        bleach_kwargs = _get_bleach_kwargs()

        unsupported_html_tags = []
        tags = BeautifulSoup(value, "html.parser").find_all()
        for tag in tags:
            if tag.name not in bleach_kwargs['tags']:
                unsupported_html_tags.append(tag.name)

        return unsupported_html_tags

    def _map_body(self, type_, row, v2_body):
        for block in v2_body:
            if block['type'] == 'paragraph':
                unsupported_html_tags = self.get_unsupported_html_tags(block['value'])
                if unsupported_html_tags:
                    block['type'] = 'paragraph_v1_legacy'
                    page = self.v1_to_v2_page_map.get(row['page_ptr_id'])
                    if page:
                        self.post_migration_report_messages['page_with_unsupported_tags'].append(
                            f'title: {page.title}. URL: {page.full_url}. '
                            f'Admin URL: {self.get_admin_url(page.id)}. '
                            f'Tags: {unsupported_html_tags}.'
                        )
                else:
                    block['type'] = 'markdown'

                if bool([domain for domain in self.v1_domains_list if domain in block['value']]):
                    page = self.v1_to_v2_page_map.get(row['page_id'])
                    self.post_migration_report_messages['sections_with_internal_links'].append(
                        f"title: {page.title}. URL: {page.full_url}. "
                        f"Admin URL: {self.get_admin_url(page.id)}.")

            elif block['type'] == 'richtext':
                block['type'] = 'paragraph'

                if bool([domain for domain in self.v1_domains_list if domain in block['value']]):
                    page = self.v1_to_v2_page_map.get(row['page_id'])
                    self.post_migration_report_messages['sections_with_internal_links'].append(
                        f"title: {page.title}. URL: {page.full_url}. "
                        f"Admin URL: {self.get_admin_url(page.id)}.")

            elif block['type'] == 'image':
                image = self.image_map.get(block['value'])
                if image:
                    block['value'] = image.id
                else:
                    page = self.v1_to_v2_page_map.get(row['page_ptr_id'])
                    if page:
                        self.post_migration_report_messages['page_with_empty_image'].append(
                            f'title: {page.title}. URL: {page.full_url}. '
                            f'Admin URL: {self.get_admin_url(page.id)}. '
                            f'Image ID: {block["value"]}'
                        )
                    else:
                        self.post_migration_report_messages['invalid_image_id'].append(
                            f"title={row['title']} has image with invalid id {block['value']}"
                        )
                    block['value'] = None
            elif block['type'] == 'media':
                media = self.media_map.get(block['value'])
                if media:
                    block['value'] = media.id
                else:
                    self.post_migration_report_messages['invalid_media_id'].append(
                        f"title={row['title']} has media with invalid id {block['value']}"
                    )
                    block['value'] = None
            elif block['type'] == 'page':
                block['type'] = 'page_button'
                page = self.v1_to_v2_page_map.get(block['value'])
                if page:
                    block['value'] = {'page': page.id, 'text': ''}
                else:
                    block['value'] = {'page': None, 'text': ''}
                    self.post_migration_report_messages['invalid_page_id'].append(
                        f'Unable to attach v2 page for {type_[:-1]}, title={row["title"]}'
                    )
        return v2_body

    def map_article_body(self, row):
        v1_body = json.loads(row['body'])

        v2_body = self._map_body('articles', row, v1_body)

        if row['subtitle']:
            v2_body = [{
                'type': 'paragraph',
                'value': row['subtitle'],
            }] + v2_body
        return json.dumps(v2_body)

    def migrate_banners(self):
        sql = f"select * " \
              f"from core_bannerpage cbp, wagtailcore_page wcp, core_languagerelation clr, core_sitelanguage csl " \
              f"where cbp.page_ptr_id = wcp.id " \
              f"and wcp.id = clr.page_id " \
              f"and clr.language_id = csl.id " \
              f"order by wcp.path"
        cur = self.db_query(sql)
        banner_page_translations = []
        for row in cur:
            if row['page_ptr_id'] in self.page_translation_map:
                banner_page_translations.append(row)
            else:
                self.create_banner(row)
        else:
            for row in banner_page_translations:
                banner = self.v1_to_v2_page_map.get(self.page_translation_map[row['page_ptr_id']])
                locale, __ = Locale.objects.get_or_create(language_code=self._get_iso_locale(row['locale']))

                try:
                    self.translate_page(locale=locale, page=banner)
                except:
                    self.post_migration_report_messages['untranslated_banners'].append(
                        f"Unable to translate banner, title={row['title']}"
                    )
                    continue

                translated_banner = banner.get_translation_or_none(locale)
                if translated_banner:
                    translated_banner.banner_image = self.image_map.get(row['banner_id'])
                    translated_banner.title = row['title']
                    translated_banner.slug = row['slug']
                    translated_banner.draft_title = row['draft_title']
                    translated_banner.live = row['live']
                    translated_banner.locked = row['locked']
                    translated_banner.go_live_at = row['go_live_at']
                    translated_banner.expire_at = row['expire_at']
                    translated_banner.first_published_at = row['first_published_at']
                    translated_banner.last_published_at = row['last_published_at']
                    translated_banner.search_description = row['search_description']
                    translated_banner.seo_title = row['seo_title']
                    translated_banner.latest_revision_created_at = row['latest_revision_created_at']
                    translated_banner.save()

                    if row['external_link']:
                        self.post_migration_report_messages['banners_with_external_link'].append(
                            f'title: {translated_banner.title}. URL: {translated_banner.full_url}. '
                            f'Admin URL: {self.get_admin_url(translated_banner.id)}. '
                            f'External link: {row["external_link"]}.'
                        )

                    V1ToV2ObjectMap.create_map(content_object=translated_banner, v1_object_id=row['page_ptr_id'])
                    V1PageURLToV2PageMap.create_map(url=row['url_path'], page=translated_banner)

                    self.v1_to_v2_page_map.update({
                        row['page_ptr_id']: translated_banner
                    })

                self.stdout.write(f"Translated banner, title={row['title']}")
        cur.close()

    def create_banner(self, row):
        banner = models.BannerPage(
            banner_image=self.image_map.get(row['banner_id']),
            title=row['title'],
            draft_title=row['draft_title'],
            slug=row['slug'],
            path=self.banner_index_page.path + row['path'][12:],
            depth=row['depth'],
            numchild=row['numchild'],
            live=row['live'],
            banner_description='',
            locked=row['locked'],
            go_live_at=row['go_live_at'],
            expire_at=row['expire_at'],
            first_published_at=row['first_published_at'],
            last_published_at=row['last_published_at'],
            search_description=row['search_description'],
            seo_title=row['seo_title'],
            latest_revision_created_at=row['latest_revision_created_at'],
        )
        banner.save()

        if row['external_link']:
            self.post_migration_report_messages['banners_with_external_link'].append(
                f'title: {banner.title}. URL: {banner.full_url}. '
                f'Admin URL: {self.get_admin_url(banner.id)}. '
                f'External link: {row["external_link"]}.'
            )

        V1ToV2ObjectMap.create_map(content_object=banner, v1_object_id=row['page_ptr_id'])
        V1PageURLToV2PageMap.create_map(url=row['url_path'], page=banner)

        self.v1_to_v2_page_map.update({
            row['page_ptr_id']: banner
        })
        self.stdout.write(f"saved banner, title={banner.title}")

    def map_banner_page(self, row):
        v2_page = None
        v1_banner_link_page_id = row['banner_link_page_id']
        if v1_banner_link_page_id:
            v2_page = self.v1_to_v2_page_map.get(v1_banner_link_page_id)
            if not v2_page:
                self.post_migration_report_messages['banner_page_link'].append(
                    f'Unable to attach v2 page for banner, title={row["title"]}'
                )

        return v2_page

    def migrate_footers(self):
        sql = f"select * " \
              f"from core_footerpage cfp, core_articlepage cap, wagtailcore_page wcp, core_languagerelation clr, core_sitelanguage csl " \
              f"where cfp.articlepage_ptr_id = cap.page_ptr_id " \
              f"and cap.page_ptr_id = wcp.id " \
              f"and wcp.id = clr.page_id " \
              f"and clr.language_id = csl.id " \
              f"order by wcp.path"
        cur = self.db_query(sql)
        footer_page_translations = []
        for row in cur:
            if row['page_ptr_id'] in self.page_translation_map:
                footer_page_translations.append(row)
            else:
                self.create_footer(row)
        else:
            for row in footer_page_translations:
                footer = self.v1_to_v2_page_map.get(self.page_translation_map[row['page_ptr_id']])
                locale, __ = Locale.objects.get_or_create(language_code=self._get_iso_locale(row['locale']))

                try:
                    self.translate_page(locale=locale, page=footer)
                except:
                    self.post_migration_report_messages['untranslated_footers'].append(
                        f"Unable to translate footer, title={row['title']}"
                    )
                    continue

                translated_footer = footer.get_translation_or_none(locale)
                if translated_footer:
                    commenting_status, commenting_open_time, commenting_close_time = self._get_commenting_fields(row)

                    image = self.image_map.get(row['image_id'])
                    translated_footer.image_icon = image
                    translated_footer.title = row['title']
                    translated_footer.slug = row['slug']
                    translated_footer.draft_title = row['draft_title']
                    translated_footer.live = row['live']
                    translated_footer.locked = row['locked']
                    translated_footer.go_live_at = row['go_live_at']
                    translated_footer.expire_at = row['expire_at']
                    translated_footer.first_published_at = row['first_published_at']
                    translated_footer.last_published_at = row['last_published_at']
                    translated_footer.search_description = row['search_description']
                    translated_footer.seo_title = row['seo_title']
                    translated_footer.commenting_status = commenting_status
                    translated_footer.commenting_starts_at = commenting_open_time
                    translated_footer.commenting_ends_at = commenting_close_time
                    translated_footer.latest_revision_created_at = row['latest_revision_created_at']
                    translated_footer.save()
                    if row['featured_in_latest']:
                        self.post_migration_report_messages['footers_featured_in_latest'].append(
                            f'title: {translated_footer.title}. URL: {translated_footer.full_url}. '
                            f'Admin URL: {self.get_admin_url(translated_footer.id)}.'
                        )

                    if image:
                        self.post_migration_report_messages['footers_with_image'].append(
                            f'title: {translated_footer.title}. URL: {translated_footer.full_url}. '
                            f'Admin URL: {self.get_admin_url(translated_footer.id)}.'
                        )

                    V1ToV2ObjectMap.create_map(content_object=translated_footer, v1_object_id=row['page_ptr_id'])
                    V1PageURLToV2PageMap.create_map(url=row['url_path'], page=translated_footer)

                    self.v1_to_v2_page_map.update({
                        row['page_ptr_id']: translated_footer
                    })

                self.stdout.write(f"Translated footer, title={row['title']}")
        cur.close()

    def create_footer(self, row):
        commenting_status, commenting_open_time, commenting_close_time = self._get_commenting_fields(row)

        image = self.image_map.get(row['image_id'])
        footer = models.Article(
            image_icon=image,
            title=row['title'],
            draft_title=row['draft_title'],
            slug=row['slug'],
            path=self.footer_index_page.path + row['path'][12:],
            depth=row['depth'],
            numchild=row['numchild'],
            live=row['live'],
            locked=row['locked'],
            go_live_at=row['go_live_at'],
            expire_at=row['expire_at'],
            first_published_at=row['first_published_at'],
            last_published_at=row['last_published_at'],
            search_description=row['search_description'],
            seo_title=row['seo_title'],
            commenting_status=commenting_status,
            commenting_starts_at=commenting_open_time,
            commenting_ends_at=commenting_close_time,
            latest_revision_created_at=row['latest_revision_created_at'],
        )
        footer.save()
        if row['featured_in_latest']:
            self.post_migration_report_messages['footers_featured_in_latest'].append(
                f'title: {footer.title}. URL: {footer.full_url}. '
                f'Admin URL: {self.get_admin_url(footer.id)}.'
            )

        if image:
            self.post_migration_report_messages['footers_with_image'].append(
                f'title: {footer.title}. URL: {footer.full_url}. Admin URL: {self.get_admin_url(footer.id)}.'
            )

        V1ToV2ObjectMap.create_map(content_object=footer, v1_object_id=row['page_ptr_id'])
        V1PageURLToV2PageMap.create_map(url=row['url_path'], page=footer)

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

    def migrate_polls(self):
        sql = f"select * " \
              f"from polls_pollsindexpage ppip, wagtailcore_page wcp " \
              f"where ppip.page_ptr_id = wcp.id " \
              f"order by wcp.path"
        cur = self.db_query(sql)
        v1_poll_index_page = cur.fetchone()
        cur.close()

        self._migrate_polls(v1_poll_index_page, self.poll_index_page)

        sql = f"select * " \
              f"from core_sectionindexpage csip, wagtailcore_page wcp " \
              f"where csip.page_ptr_id = wcp.id " \
              f"order by wcp.path"
        cur = self.db_query(sql)
        v1_section_index_page = cur.fetchone()
        cur.close()

        self._migrate_polls(v1_section_index_page, self.section_index_page)

    def _migrate_polls(self, v1_index_page, v2_index_page):
        sql = f"select * " \
              f"from polls_question pq, wagtailcore_page wcp, core_languagerelation clr, core_sitelanguage csl " \
              f"where pq.page_ptr_id = wcp.id " \
              f"and wcp.id = clr.page_id " \
              f"and clr.language_id = csl.id " \
              f"and wcp.path like '{v1_index_page['path']}%' " \
              f"order by wcp.path"
        cur = self.db_query(sql)
        poll_page_translations = []
        for row in cur:
            if row['page_ptr_id'] in self.page_translation_map:
                poll_page_translations.append(row)
            else:
                self.create_poll(v2_index_page, row)
        else:
            for row in poll_page_translations:
                poll = self.v1_to_v2_page_map.get(self.page_translation_map[row['page_ptr_id']])
                locale, __ = Locale.objects.get_or_create(language_code=self._get_iso_locale(row['locale']))

                try:
                    self.translate_page(locale=locale, page=poll)
                except Exception as e:
                    self.post_migration_report_messages['untranslated_polls'].append(
                        f"Unable to translate poll, title={row['title']}"
                    )
                    continue

                translated_poll = poll.get_translation_or_none(locale)
                if translated_poll:
                    translated_poll.title = row['title']
                    translated_poll.slug = row['slug']
                    translated_poll.draft_title = row['draft_title']
                    translated_poll.live = row['live']
                    translated_poll.result_as_percentage = row['result_as_percentage']
                    translated_poll.show_results = row['show_results']
                    translated_poll.locked = row['locked']
                    translated_poll.go_live_at = row['go_live_at']
                    translated_poll.expire_at = row['expire_at']
                    translated_poll.first_published_at = row['first_published_at']
                    translated_poll.last_published_at = row['last_published_at']
                    translated_poll.search_description = row['search_description']
                    translated_poll.seo_title = row['seo_title']
                    translated_poll.randomise_options = row['randomise_options']
                    translated_poll.allow_anonymous_submissions = False
                    translated_poll.allow_multiple_submissions = False
                    translated_poll.latest_revision_created_at = row['latest_revision_created_at']
                    translated_poll.save()

                    V1ToV2ObjectMap.create_map(content_object=translated_poll, v1_object_id=row['page_ptr_id'])
                    V1PageURLToV2PageMap.create_map(url=row['url_path'], page=translated_poll)

                    self.v1_to_v2_page_map.update({
                        row['page_ptr_id']: translated_poll
                    })

                    row['path'] = row['path'][:-4]
                    self.migrate_poll_questions(translated_poll, row)

                self.stdout.write(f"Translated poll, title={row['title']}")
        cur.close()

    def create_poll(self, v2_index_page, row):
        poll = Poll(
            title=row['title'],
            draft_title=row['draft_title'],
            show_in_menus=True,
            slug=row['slug'],
            path=v2_index_page.path + row['path'][12:],
            depth=row['depth'],
            numchild=row['numchild'],
            live=row['live'],
            show_results=row['show_results'],
            result_as_percentage=row['result_as_percentage'],
            locked=row['locked'],
            go_live_at=row['go_live_at'],
            expire_at=row['expire_at'],
            first_published_at=row['first_published_at'],
            last_published_at=row['last_published_at'],
            search_description=row['search_description'],
            seo_title=row['seo_title'],
            randomise_options=row['randomise_options'],
            allow_anonymous_submissions=False,
            allow_multiple_submissions=False,
            latest_revision_created_at=row['latest_revision_created_at'],
        )
        try:
            poll.save()
            V1ToV2ObjectMap.create_map(content_object=poll, v1_object_id=row['page_ptr_id'])
            V1PageURLToV2PageMap.create_map(url=row['url_path'], page=poll)
        except Exception as e:
            self.post_migration_report_messages['polls'].append(
                f"Unable to save poll, title={row['title']}"
            )
            return

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
              f'and csl.locale = \'{poll_row["locale"]}\' ' \
              f'order by wcp.path'
        cur = self.db_query(sql)
        self.create_poll_question(poll, poll_row, cur)
        cur.close()

    def create_poll_question(self, poll, poll_row, cur):
        PollFormField.objects.filter(page=poll).delete()
        choices = []
        for row in cur:
            choices.append(row['title'])

        choices_length = len(choices)

        if choices_length == 0:
            field_type = 'multiline'
        elif choices_length > 1:
            if poll_row['allow_multiple_choice']:
                field_type = 'checkboxes'
            else:
                field_type = 'radio'
        else:
            self.post_migration_report_messages['poll_questions'].append(
                f'Unable to determine field type for poll={poll_row["title"]}.'
            )
            return

        choices = '|'.join(choices)

        poll_form_field = PollFormField.objects.create(
            page=poll, label=poll.title, field_type=field_type, choices=choices,
            admin_label=poll_row['short_name'] or poll.title)
        if choices:
            cur.scroll(0, 'absolute')
        for row in cur:
            V1ToV2ObjectMap.create_map(content_object=poll_form_field, v1_object_id=row['page_ptr_id'])
        self.stdout.write(f"saved poll question, label={poll.title}")

    def migrate_surveys(self):
        sql = f"select * " \
              f"from surveys_surveysindexpage ssip, wagtailcore_page wcp " \
              f"where ssip.page_ptr_id = wcp.id " \
              f"order by wcp.path"
        cur = self.db_query(sql)
        v1_survey_index_page = cur.fetchone()
        cur.close()

        self._migrate_surveys(v1_survey_index_page, self.survey_index_page)

        sql = f"select * " \
              f"from core_sectionindexpage csip, wagtailcore_page wcp " \
              f"where csip.page_ptr_id = wcp.id " \
              f"order by wcp.path"
        cur = self.db_query(sql)
        v1_section_index_page = cur.fetchone()
        cur.close()

        self._migrate_surveys(v1_section_index_page, self.section_index_page)

    def _migrate_surveys(self, v1_index_page, v2_index_page):
        sql = f"select * " \
              f"from surveys_molosurveypage smsp, wagtailcore_page wcp, core_languagerelation clr, core_sitelanguage csl " \
              f"where smsp.page_ptr_id = wcp.id " \
              f"and wcp.id = clr.page_id " \
              f"and clr.language_id = csl.id " \
              f"and wcp.path like '{v1_index_page['path']}%' " \
              f"order by wcp.path"
        cur = self.db_query(sql)
        survey_page_translations = []
        for row in cur:
            if row['page_ptr_id'] in self.page_translation_map:
                survey_page_translations.append(row)
            else:
                self.create_survey(v2_index_page, row)
        else:
            for row in survey_page_translations:
                survey = self.v1_to_v2_page_map.get(self.page_translation_map[row['page_ptr_id']])
                locale, __ = Locale.objects.get_or_create(language_code=self._get_iso_locale(row['locale']))

                try:
                    self.translate_page(locale=locale, page=survey)
                except Exception as e:
                    self.post_migration_report_messages['untranslated_surveys'].append(
                        f"Unable to translate survey, title={row['title']}"
                    )

                    continue

                translated_survey = survey.get_translation_or_none(locale)
                if translated_survey:
                    translated_survey.title = row['title']
                    translated_survey.slug = row['slug']
                    translated_survey.draft_title = row['draft_title']
                    translated_survey.live = row['live']
                    translated_survey.thank_you_text = self.map_survey_thank_you_text(row)
                    translated_survey.allow_anonymous_submissions = row['allow_anonymous_submissions']
                    translated_survey.allow_multiple_submissions = row['allow_multiple_submissions_per_user']
                    translated_survey.submit_button_text = row['submit_text'][:40] if row['submit_text'] else 'Submit'
                    translated_survey.direct_display = row['display_survey_directly']
                    translated_survey.multi_step = row['multi_step']
                    translated_survey.locked = row['locked']
                    translated_survey.go_live_at = row['go_live_at']
                    translated_survey.expire_at = row['expire_at']
                    translated_survey.first_published_at = row['first_published_at']
                    translated_survey.last_published_at = row['last_published_at']
                    translated_survey.search_description = row['search_description']
                    translated_survey.seo_title = row['seo_title']
                    translated_survey.index_page_description = row['homepage_introduction']
                    translated_survey.index_page_description_line_2 = row['homepage_button_text']
                    translated_survey.terms_and_conditions = self.map_survey_terms_and_conditions(row)
                    translated_survey.latest_revision_created_at = row['latest_revision_created_at']
                    translated_survey.save()

                    if row['submit_text'] and len(row['submit_text']) > 40:
                        self.post_migration_report_messages['truncated_submit_button_text'].append(
                            f'title: {translated_survey.title}. URL: {translated_survey.full_url}. '
                            f'Admin URL: {self.get_admin_url(translated_survey.id)}. '
                            f'Full text: {row["submit_text"]}.'
                        )

                    V1ToV2ObjectMap.create_map(content_object=translated_survey, v1_object_id=row['page_ptr_id'])
                    V1PageURLToV2PageMap.create_map(url=row['url_path'], page=translated_survey)

                    self.v1_to_v2_page_map.update({
                        row['page_ptr_id']: translated_survey
                    })

                    self.migrate_survey_questions(translated_survey, row)

                self.stdout.write(f"Translated survey, title={row['title']}")
        cur.close()

    def create_survey(self, v2_index_page, row):
        survey = Survey(
            title=row['title'],
            draft_title=row['draft_title'],
            show_in_menus=True,
            slug=row['slug'],
            path=v2_index_page.path + row['path'][12:],
            depth=row['depth'],
            numchild=row['numchild'],
            live=row['live'],
            thank_you_text=self.map_survey_thank_you_text(row),
            allow_anonymous_submissions=row['allow_anonymous_submissions'],
            allow_multiple_submissions=row['allow_multiple_submissions_per_user'],
            submit_button_text=row['submit_text'][:40] if row['submit_text'] else 'Submit',
            direct_display=row['display_survey_directly'],
            multi_step=row['multi_step'],
            locked=row['locked'],
            go_live_at=row['go_live_at'],
            expire_at=row['expire_at'],
            first_published_at=row['first_published_at'],
            last_published_at=row['last_published_at'],
            search_description=row['search_description'],
            seo_title=row['seo_title'],
            index_page_description=row['homepage_introduction'],
            index_page_description_line_2=row['homepage_button_text'],
            terms_and_conditions=self.map_survey_terms_and_conditions(row),
            latest_revision_created_at=row['latest_revision_created_at'],
        )

        try:
            survey.save()
            if row['submit_text'] and len(row['submit_text']) > 40:
                self.post_migration_report_messages['truncated_submit_button_text'].append(
                    f'title: {survey.title}. URL: {survey.full_url}. '
                    f'Admin URL: {self.get_admin_url(survey.id)}. '
                    f'Full text: {row["submit_text"]}.'
                )
            V1ToV2ObjectMap.create_map(content_object=survey, v1_object_id=row['page_ptr_id'])
            V1PageURLToV2PageMap.create_map(url=row['url_path'], page=survey)
        except Exception as e:
            self.post_migration_report_messages['surveys'].append(
                f"Unable to save survey, title={row['title']}"
            )
            return

        self.migrate_survey_questions(survey, row)

        self.v1_to_v2_page_map.update({
            row['page_ptr_id']: survey
        })
        self.stdout.write(f"saved survey, title={survey.title}")

    def map_survey_description(self, row):
        v1_survey_description = json.loads(row['description'])
        v2_survey_description = self._map_body('surveys', row, v1_survey_description)

        if row['introduction']:
            v2_survey_description = [{
                'type': 'paragraph',
                'value': row['introduction'],
            }] + v2_survey_description

        return json.dumps(v2_survey_description)

    def map_survey_thank_you_text(self, row):
        v2_thank_you_text = []
        if row['thank_you_text']:
            v2_thank_you_text.append({'type': 'paragraph', 'value': row['thank_you_text']})

        return json.dumps(v2_thank_you_text)

    def map_survey_terms_and_conditions(self, row):
        sql = f'select * ' \
              f'from surveys_surveytermsconditions stc, surveys_molosurveypage msp, wagtailcore_page wcp ' \
              f'where stc.page_id = msp.page_ptr_id ' \
              f'and stc.terms_and_conditions_id = wcp.id ' \
              f'and stc.page_id = {row["page_ptr_id"]} ' \
              f'order by wcp.path'

        cur = self.db_query(sql)
        v1_term_and_condition = cur.fetchone()
        cur.close()
        if v1_term_and_condition:
            return json.dumps([
                {
                    "type": "page_button",
                    "value": {
                        "page": self.v1_to_v2_page_map[v1_term_and_condition["terms_and_conditions_id"]].id,
                    },
                },
            ])

    def migrate_survey_questions(self, survey, survey_row):
        sql = f'select *, smsff.id as smsffid ' \
              f'from surveys_molosurveyformfield smsff, surveys_molosurveypage smsp, wagtailcore_page wcp, core_languagerelation clr, core_sitelanguage csl ' \
              f'where smsff.page_id = smsp.page_ptr_id ' \
              f'and smsp.page_ptr_id = wcp.id ' \
              f'and wcp.id = clr.page_id ' \
              f'and clr.language_id = csl.id ' \
              f'and wcp.id = {survey_row["page_ptr_id"]} ' \
              f'order by wcp.path'
        cur = self.db_query(sql)
        self.create_survey_question(survey, survey_row, cur)
        cur.close()

    def create_survey_question(self, survey, survey_row, cur):
        SurveyFormField.objects.filter(page=survey).delete()

        for row in cur:
            field_type = 'positivenumber' if row['field_type'] == 'positive_number' else row['field_type']
            survey_form_field = SurveyFormField.objects.create(
                page=survey, sort_order=row['sort_order'], label=row['label'], required=row['required'],
                default_value=row['default_value'], help_text=row['help_text'], field_type=field_type,
                admin_label=row['admin_label'], page_break=row['page_break'],
                choices='|'.join(row['choices'].split(',')), skip_logic=row['skip_logic']
            )
            V1ToV2ObjectMap.create_map(content_object=survey_form_field, v1_object_id=row['smsffid'])
            skip_logic_next_actions = [logic['value']['skip_logic'] for logic in json.loads(row['skip_logic'])]
            if not survey_row['multi_step'] and (
                    'end' in skip_logic_next_actions or 'question' in skip_logic_next_actions):
                self.post_migration_report_messages['survey_multistep'].append(
                    f'skip logic without multi step'
                )
            self.stdout.write(f"saved survey question, label={row['label']}")

    def _get_iso_locale(self, locale):
        iso_locales_map = {
            'sho': 'sn',
            'ch': 'ny',
        }

        return iso_locales_map.get(locale, locale)

    def translate_home_pages(self):
        locales = Locale.objects.all()
        for locale in locales:
            self.translate_page(locale=locale, page=self.home_page)
            translated_home_page = self.home_page.get_translation_or_none(locale)
            if translated_home_page:
                translated_home_page.title = f"{translated_home_page.title} [{str(locale)}]"
                translated_home_page.draft_title = f"{translated_home_page.draft_title} [{str(locale)}]"
                translated_home_page.save()

    def translate_index_pages(self):
        index_pages = [
            self.section_index_page, self.banner_index_page, self.footer_index_page, self.poll_index_page,
            self.survey_index_page, self.quiz_index_page, self.miscellaneous_index_page,
        ]
        locales = Locale.objects.all()
        for page in index_pages:
            for locale in locales:
                self.translate_page(locale=locale, page=page)

    def migrate_recommended_articles_for_article(self):
        article_cur = self.db_query(f'select DISTINCT page_id from core_articlepagerecommendedsections')
        for article_row in article_cur:
            v1_article_id = article_row['page_id']
            v2_article = self.v1_to_v2_page_map.get(v1_article_id)
            if v2_article:
                cur = self.db_query(
                    f'select * from core_articlepagerecommendedsections where page_id = {v1_article_id} and recommended_article_id is not null')
                for row in cur:
                    v2_recommended_article = self.v1_to_v2_page_map.get(row['recommended_article_id'])
                    if v2_recommended_article:
                        models.ArticleRecommendation.objects.create(
                            sort_order=row['sort_order'],
                            article=v2_recommended_article,
                            source=v2_article
                        )
                cur.close()
        article_cur.close()
        self.stdout.write('Recommended articles migrated')

    def migrate_featured_articles_for_homepage(self):
        locale_cur = self.db_query(f"select * from core_sitelanguage")
        for locale_row in locale_cur:
            articles_cur = self.db_query(
                f"select * "
                f"from core_articlepage cap, wagtailcore_page wcp, core_languagerelation clr, core_sitelanguage csl "
                f"where cap.page_ptr_id = wcp.id "
                f"and wcp.id = clr.page_id "
                f"and clr.language_id = csl.id "
                f"and wcp.live = true "
                f"and csl.locale = '{locale_row['locale']}' "
                f"order by left(wcp.path, 16) "
            )
            articles_list = []
            for article_row in articles_cur:
                translated_from_page_id = self.page_translation_map.get(article_row['page_ptr_id'])
                featured_in_homepage_start_date = article_row['featured_in_homepage_start_date']
                if translated_from_page_id:
                    translated_from_article_cur = self.db_query(
                        f'select * from core_articlepage where page_ptr_id = {translated_from_page_id}')
                    translated_from_article_row = translated_from_article_cur.fetchone()
                    translated_from_article_cur.close()
                    # For translated articles, only the date of the translated from matters
                    featured_in_homepage_start_date = translated_from_article_row['featured_in_homepage_start_date']

                if featured_in_homepage_start_date:
                    article = self.v1_to_v2_page_map.get(article_row['page_ptr_id'])
                    if article:
                        article.featured_in_homepage_start_date = featured_in_homepage_start_date
                        articles_list.append(article)

            articles_cur.close()

            articles_list = sorted(articles_list, key=lambda x: x.featured_in_homepage_start_date, reverse=True)
            articles_list = sorted(articles_list, key=lambda x: x.path[:16])

            article_groups = defaultdict(list)
            for article in articles_list:
                article_groups[article.path[:16]].append(article)

            for k, v in article_groups.items():
                for i, article in enumerate(v):
                    if i < 5:
                        self.add_article_as_featured_content_in_home_page(article)
                    else:
                        self.post_migration_report_messages['ommitted_old_featured_article'].append(
                            f'title: {article.title}. URL: {article.full_url}. '
                            f'Admin URL: {self.get_admin_url(article.id)}. '
                            f'featured since: {article.featured_in_homepage_start_date}.'
                        )

                section = models.Section.objects.get(path=k)
                self.add_section_as_featured_content_in_home_page(section)

        locale_cur.close()

    def add_article_as_featured_content_in_home_page(self, article):
        home_page = self.home_page.get_translation_or_none(article.locale)
        if home_page:
            home_featured_content = home_page.home_featured_content.stream_data
            home_featured_content.append({
                'type': 'article',
                'value': {
                    'article': article.id,
                    'display_section_title': True,
                },
            })
            home_page.save()

    def add_section_as_featured_content_in_home_page(self, section):
        home_page = self.home_page.get_translation_or_none(section.locale)
        if home_page:
            home_featured_content = home_page.home_featured_content.stream_data
            home_featured_content.append({
                'type': 'page_button',
                'value': {
                    'page': section.id,
                    'text': '',
                },
            })
            home_page.save()

    def attach_banners_to_home_page(self):
        sql = f"select * " \
              f"from core_bannerpage cbp, wagtailcore_page wcp, core_languagerelation clr, core_sitelanguage csl " \
              f"where cbp.page_ptr_id = wcp.id " \
              f"and wcp.id = clr.page_id " \
              f"and clr.language_id = csl.id " \
              f"order by wcp.path"
        cur = self.db_query(sql)
        for row in cur:
            v2_banner = self.v1_to_v2_page_map.get(row['page_ptr_id'])
            if v2_banner:
                home_page = v2_banner.get_ancestors().exact_type(models.HomePage).first().specific
                models.HomePageBanner.objects.create(source=home_page, banner_page=v2_banner)
        cur.close()

    def get_color_hex(self, color_name):
        return {
            '--tiber': '#07292F',
            '--mecury': '#eae9e9',
            '--light_scampi': '#685FA1',
            '--dove_gray': '#737373',
            '--mineral_gray': '#dedede',
            '--washed_gray': '#f1f1f1',
            '--brown': '#a03321',
            '--medium_red_violet': '#B62A99',
            '--dark_medium_red_violet': '#b43393',
            '--violet_blue': '#a54f9e',
            '--mandy': '#E24256',
            '--plum': '#7e2268',
            '--wisteria': '#8e68ad',
            '--grape': '#541c56',
            '--paris_m': '#202855',
            '--east_bay': '#4E4682',
            '--victoria': '#4D4391',
            '--scampi': '#685FA1',
            '--sandybrown': '#EF9955',
            '--jaffa': '#ee8c39',
            '--saffron': '#F2B438',
            '--saffron_light': '#f2b437',
            '--cinnabar': '#EC3B3A',
            '--cinnabar_dark': '#ee5523',
            '--cardinal': '#bf2026',
            '--pomegranate': '#ed3330',
            '--roman': '#DF6859',
            '--mauvelous': '#F38AA5',
            '--beed_blush': '#e764a0',
            '--maxican_red': '#a21d2e',
            '--kobi': '#d481b5',
            '--illusion': '#ee97ac',
            '--celery': '#A4CE55',
            '--de_york': '#6EC17F',
            '--eucalyptus': '#2A9B58',
            '--tradewind': '#4bab99',
            '--moss_green': '#b3d9a1',
            '--danube': '#6093CD',
            '--light_danube': '#627abc',
            '--indigo': '#5F7AC9',
            '--mariner': '#4759a6',
            '--robin_egg_blue': '#00BFC6',
            '--pelorous': '#37BFBE',
            '--iris_blue': '#03acc3',
            '--red_berry': '#711e29',
            '--bay_of_may': '#2b378c',
            '--viking': '#3bbfbd',
            '--denim': '#127f99',
            '--tory_blue': '#134b90',
        }.get(color_name)

    def fix_articles_body(self):
        sql = f"select * " \
              f"from core_articlepage cap, wagtailcore_page wcp, core_languagerelation clr, core_sitelanguage csl " \
              f"where cap.page_ptr_id = wcp.id " \
              f"and wcp.id = clr.page_id " \
              f"and clr.language_id = csl.id " \
              f"and wcp.path like '000100010002%' " \
              f"order by wcp.path"
        cur = self.db_query(sql)
        for row in cur:
            v2_article = self.v1_to_v2_page_map.get(row['page_ptr_id'])
            if v2_article:
                v2_article.refresh_from_db()
                v2_article.body = self.map_article_body(row)
                v2_article.save()
            else:
                self.post_migration_report_messages['articles'].append(
                    f'Unable to add article body, title={row["title"]}'
                )

        cur.close()

    def fix_footers_body(self):
        sql = f"select * " \
              f"from core_footerpage cfp, core_articlepage cap, wagtailcore_page wcp, core_languagerelation clr, core_sitelanguage csl " \
              f"where cfp.articlepage_ptr_id = cap.page_ptr_id " \
              f"and cap.page_ptr_id = wcp.id " \
              f"and wcp.id = clr.page_id " \
              f"and clr.language_id = csl.id " \
              f"order by wcp.path"
        cur = self.db_query(sql)
        for row in cur:
            v2_footer = self.v1_to_v2_page_map.get(row['page_ptr_id'])
            if v2_footer:
                v2_footer.refresh_from_db()
                v2_footer.body = self.map_article_body(row)
                v2_footer.save()
        cur.close()

    def fix_survey_description(self):
        sql = f"select * " \
              f"from surveys_molosurveypage smsp, wagtailcore_page wcp, core_languagerelation clr, core_sitelanguage csl " \
              f"where smsp.page_ptr_id = wcp.id " \
              f"and wcp.id = clr.page_id " \
              f"and clr.language_id = csl.id  " \
              f"order by wcp.path"
        cur = self.db_query(sql)
        for row in cur:
            v2_survey = self.v1_to_v2_page_map.get(row['page_ptr_id'])
            if v2_survey:
                v2_survey.refresh_from_db()
                v2_survey.description = self.map_survey_description(row)
                v2_survey.save()
        cur.close()

    def fix_banner_link_page(self):
        sql = f"select * " \
              f"from core_bannerpage cbp, wagtailcore_page wcp, core_languagerelation clr, core_sitelanguage csl " \
              f"where cbp.page_ptr_id = wcp.id " \
              f"and wcp.id = clr.page_id " \
              f"and clr.language_id = csl.id " \
              f"order by wcp.path"
        cur = self.db_query(sql)
        for row in cur:
            v2_banner = self.v1_to_v2_page_map.get(row['page_ptr_id'])
            if v2_banner:
                v2_banner.refresh_from_db()
                v2_banner.banner_link_page = self.map_banner_page(row)
                v2_banner.save()
        cur.close()

    def add_polls_from_polls_index_page_to_footer_index_page_as_page_link_page(self):
        self.poll_index_page.refresh_from_db()
        self.footer_index_page.refresh_from_db()
        file = File(open(Path(settings.BASE_DIR) / 'iogt/static/icons/clip_board_pen.svg'), name='clip_board_pen.svg')
        icon = Svg.objects.create(title='clip board pen', file=file)
        poll_index_pages = self.poll_index_page.get_translations(inclusive=True)
        for poll_index_page in poll_index_pages:
            polls = poll_index_page.get_children()
            for poll in polls:
                page_link_page = models.PageLinkPage(title=poll.title, page=poll, icon=icon, live=poll.live)
                footer_index_page = self.footer_index_page.get_translation_or_none(poll.locale)
                footer_index_page.add_child(instance=page_link_page)

        self.stdout.write('Added polls from poll index page to footer index page as page link page.')

    def add_surveys_from_surveys_index_page_to_footer_index_page_as_page_link_page(self):
        self.survey_index_page.refresh_from_db()
        self.footer_index_page.refresh_from_db()
        file = File(open(Path(settings.BASE_DIR) / 'iogt/static/icons/loud_speaker.svg'), name='loud_speaker.svg')
        icon = Svg.objects.create(title='loud speaker', file=file)
        survey_index_page = self.survey_index_page.get_translations(inclusive=True)
        for survey_index_page in survey_index_page:
            surveys = survey_index_page.get_children()
            for survey in surveys:
                page_link_page = models.PageLinkPage(title=survey.title, page=survey, icon=icon, live=survey.live)
                footer_index_page = self.footer_index_page.get_translation_or_none(survey.locale)
                footer_index_page.add_child(instance=page_link_page)

        self.stdout.write('Added surveys from survey index page to footer index page as page link page.')

    def mark_pages_which_are_not_translated_in_v1_as_draft(self):
        self.section_index_page.refresh_from_db()
        self.banner_index_page.refresh_from_db()
        self.footer_index_page.refresh_from_db()
        self.poll_index_page.refresh_from_db()
        self.survey_index_page.refresh_from_db()
        self.quiz_index_page.refresh_from_db()

        page_ids_to_exclude = []
        page_ids_to_exclude += self.section_index_page.get_translations(inclusive=True).values_list('id', flat=True)
        page_ids_to_exclude += self.banner_index_page.get_translations(inclusive=True).values_list('id', flat=True)
        page_ids_to_exclude += self.footer_index_page.get_translations(inclusive=True).values_list('id', flat=True)
        page_ids_to_exclude += self.poll_index_page.get_translations(inclusive=True).values_list('id', flat=True)
        page_ids_to_exclude += self.survey_index_page.get_translations(inclusive=True).values_list('id', flat=True)
        page_ids_to_exclude += self.quiz_index_page.get_translations(inclusive=True).values_list('id', flat=True)

        Page.objects.filter(alias_of__isnull=False).exclude(id__in=page_ids_to_exclude).update(live=False)

    def migrate_social_media_links(self):
        self.footer_index_page.refresh_from_db()
        sql = f'select * from core_sitesettings'
        cur = self.db_query(sql)
        for row in cur:
            social_media_links = json.loads(row['social_media_links_on_footer_page'])
            for social_media_link in social_media_links:
                block_value = social_media_link.get('value')
                if block_value:
                    page_link_page_data = {
                        'title': block_value.get('title'),
                        'external_link': block_value.get('link'),
                    }
                    v2_image = self.image_map.get(block_value.get('image'))
                    if v2_image:
                        page_link_page_data.update({'image_icon_id': v2_image.id})

                    page_link_page = models.PageLinkPage(**page_link_page_data)
                    self.footer_index_page.add_child(instance=page_link_page)

    def migrate_page_revisions(self):
        PageRevision.objects.all().delete()
        sql = f"select * " \
              f"from wagtailcore_pagerevision wcpr"
        cur = self.db_query(sql)
        for row in cur:
            v2_page = self.v1_to_v2_page_map.get(row['page_id'])
            if v2_page:
                page_revision = PageRevision.objects.create(
                    page=v2_page,
                    submitted_for_moderation=row['submitted_for_moderation'],
                    created_at=row['created_at'],
                    content_json=row['content_json'],
                    approved_go_live_at=row['approved_go_live_at'],
                )
                V1ToV2ObjectMap.create_map(page_revision, row['id'])
        cur.close()

    def add_polls_from_polls_index_page_to_home_page_featured_content(self):
        self.poll_index_page.refresh_from_db()
        self.home_page.refresh_from_db()
        poll_index_pages = self.poll_index_page.get_translations(inclusive=True)
        for poll_index_page in poll_index_pages:
            home_page = self.home_page.get_translation_or_none(poll_index_page.locale)
            home_featured_content = home_page.home_featured_content.stream_data
            polls = poll_index_page.get_children().live()
            for poll in polls:
                home_featured_content.append({
                    'type': 'embedded_poll',
                    'value': {
                        'direct_display': True,
                        'poll': poll.id,
                    },
                })
            home_page.home_featured_content = json.dumps(home_featured_content)
            home_page.save()

        self.stdout.write('Added polls from poll index page to home page featured content.')

    def add_surveys_from_surveys_index_page_to_home_page_featured_content(self):
        self.survey_index_page.refresh_from_db()
        self.home_page.refresh_from_db()
        survey_index_pages = self.survey_index_page.get_translations(inclusive=True)
        for survey_index_page in survey_index_pages:
            home_page = self.home_page.get_translation_or_none(survey_index_page.locale)
            home_featured_content = home_page.home_featured_content.stream_data
            surveys = survey_index_page.get_children().live()
            for survey in surveys:
                home_featured_content.append({
                    'type': 'embedded_survey',
                    'value': {
                        'direct_display': survey.specific.direct_display,
                        'survey': survey.id,
                    },
                })
            home_page.home_featured_content = json.dumps(home_featured_content)
            home_page.save()

        self.stdout.write('Added surveys from survey index page to home page featured content.')

    def migrate_article_related_sections(self):
        cur = self.db_query('select * from core_articlepagerelatedsections caprs')
        sections = defaultdict(list)
        for row in cur:
            section = self.v1_to_v2_page_map.get(row['section_id'])
            article = self.v1_to_v2_page_map.get(row['page_id'])
            if (not section) or (not article):
                self.post_migration_report_messages['articles_in_related_sections'].append(
                    f"Couldn't find v2 page for v1 section: {row['section_id']} and article: {row['page_id']}"
                )
                continue
            section.refresh_from_db()
            article.refresh_from_db()
            page_link_page = models.PageLinkPage(title=article.title, page=article, live=article.live)
            section.add_child(instance=page_link_page)
            page = Page.objects.get(id=page_link_page.id)
            self.move_page(page_to_move=page, position=0)
            sections[section.id].append(article.title)

        for k, v in sections.items():
            page = Page.objects.get(id=k)
            self.post_migration_report_messages['unordered_related_articles_in_section'].append(
                f"title: {page.title}. URL: {page.full_url}. Admin URL: {self.get_admin_url(page.id)}. "
                f"articles: {', '.join(v)}"
            )

    def move_footers_to_end_of_footer_index_page(self):
        footer_index_pages = self.footer_index_page.get_translations(inclusive=True)
        for footer_index_page in footer_index_pages:
            footer_index_page_children = footer_index_page.get_children()
            articles = footer_index_page_children.exact_type(models.Article)
            for article in articles:
                self.move_page(page_to_move=article, position=footer_index_page_children.count())

    def move_page(self, page_to_move, position):
        parent_page = page_to_move.get_parent()

        # Find page that is already in this position
        position_page = None
        if position is not None:
            try:
                position_page = parent_page.get_children()[int(position)]
            except IndexError:
                pass  # No page in this position

        # Move page

        # any invalid moves *should* be caught by the permission check above,
        # so don't bother to catch InvalidMoveToDescendant

        if position_page:
            # If the page has been moved to the right, insert it to the
            # right. If left, then left.
            old_position = list(parent_page.get_children()).index(page_to_move)
            if int(position) < old_position:
                page_to_move.move(position_page, pos='left')
            elif int(position) > old_position:
                page_to_move.move(position_page, pos='right')
        else:
            # Move page to end
            page_to_move.move(parent_page, pos='last-child')

    def _sort_articles(self):
        pages = models.Section.objects.all().order_by('path')
        for page in pages:
            page.refresh_from_db()
            articles = page.get_children().type(models.Article)
            children_list = []
            for article in articles:
                try:
                    v1_id = V1ToV2ObjectMap.get_v1_id(article.specific, article.id)
                except:
                    continue
                if v1_id:
                    translated_from_page_id = self.page_translation_map.get(v1_id)
                    if translated_from_page_id:
                        v1_id = translated_from_page_id
                    cur = self.db_query(f'select * from wagtailcore_page wcp where id = {v1_id}')
                    v1_row = cur.fetchone()
                    cur.close()
                    setattr(article, 'creation_date', v1_row['first_published_at'])
                else:
                    setattr(article, 'creation_date', None)

                children_list.append(article)

            children_list = sorted(
                children_list, key=lambda x: (x.creation_date is not None, x.creation_date))
            for article in children_list:
                article.refresh_from_db()
                article.move(page, pos='first-child')

    def _sort_sections(self):
        locales = Locale.objects.all()
        for locale in locales:
            pages = models.Section.objects.filter(locale=locale).order_by('path')
            for page in pages:
                page.refresh_from_db()
                try:
                    v1_id = V1ToV2ObjectMap.get_v1_id(page.specific, page.id)
                except:
                    continue

                translated_from_page_id = self.page_translation_map.get(v1_id)
                if not translated_from_page_id:
                    continue

                translated_from_page = self.v1_to_v2_page_map.get(translated_from_page_id)
                if not translated_from_page:
                    continue

                translated_from_page.refresh_from_db()

                translated_from_sub_sections = translated_from_page.get_children().type(models.Section)
                translated_sub_sections = page.get_children().type(models.Section)

                if translated_sub_sections:
                    index_to_move = list(page.get_children()).index(translated_sub_sections.first())
                    for child in translated_from_sub_sections:
                        child.refresh_from_db()
                        translated_sub_section = child.get_translation_or_none(locale)
                        if translated_sub_section:
                            self.move_page(page_to_move=translated_sub_section, position=index_to_move)
                            index_to_move += 1

    def sort_pages(self):
        if self.sort != 'type1':
            return

        self._sort_sections()
        self._sort_articles()

        self.stdout.write('Pages sorted.')

    def populate_registration_survey_translations(self):
        with open(f'{settings.BASE_DIR}/iogt_content_migration/files/registration_survey_translations.csv',
                  newline='') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                str_key = self._get_iso_locale(row.pop('str'))
                self.registration_survey_translations[str_key] = row

    def translate_default_survey_submit_button_text(self):
        surveys = Survey.objects.all()
        for survey in surveys:
            if survey.submit_button_text == 'Submit':
                # Technically, someone could have manually put 'Submit' on a non-English button,
                # which we would now translate even though we shouldn't.
                # This is quite unlikely though.
                submit_button_text = self.registration_survey_translations['submit_button_text'].get(survey.locale.language_code)
                if not submit_button_text:
                    self.post_migration_report_messages['untranslated_survey_button'].append(
                            f'title: {survey.title}. URL: {survey.full_url}. '
                            f'Admin URL: {self.get_admin_url(survey.id)}.'
                        )
                if submit_button_text and len(submit_button_text) > 40:
                    # This should never happen in practice as we provide submit_button_text
                    self.stdout.write(f"Truncated default submit button text, title={survey.title}")

                survey.submit_button_text = submit_button_text[:40] if submit_button_text else 'Submit'
                survey.save()

    def migrate_post_registration_survey(self):
        sql = 'select * from profiles_userprofilessettings pups ' \
              'inner join wagtailcore_site ws on pups.site_id = ws.id ' \
              'where is_default_site = true'
        cur = self.db_query(sql)
        row = cur.fetchone()

        survey = Survey(
            title='Registration Survey', live=True, allow_multiple_submissions=True,
            allow_anonymous_submissions=False, submit_button_text='Register')

        self.survey_index_page.add_child(instance=survey)

        for (should_add_field_key, translation_key, is_required_key, field_type, admin_label) in [
            ('activate_dob', 'dob', 'dob_required', 'date', 'date_of_birth'),
            ('activate_gender', 'gender', 'gender_required', 'singleline', 'gender'),
            ('activate_location', 'location', 'location_required', 'singleline', 'location'),
            ('activate_education_level', 'education_level', 'activate_education_level_required', 'singleline',
             'education_level'),
            ('show_mobile_number_field', 'mobile_number', 'mobile_number_required', 'singleline', 'mobile_number'),
            ('show_email_field', 'email_address', 'email_required', 'email', 'email'),
        ]:
            if row[should_add_field_key]:
                SurveyFormField.objects.create(
                    page=survey,
                    label=self.registration_survey_translations[translation_key]['en'],
                    required=bool(row[is_required_key]),
                    field_type=field_type,
                    admin_label=admin_label,
                    help_text=self.registration_survey_translations[f'{translation_key}_helptext']['en']
                )

        self.stdout.write('Successfully migrated post registration survey')

        default_site_settings = models.SiteSettings.get_for_default_site()
        default_site_settings.registration_survey = survey
        default_site_settings.save()

        for locale in Locale.objects.all():
            try:
                self.translate_page(locale=locale, page=survey)
                translated_survey = survey.get_translation_or_none(locale)
            except Exception as e:
                self.post_migration_report_messages['registration_survey'].append(
                    f"Unable to translate survey, title={survey.title} to locale={locale}"
                )
                continue

            submit_button_text = self.registration_survey_translations['register_button_text'].get(locale.language_code)
            if not submit_button_text:
                self.post_migration_report_messages['registration_survey_translation_not_found'].append(
                    f'No translation for submit button of registration survey to locale: {locale}'
                )
            if submit_button_text and len(submit_button_text) > 40:
                # This should never happen in practice as we provide submit_button_text
                self.stdout.write(f"Truncated survey submit button text, title={translated_survey.title}")

            translated_survey.submit_button_text = submit_button_text[:40] if submit_button_text else 'Register'
            translated_survey.save()
            if translated_survey:
                for (admin_label, label_identifier) in [
                    ('date_of_birth', 'dob'),
                    ('gender', 'gender'),
                    ('location', 'location'),
                    ('mobile_number', 'mobile_number'),
                    ('education_level', 'education_level'),
                    ('email', 'email_address')
                ]:
                    try:
                        field = SurveyFormField.objects.get(page=translated_survey, admin_label=admin_label)
                    except SurveyFormField.DoesNotExist:
                        # This field is not marked as required in the registration survey
                        continue
                    try:
                        field.label = self.registration_survey_translations[label_identifier][locale.language_code]
                        field.help_text = self.registration_survey_translations[
                            f'{label_identifier}_helptext'][locale.language_code]
                    except KeyError:
                        self.post_migration_report_messages['registration_survey_translation_not_found'].append(
                            f'Incomplete translation for registration survey to locale: {locale}'
                        )
                        break
                    field.save()

        self.post_migration_report_messages['other'].append(
            'Title of registration survey (Pages > Internet of Good Things [Language] > Surveys > Registration Survey) '
            'has not been translated for any language.'
        )

    def get_admin_url(self, id):
        site = Site.objects.filter(is_default_site=True).first()
        return f"{site.root_url}{reverse('wagtailadmin_pages:edit', args=(id,))}"

    def print_post_migration_report(self):
        self.stdout.write(self.style.ERROR('====================='))
        self.stdout.write(self.style.ERROR('POST MIGRATION REPORT'))
        self.stdout.write(self.style.ERROR('====================='))

        for k, v in self.post_migration_report_messages.items():
            self.stdout.write(self.style.ERROR(f"===> {k.replace('_', ' ').upper()}"))
            self.stdout.write(self.style.ERROR('\n'.join(v)))
