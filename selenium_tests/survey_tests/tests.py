import time
from django.test import LiveServerTestCase
from selenium import webdriver
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.webdriver.support.ui import Select
from selenium.webdriver.chrome.options import Options as ChromeOptions
from home.factories import SurveyFactory, SectionFactory
from home.models import HomePage
from iogt_users.factories import AdminUserFactory
from comments.models import CommentStatus
from django.conf import settings
from django.core.management import execute_from_command_line
from wagtail.core.models import Site, Page
from questionnaires.models import SurveyFormField
from django.contrib.contenttypes.models import ContentType
from wagtail.images.models import Image
import home.models as models
from wagtail.core.models import Site, Locale
from django.core.files import File
from pathlib import Path
from wagtailmenus.models import FlatMenu
from wagtailsvg.models import Svg
from home.models import IogtFlatMenuItem

class MySeleniumTests(LiveServerTestCase):
    serialized_rollback = True
    host = 'django'
    port = 9000

    @classmethod
    def setUpClass(cls):
        options = ChromeOptions()
        options.add_argument('--ignore-ssl-errors=yes')
        options.add_argument('--ignore-certificate-errors')
        # options.add_argument("--window-size=1920,1080")
        options.add_argument("--start-maximized")
        # options.add_argument("--headless")
        cls.selenium = webdriver.Remote(
            command_executor='http://selenium-hub:4444/wd/hub',
            desired_capabilities=DesiredCapabilities.CHROME,
            options=options
        )
        cls.selenium.implicitly_wait(5)
        super(MySeleniumTests, cls).setUpClass()

    @classmethod
    def tearDownClass(cls):
        cls.selenium.quit()
        super(MySeleniumTests, cls).tearDownClass()

    def setUp(self):

        execute_from_command_line(['manage.py', 'migrate'])

        print("Set up")

        models.MiscellaneousIndexPage.objects.all().delete()
        models.BannerIndexPage.objects.all().delete()
        models.Article.objects.all().delete()
        models.Section.objects.all().delete()
        models.SectionIndexPage.objects.all().delete()
        Image.objects.all().delete()
        Page.objects.filter(id=2).delete()

        homepage_content_type, __ = ContentType.objects.get_or_create(
            model='homepage', app_label='home')

        homepage, __ = HomePage.objects.update_or_create(slug='home', defaults={
            'title': "Home",
            'draft_title': "Home",
            'content_type': homepage_content_type,
            'path': '00010002',
            'depth': 2,
            'numchild': 0,
            'url_path': '/home_new/',
            'show_in_menus': True,
        })

        Site.objects.get_or_create(hostname='localhost', defaults={
            'root_page': homepage,
            'is_default_site': True,
        })

        site = Site.objects.get(is_default_site=True)
        if not site:
            self.stdout.write(self.style.SUCCESS('Default site not found.'))

        locales = Locale.objects.all()
        file = File(open(Path(settings.BASE_DIR) / 'iogt/static/icons/burger.svg'), name='burger.svg')
        icon = Svg.objects.create(title='burger', file=file)
        for locale in locales:
            menu, __ = FlatMenu.objects.get_or_create(handle=f'{locale.language_code}_menu_live', defaults={
                'title': f'{locale.language_code} main menu',
                'site': site,
                'heading': 'Main Menu',
            })
            IogtFlatMenuItem.objects.get_or_create(link_url='#menu', menu=menu, defaults={
                'link_text': 'Menu',
                'icon': icon,
                'display_only_in_single_column_view': True,
            })

        self.user = AdminUserFactory()
        self.home_page = homepage
        self.section01 = SectionFactory.build(
            owner=self.user,            
        )
        self.survey01 = SurveyFactory.build(
            owner=self.user,            
        )
        self.home_page.add_child(instance=self.section01)
        self.section01.add_child(instance=self.survey01)

        SurveyFormField.objects.create(
            page=self.survey01, 
            sort_order=0,
            required = True,
            choices = "A|B|C", 
            label='Question 1', 
            default_value='',  
            field_type='checkboxes',
            admin_label='Q1',            
        )

        SurveyFormField.objects.create(
            page=self.survey01, 
            sort_order=1,
            required = True,
            choices = "blah1|blah2|blah3", 
            label='Question 2', 
            default_value='',  
            field_type='dropdown',
            admin_label='Q2',            
        )
        
    def test_login(self):
        self.selenium.get('%s%s' % (self.live_server_url, '/accounts/login/'))
        time.sleep(2)
        username_input = self.selenium.find_element_by_name("login")
        username_input.send_keys(self.user.username)
        time.sleep(2)
        password_input = self.selenium.find_element_by_name("password")
        password_input.send_keys('test@123')
        time.sleep(2)
        self.selenium.find_element_by_xpath('//button[@type="submit"]').click()
        body_text = self.selenium.find_element_by_tag_name('body').text
        assert self.user.username in body_text   

    def test_survey(self):   
        self.selenium.get('%s%s' % (self.live_server_url, '/section0/survey0/'))
        time.sleep(2)
        self.selenium.find_element_by_xpath('//input[@value="A"]').click()
        time.sleep(2)
        select = Select(self.selenium.find_element_by_name("question_2"))
        select.select_by_visible_text("blah3")
        print(select.first_selected_option)
        assert 'blah3' in select.first_selected_option.text
        time.sleep(2)
        self.selenium.find_element_by_xpath('//button[@type="submit"]').click()
        time.sleep(2)
        
     
        
        
        
