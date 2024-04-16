import uuid
from django.contrib.auth import get_user_model
import requests
from wagtail.models import Page

from interactive.models import InteractivePage
from interactive.shortcode import Shortcode


class RapidProApiService(object):
    def get_user_identifier(self, request):
        if not request.session.session_key:
            request.session.save()

        user_uuid = request.session.setdefault('interactive_uuid', str(uuid.uuid4()))
 
        # Get the authenticated user
        user = request.user

        # If the user is authenticated and has no 'interactive_uuid' set, update it
        if user.is_authenticated:
            if user.interactive_uuid:
                user_uuid = user.interactive_uuid
            else:
                user_model = get_user_model()
                user.interactive_uuid = user_uuid
                user_model.objects.filter(pk=user.pk).update(interactive_uuid=user_uuid)

        return user_uuid
    
    def send_message(self, data=None, slug=None):
        # TODO: optimize dynamic url allocation............
        core_page_id = Page.objects.filter(slug=slug).first().id
        interactive_page = InteractivePage.objects.filter(page_ptr_id=core_page_id).first()
        url = interactive_page.channel.request_url

        try:
            response = requests.post(url=url, data=data)
            response.raise_for_status()
            return response
        except requests.exceptions.RequestException as e:
            return None

class ShortCodeService:
    # def __init__(self):
    #     self.register_shortcode()
        
    def register_shortcodes(self):
        shortcode_service = Shortcode()
        shortcode_service.add_shortcode('insert_message', self.message_callback)
        shortcode_service.add_shortcode('insert_button', self.button_callback)
        shortcode_service.add_shortcode('insert_form_field', self.form_callback)
        shortcode_service.add_shortcode('insert_image', self.image_callback)
        # shortcode_service.add_shortcode('insert_attachment_image', attachment_callback)
        shortcode_service.add_shortcode('insert_header', self.header_callback)
        shortcode_service.add_shortcode('insert_navbar', self.navbar_callback)
        shortcode_service.add_shortcode('insert_html', self.html_callback)
        shortcode_service.add_shortcode('insert_bg_color', self.header_callback)
      
    def apply_shortcode(self, content):
        shortcode_service = Shortcode()
        
        shortcode_service.add_shortcode('insert_message', self.message_callback)
        shortcode_service.add_shortcode('insert_button', self.button_callback)
        shortcode_service.add_shortcode('insert_form_field', self.form_callback)
        shortcode_service.add_shortcode('insert_image', self.image_callback)
        # shortcode_service.add_shortcode('insert_attachment_image', attachment_callback)
        shortcode_service.add_shortcode('insert_header', self.header_callback)
        shortcode_service.add_shortcode('insert_navbar', self.navbar_callback)
        shortcode_service.add_shortcode('insert_html', self.html_callback)
        shortcode_service.add_shortcode('insert_bg_color', self.header_callback)
        shortcode_service.add_shortcode('CONTINUE', lambda attrs, content=None: '')
        shortcode_service.add_shortcode('insert_trick_button', self.trick_button_callback)
        
        
        return shortcode_service.do_shortcode(content)
      
    def message_callback(self, attrs, content):
        return f'<p>{content}</p>'

    def button_callback(self, attrs, content):
        type = attrs.get("type", "submit")
        message = attrs.get("message", content)
        return f'<button type="{type}" class="cust-btn btn-secondary cranky-btn" name="text" value="{message}">{content}</button>'

    def form_callback(self, attrs, content):
        if attrs['type'] == 'input':
            return f'<input type="text" name="text">'
        
        return ''

    def image_callback(self, attrs, content):
        class_value = attrs.get('class', '')
        return f'<img src="{content}" class="{class_value}">'

    def header_callback(self, attrs, content=None):
        value = attrs.get('trigger_string', '')
        button_text = attrs.get('button_text', '')
        if not button_text:
            value = ''
        return f'<div class="top-navbar"> <div>{content}</div> <button type="submit" name="text" value="{value}">{button_text}</button>  </div>'

    def html_callback(self, attrs, content):
        return content

    def navbar_callback(self, attrs, content=None):
        button_group = ''
        for x, y in attrs.items():
            button = '''<button type="submit" name="text" value="{0}">
                <div>
                    <i class="fa fa-house"></i>
                    <span>{1}</span>
                </div>
            </button>'''
            
            button_group += button.format(y, x.capitalize())
        
        return f'<section class="interactive_navigation">{button_group}</section>'
    
    def trick_button_callback(self, attrs, content=None):
        image = attrs.get("img", "")
        hint = attrs.get("hint", "")
        
        button = f'''<button class="sub-section denial-btn" type="submit" name="text" value="{content}">
                <div class="section-header">
                    <img height="64" src="{image}">
                    <p class="section-title">{content}</p></div><div class="img-holder">
                </div>
            </button>'''
        
        if hint:
            hint = f'<p class="trick_hint"><b>Hint:</b> {hint}</p>'
        
        
        return button + hint
