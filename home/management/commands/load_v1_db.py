from django.core.management.base import BaseCommand
from wagtail.core.models import Page, Site
import home.models as models
import psycopg2
import psycopg2.extras
import json

class Command(BaseCommand):

    def add_arguments(self, parser):
        parser.add_argument(
            '--host',
            default='0.0.0.0',
            help='IoGT V1 database host'
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

    def handle(self, *args, **options):
        self.clear()
        self.stdout.write('Existing site structure cleared')

        root = Page.get_first_root_node()
        self.db_connect(options)
        self.migrate(root)

    def clear(self):
        models.Article.objects.all().delete()
        models.Section.objects.all().delete()
        models.HomePage.objects.all().delete()
        Site.objects.all().delete()

    def db_connect(self, options):
        connection_string = self.create_connection_string(options)
        self.stdout.write(f'DB connection string created, string={connection_string}')
        self.v1_conn = psycopg2.connect(connection_string)
        self.stdout.write('Connected to v1 DB')

    def __del__(self):
        self.v1_conn.close()
        self.stdout.write('Closed connection to v1 DB')

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
        home = self.create_home_page(root)
        self.migrate_sections(home)
        self.migrate_articles(home)
        self.fix_page_tree_hack(home)

    def create_home_page(self, root):
        cur = self.db_query('select * from core_main main join wagtailcore_page page on main.page_ptr_id = page.id')
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
                is_default_site=v1_site['is_default_site'],
                site_name=v1_site['site_name'] if v1_site['site_name'] else 'Internet of Good Things',
            )
        else:
            raise Exception('Could not find site in v1 DB')
        return home

    def migrate_sections(self, home):
        cur = self.db_query('select * from core_sectionpage csp join wagtailcore_page wcp on csp.page_ptr_id  = wcp.id order by wcp.path')
        for row in cur:
            self.create_section(home, row)
        cur.close()

    # Hack to make pages appear under the home page in Wagtail Admin. Not sure
    # why this is necessary, nor why it works. Better solutions are welcome.
    def fix_page_tree_hack(self, home):
        try:
            home.add_child(instance=models.Section(title='temp'))
        except:
            self.stdout.write('Page tree hack applied')

    def create_section(self, home, row):
        section = models.Section(
            title=row['title'],
            draft_title=row['draft_title'],
            show_in_menus=True,
            color='1CABE2',
            slug=row['slug'],
            path=home.path + row['path'][12:],
            depth=row['depth']-1,
            numchild=row['numchild'],
            live=row['live'],
        )
        section.save()
        self.stdout.write(f"saved section, title={section.title}")

    def migrate_articles(self, home):
        cur = self.db_query("select * from core_articlepage cap join wagtailcore_page wcp on cap.page_ptr_id  = wcp.id where wcp.path like '000100010002%' order by wcp.path")
        for row in cur:
            self.create_article(home, row)
        cur.close()

    def create_article(self, home, row):
        article = models.Article(
            title=row['title'],
            draft_title=row['draft_title'],
            slug=row['slug'],
            path=home.path + row['path'][12:],
            depth=row['depth']-1,
            numchild=row['numchild'],
            live=row['live'],
            body=self.map_article_body(row['body']),
        )
        article.save()
        self.stdout.write(f"saved article, title={article.title}")

    def map_article_body(self, v1_body):
        v2_body = json.loads(v1_body)
        for block in v2_body:
            if block['type'] == 'paragraph':
                block['type'] = 'markdown'
        return json.dumps(v2_body)
