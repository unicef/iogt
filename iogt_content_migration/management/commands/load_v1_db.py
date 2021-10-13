from pathlib import Path

from django.core.files import File
from django.core.management.base import BaseCommand
from wagtail.core.models import Page, Site, Locale, Collection, PageRevision
from django.core.files.images import ImageFile
from wagtail.documents.models import Document
from wagtail.images.models import Image
from wagtail_localize.models import Translation
from wagtail_localize.views.submit_translations import TranslationCreator
from wagtailmedia.models import Media

import home.models as models
from home.models import V1ToV2ObjectMap
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

        parser.add_argument(
            '--delete-users',
            action='store_true',
            help='Delete existing Users and their associated data. Use carefully'
        )

    def handle(self, *args, **options):
        self.db_connect(options)
        self.media_dir = options.get('media_dir')
        self.skip_locales = options.get('skip_locales')

        self.collection_map = {}
        self.document_map = {}
        self.media_map = {}
        self.image_map = {}
        self.page_translation_map = {}
        self.v1_to_v2_page_map = {}
        self.pages_pending_links = {
            'articles': {},
            'surveys': {},
            'banners': {},
        }

        self.clear()
        self.stdout.write('Existing site structure cleared')

        root = Page.get_first_root_node()
        self.migrate(root)

    def clear(self):
        PageRevision.objects.all().delete()
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
        self.load_page_translation_map()
        home = self.create_home_page(root)
        self.create_index_pages(home)
        self.migrate_sections()
        self.migrate_articles()
        self.migrate_footers()
        self.migrate_polls()
        self.migrate_surveys()
        self.translate_home_pages()
        self.migrate_banners()
        self.fix_pending_links_for_pages()
        Page.fix_tree()
        self.migrate_recommended_articles_for_article()
        self.migrate_featured_articles_for_section()
        self.migrate_featured_articles_for_homepage()
        self.stop_translations()

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
                slug=main['slug'],
                live=main['live'],
                locked=main['locked'],
                go_live_at=main['go_live_at'],
                expire_at=main['expire_at'],
                first_published_at=main['first_published_at'],
                last_published_at=main['last_published_at'],
                search_description=main['search_description'],
                seo_title=main['seo_title'],
            )
            root.add_child(instance=home)
            V1ToV2ObjectMap.create_map(content_object=home, v1_object_id=main['page_ptr_id'])
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
        self.section_index_page = models.SectionIndexPage(title='Sections')
        homepage.add_child(instance=self.section_index_page)

        self.banner_index_page = models.BannerIndexPage(title='Banners')
        homepage.add_child(instance=self.banner_index_page)

        self.footer_index_page = models.FooterIndexPage(title='Footers')
        homepage.add_child(instance=self.footer_index_page)

        self.poll_index_page = PollIndexPage(title='Polls')
        homepage.add_child(instance=self.poll_index_page)

        self.survey_index_page = SurveyIndexPage(title='Surveys')
        homepage.add_child(instance=self.survey_index_page)

        self.quiz_index_page = QuizIndexPage(title='Quizzes')
        homepage.add_child(instance=self.quiz_index_page)

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
                self.stdout.write(f'Document file path not found, id={row["id"]}')
                continue

            file = self.open_file(row['file'])
            if file:
                document = Document.objects.create(
                    title=row['title'],
                    file=File(file),
                    created_at=row['created_at'],
                    collection=self.collection_map.get(row['collection_id']),
                )
                V1ToV2ObjectMap.create_map(content_object=document, v1_object_id=row['id'])
                tags = self.find_tags(content_type, row['id'])
                if tags:
                    document.tags.add(*tags)
                self.document_map.update({ row['id']: document })
        cur.close()
        self.stdout.write('Documents migrated')

    def migrate_media(self):
        cur = self.db_query('select * from core_molomedia')
        content_type = self.find_content_type_id('core', 'molomedia')
        for row in cur:
            if not row['file']:
                self.stdout.write(f'Media file path not found, id={row["id"]}')
                continue

            file = self.open_file(row['file'])
            if file:
                thumbnail = self.open_file(row['thumbnail'])
                media = Media.objects.create(
                    title=row['title'],
                    file=File(file),
                    type=row['type'],
                    duration=row['duration'],
                    thumbnail=File(thumbnail) if thumbnail else None,
                    created_at=row['created_at'],
                    collection=self.collection_map.get(row['collection_id']),
                )
                V1ToV2ObjectMap.create_map(content_object=media, v1_object_id=row['id'])
                tags = self.find_tags(content_type, row['id'])
                if tags:
                    media.tags.add(*tags)
                self.media_map.update({ row['id']: media })
        cur.close()
        self.stdout.write('Media migrated')

    def migrate_images(self):
        cur = self.db_query('select * from wagtailimages_image')
        content_type = self.find_content_type_id('wagtailimages', 'image')
        for row in cur:
            if not row['file']:
                self.stdout.write(f'Image file path not found, id={row["id"]}')
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
            self.stdout.write(f"File not found: {file_path}")

    def find_tags(self, content_type, object_id):
        tags_query = 'select t.name from taggit_tag t join taggit_taggeditem ti on t.id = ti.tag_id where ti.content_type_id = {} and ti.object_id = {}'
        cur = self.db_query(tags_query.format(content_type, object_id))
        tags = [tag['name'] for tag in cur]
        cur.close()
        return tags

    def migrate_sections(self):
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
                self.create_section(row)
        else:
            for row in section_page_translations:
                section = self.v1_to_v2_page_map.get(self.page_translation_map[row['page_ptr_id']])
                locale, __ = Locale.objects.get_or_create(language_code=self._get_iso_locale(row['locale']))

                self.translate_page(locale=locale, page=section)

                translated_section = section.get_translation_or_none(locale)
                if translated_section:
                    translated_section.lead_image = self.image_map.get(row['image_id'])
                    translated_section.title = row['title']
                    translated_section.draft_title = row['draft_title']
                    translated_section.live = row['live']
                    translated_section.locked = row['locked']
                    translated_section.go_live_at = row['go_live_at']
                    translated_section.expire_at = row['expire_at']
                    translated_section.first_published_at = row['first_published_at']
                    translated_section.last_published_at = row['last_published_at']
                    translated_section.search_description = row['search_description']
                    translated_section.seo_title = row['seo_title']
                    translated_section.font_color = self.get_color_hex(row['extra_style_hints'])
                    translated_section.save()
                    content_type = self.find_content_type_id('core', 'sectionpage')
                    tags = self.find_tags(content_type, row['id'])
                    if tags:
                        translated_section.tags.add(*tags)
                    V1ToV2ObjectMap.create_map(content_object=translated_section, v1_object_id=row['page_ptr_id'])

                    self.v1_to_v2_page_map.update({
                        row['page_ptr_id']: translated_section
                    })

                self.stdout.write(f"Translated section, title={row['title']}")
        cur.close()

    def create_section(self, row):
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
            search_description=row['search_description'],
            seo_title=row['seo_title'],
            font_color=self.get_color_hex(row['extra_style_hints']),
        )
        section.save()
        content_type = self.find_content_type_id('core', 'sectionpage')
        tags = self.find_tags(content_type, row['id'])
        if tags:
            section.tags.add(*tags)
        V1ToV2ObjectMap.create_map(content_object=section, v1_object_id=row['page_ptr_id'])

        self.v1_to_v2_page_map.update({
            row['page_ptr_id']: section
        })
        self.stdout.write(f"saved section, title={section.title}")

    def migrate_articles(self):
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
                self.create_article(row)
        else:
            for row in article_page_translations:
                article = self.v1_to_v2_page_map.get(self.page_translation_map[row['page_ptr_id']])
                locale, __ = Locale.objects.get_or_create(language_code=self._get_iso_locale(row['locale']))

                self.translate_page(locale=locale, page=article)

                translated_article = article.get_translation_or_none(locale)
                if translated_article:
                    translated_article.lead_image = self.image_map.get(row['image_id'])
                    translated_article.title = row['title']
                    translated_article.draft_title = row['draft_title']
                    translated_article.live = row['live']
                    translated_article.body = self.map_article_body(row)
                    translated_article.locked = row['locked']
                    translated_article.go_live_at = row['go_live_at']
                    translated_article.expire_at = row['expire_at']
                    translated_article.first_published_at = row['first_published_at']
                    translated_article.last_published_at = row['last_published_at']
                    translated_article.search_description = row['search_description']
                    translated_article.seo_title = row['seo_title']
                    translated_article.index_page_description = row['subtitle']
                    translated_article.save()
                    content_type = self.find_content_type_id('core', 'articlepage')
                    tags = self.find_tags(content_type, row['id'])
                    if tags:
                        translated_article.tags.add(*tags)
                    V1ToV2ObjectMap.create_map(content_object=translated_article, v1_object_id=row['page_ptr_id'])

                    self.v1_to_v2_page_map.update({
                        row['page_ptr_id']: translated_article
                    })

                self.stdout.write(f"Translated article, title={row['title']}")
        cur.close()

    def create_article(self, row):
        article = models.Article(
            lead_image=self.image_map.get(row['image_id']),
            title=row['title'],
            draft_title=row['draft_title'],
            slug=row['slug'],
            path=self.section_index_page.path + row['path'][12:],
            depth=row['depth'],
            numchild=row['numchild'],
            live=row['live'],
            body=self.map_article_body(row),
            locked=row['locked'],
            go_live_at=row['go_live_at'],
            expire_at=row['expire_at'],
            first_published_at=row['first_published_at'],
            last_published_at=row['last_published_at'],
            allow_comments=True if row['commenting_state'] == 'O' else False,
            search_description=row['search_description'],
            seo_title=row['seo_title'],
            index_page_description=row['subtitle'],
        )
        try:
            article.save()
            content_type = self.find_content_type_id('core', 'articlepage')
            tags = self.find_tags(content_type, row['id'])
            if tags:
                article.tags.add(*tags)
            V1ToV2ObjectMap.create_map(content_object=article, v1_object_id=row['page_ptr_id'])
            self.v1_to_v2_page_map.update({
                row['page_ptr_id']: article
            })
        except Page.DoesNotExist:
            self.stdout.write(f"Skipping page with missing parent: title={row['title']}")
            return
        self.stdout.write(f"saved article, title={article.title}")

    def _map_body(self, type_, row, v1_body):
        v2_body = []
        for block in v1_body:
            if block['type'] in ['paragraph', 'html']:
                block['type'] = 'markdown'
                v2_body.append(block)
            elif block['type'] == 'richtext':
                block['type'] = 'paragraph'
                v2_body.append(block)
            elif block['type'] in ['heading', 'list', 'numbered_list']:
                v2_body.append(block)
            elif block['type'] == 'image':
                image = self.image_map.get(block['value'])
                if image:
                    block['value'] = image.id
                else:
                    self.stdout.write(f"Article (title={row['title']}) has image with invalid id {block['value']}")
                    block['value'] = None
                v2_body.append(block)
            elif block['type'] == 'media':
                media = self.media_map.get(block['value'])
                if media:
                    block['value'] = media.id
                else:
                    self.stdout.write(f"Article (title={row['title']}) has media with invalid id {block['value']}")
                    block['value'] = None
                v2_body.append(block)
            elif block['type'] == 'page':
                page = self.v1_to_v2_page_map.get(block['value'])
                if page:
                    v2_body.append(
                        {
                            'type': 'page_button',
                            'value': {
                                'page': page.id
                            },
                        }
                    )
                else:
                    self.pages_pending_links[type_].update({row['page_ptr_id']: row})
                    self.stdout.write(f'Unable to attach v2 page for {type_[:-1]}, title={row["title"]}')

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
                self.create_banner(row)
        else:
            for row in banner_page_translations:
                banner = self.v1_to_v2_page_map.get(self.page_translation_map[row['page_ptr_id']])
                locale, __ = Locale.objects.get_or_create(language_code=self._get_iso_locale(row['locale']))

                try:
                    self.translate_page(locale=locale, page=banner)
                except:
                    continue

                translated_banner = banner.get_translation_or_none(locale)
                if translated_banner:
                    translated_banner.banner_image = self.image_map.get(row['banner_id'])
                    translated_banner.banner_link_page = self.map_banner_page(row)
                    translated_banner.title = row['title']
                    translated_banner.draft_title = row['draft_title']
                    translated_banner.live = row['live']
                    translated_banner.locked = row['locked']
                    translated_banner.go_live_at = row['go_live_at']
                    translated_banner.expire_at = row['expire_at']
                    translated_banner.first_published_at = row['first_published_at']
                    translated_banner.last_published_at = row['last_published_at']
                    translated_banner.search_description = row['search_description']
                    translated_banner.seo_title = row['seo_title']
                    translated_banner.save()
                    V1ToV2ObjectMap.create_map(content_object=translated_banner, v1_object_id=row['page_ptr_id'])

                    self.v1_to_v2_page_map.update({
                        row['page_ptr_id']: translated_banner
                    })

                self.stdout.write(f"Translated banner, title={row['title']}")
        cur.close()

    def create_banner(self, row):
        banner = models.BannerPage(
            banner_image=self.image_map.get(row['banner_id']),
            banner_link_page=self.map_banner_page(row),
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
        )
        banner.save()
        V1ToV2ObjectMap.create_map(content_object=banner, v1_object_id=row['page_ptr_id'])
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
                self.pages_pending_links['banners'].update({row['page_ptr_id']: row})
                self.stdout.write(f'Unable to attach v2 page for banner, title={row["title"]}')

        return v2_page

    def migrate_footers(self):
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
                self.create_footer(row)
        else:
            for row in footer_page_translations:
                footer = self.v1_to_v2_page_map.get(self.page_translation_map[row['page_ptr_id']])
                locale, __ = Locale.objects.get_or_create(language_code=self._get_iso_locale(row['locale']))

                self.translate_page(locale=locale, page=footer)

                translated_footer = footer.get_translation_or_none(locale)
                if translated_footer:
                    translated_footer.lead_image = self.image_map.get(row['image_id'])
                    translated_footer.title = row['title']
                    translated_footer.draft_title = row['draft_title']
                    translated_footer.live = row['live']
                    translated_footer.body = self.map_article_body(row)
                    translated_footer.locked = row['locked']
                    translated_footer.go_live_at = row['go_live_at']
                    translated_footer.expire_at = row['expire_at']
                    translated_footer.first_published_at = row['first_published_at']
                    translated_footer.last_published_at = row['last_published_at']
                    translated_footer.search_description = row['search_description']
                    translated_footer.seo_title = row['seo_title']
                    translated_footer.save()
                    V1ToV2ObjectMap.create_map(content_object=translated_footer, v1_object_id=row['page_ptr_id'])

                    self.v1_to_v2_page_map.update({
                        row['page_ptr_id']: translated_footer
                    })

                self.stdout.write(f"Translated footer, title={row['title']}")
        cur.close()

    def create_footer(self, row):
        footer = models.FooterPage(
            lead_image=self.image_map.get(row['image_id']),
            title=row['title'],
            draft_title=row['draft_title'],
            slug=row['slug'],
            path=self.footer_index_page.path + row['path'][12:],
            depth=row['depth'],
            numchild=row['numchild'],
            live=row['live'],
            body=self.map_article_body(row),
            locked=row['locked'],
            go_live_at=row['go_live_at'],
            expire_at=row['expire_at'],
            first_published_at=row['first_published_at'],
            last_published_at=row['last_published_at'],
            search_description=row['search_description'],
            seo_title=row['seo_title'],
        )
        footer.save()
        V1ToV2ObjectMap.create_map(content_object=footer, v1_object_id=row['page_ptr_id'])
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
        sql = "select * from polls_pollsindexpage ppip, wagtailcore_page wcp where ppip.page_ptr_id = wcp.id"
        cur = self.db_query(sql)
        v1_poll_index_page = cur.fetchone()
        cur.close()

        self._migrate_polls(v1_poll_index_page, self.poll_index_page)

        sql = "select * from core_sectionindexpage csip, wagtailcore_page wcp where csip.page_ptr_id = wcp.id"
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
              f"and wcp.path like '{v1_index_page['path']}%' "
        if self.skip_locales:
            sql += " and locale = 'en' "
        sql += 'order by wcp.path'
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
                    self.stdout.write(f"Unable to translate poll, title={row['title']}")
                    continue

                translated_poll = poll.get_translation_or_none(locale)
                if translated_poll:
                    translated_poll.title = row['title']
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
                    translated_poll.save()
                    V1ToV2ObjectMap.create_map(content_object=translated_poll, v1_object_id=row['page_ptr_id'])

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
        )
        try:
            poll.save()
            V1ToV2ObjectMap.create_map(content_object=poll, v1_object_id=row['page_ptr_id'])
        except Exception as e:
            self.stdout.write(f"Unable to save poll, title={row['title']}")
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
            self.stdout.write(f'Unable to determine field type for poll={poll_row["title"]}.')
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
        sql = "select * from surveys_surveysindexpage ssip, wagtailcore_page wcp where ssip.page_ptr_id = wcp.id"
        cur = self.db_query(sql)
        v1_survey_index_page = cur.fetchone()
        cur.close()

        self._migrate_surveys(v1_survey_index_page, self.survey_index_page)

        sql = "select * from core_sectionindexpage csip, wagtailcore_page wcp where csip.page_ptr_id = wcp.id"
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
              f"and wcp.path like '{v1_index_page['path']}%' "
        if self.skip_locales:
            sql += "and locale = 'en' "
        sql += 'order by wcp.path'
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
                    self.stdout.write(f"Unable to translate survey, title={row['title']}")
                    continue

                translated_survey = survey.get_translation_or_none(locale)
                if translated_survey:
                    translated_survey.title = row['title']
                    translated_survey.draft_title = row['draft_title']
                    translated_survey.live = row['live']
                    translated_survey.description = self.map_survey_description(row)
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
                    translated_survey.save()

                    if row['submit_text'] and len(row['submit_text']) > 40:
                        self.stdout.write(f"Truncated survey submit button text, title={row['title']}")

                    V1ToV2ObjectMap.create_map(content_object=translated_survey, v1_object_id=row['page_ptr_id'])

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
            description=self.map_survey_description(row),
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
        )

        try:
            survey.save()
            if row['submit_text'] and len(row['submit_text']) > 40:
                self.stdout.write(f"Truncated survey submit button text, title={row['title']}")
            V1ToV2ObjectMap.create_map(content_object=survey, v1_object_id=row['page_ptr_id'])
        except Exception as e:
            self.stdout.write(f"Unable to save survey, title={row['title']}")
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
              f'and stc.page_id = {row["page_ptr_id"]}'

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
                self.stdout.write(f'skip logic without multi step')
            self.stdout.write(f"saved survey question, label={row['label']}")

    def _get_iso_locale(self, locale):
        iso_locales_map = {
            'sho': 'sn',
            'ch': 'ny',
        }

        return iso_locales_map.get(locale, locale)

    def translate_home_pages(self):
        eng_home_page = models.HomePage.objects.get(locale__language_code='en')
        locales = Locale.objects.exclude(language_code='en')
        for locale in locales:
            self.translate_page(locale=locale, page=eng_home_page)

    def migrate_recommended_articles_for_article(self):
        article_cur = self.db_query(f'select DISTINCT page_id from core_articlepagerecommendedsections')
        for article_row in article_cur:
            v1_article_id = article_row['page_id']
            v2_article = self.v1_to_v2_page_map.get(v1_article_id)
            if v2_article:
                cur = self.db_query(f'select * from core_articlepagerecommendedsections where page_id = {v1_article_id} and recommended_article_id is not null')
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

    def migrate_featured_articles_for_section(self):
        cur = self.db_query(f'select * from core_articlepage where featured_in_section = true')
        for row in cur:
            v2_article = self.v1_to_v2_page_map.get(row['page_ptr_id'])
            if v2_article:
                section = v2_article.get_parent()
                if isinstance(section.specific, models.Section):
                    models.FeaturedContent.objects.create(source=section, content=v2_article)
        cur.close()
        self.stdout.write('Articles featured in sections migrated')

    def migrate_featured_articles_for_homepage(self):
        cur = self.db_query(f'select * from core_articlepage where featured_in_homepage = true')
        for row in cur:
            v2_article = self.v1_to_v2_page_map.get(row['page_ptr_id'])
            if v2_article:
                home_page = v2_article.get_ancestors().exact_type(models.HomePage).first().specific
                home_featured_content = []
                for hfc in home_page.home_featured_content:
                    home_featured_content.append({
                        'type': 'article',
                        'value': hfc.value.id,
                    })
                home_featured_content.append({'type': 'article', 'value': v2_article.id})
                home_page.home_featured_content = json.dumps(home_featured_content)
                home_page.save()
        cur.close()
        self.stdout.write('Articles featured in home page migrated')

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

    def fix_pending_links_for_pages(self):
        for k, v in self.pages_pending_links['articles'].items():
            v2_article = self.v1_to_v2_page_map.get(k)
            if v2_article:
                v2_article.body = self.map_article_body(v)
                v2_article.save()

        for k, v in self.pages_pending_links['surveys'].items():
            v2_survey = self.v1_to_v2_page_map.get(k)
            if v2_survey:
                v2_survey.description = self.map_survey_description(v)
                v2_survey.save()

        for k, v in self.pages_pending_links['banners'].items():
            v2_banner = self.v1_to_v2_page_map.get(k)
            if v2_banner:
                v2_banner.banner_link_page = self.map_banner_page(v)
                v2_banner.save()

        self.stdout.write('Fixed pending links for pages.')
