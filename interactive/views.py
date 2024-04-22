import re
from time import sleep
import time
from django.shortcuts import redirect, render
from django.views.generic import TemplateView
from wagtail.models import Page
from interactive.forms import MessageSendForm
from interactive.models import InteractivePage, Message
from interactive.services import RapidProApiService, ShortCodeService

class InteractiveView(TemplateView):
    template_name = 'interactive/interactive_game.html'

    def get(self, request, *args, **kwargs):
        context = super().get_context_data()
        slug = self.kwargs['slug']
        
        user = RapidProApiService().get_user_identifier(request)
        
        if not user:
            return redirect('/')
        
        self.send_message_on_language_switch(request, user, slug)
        
        context['slug'] = slug
        context['db_data'] = self.get_message_from_db(user=user)
        
        if not context['db_data']:
            return redirect('/')
        
        return render(request, self.template_name, context)

    def get_message_from_db(self, user):
        # wait a second to receive new message from rapidpro
        sleep(1)
        
        start_time = time.time()

        while True:
            # Calculate the elapsed time
            elapsed_time = time.time() - start_time

            # Break the loop if 5 seconds have elapsed
            if elapsed_time >= 5:
                break
            
            chat = Message.objects.filter(to=user).order_by('-created_at').first()
            if not chat:
                return None
            
            text = chat.text.strip()

            # Check if the message has a next message indicator
            if text.endswith('[CONTINUE]'):
                sleep(1)
            else:
                break  # Exit the loop if the message does not end with '[CONTINUE]'
        
        
        shortcode_service = ShortCodeService()
        text = shortcode_service.apply_shortcode(text)
        
        # Define the regular expression pattern
        pattern = r'\[color_scheme\s+bg-color="(?P<bg_color>[^"]+)"(\])?'
        
        # Search for matches in the input string
        match = re.search(pattern, text)

        bg_color = ''
        # Check if a match is found
        if match:
            # Extract the bg_color attributes
            bg_color = match.group('bg_color')
        
        # Remove the [bg_color] tag from the input string
        text = re.sub(pattern, '', text)

        return {
            'message': text,
            'buttons': chat.quick_replies,
            'bg_color': bg_color,
        }
        
    def send_message_on_language_switch(self, request, user, slug):
        current_lang = self.request.build_absolute_uri().split('/')[3]
        
        if request.META.get('HTTP_REFERER'):
            referer_lang = request.META.get('HTTP_REFERER').split('/')[3]
        else:
            referer_lang = current_lang
        
        
        if(referer_lang != current_lang):
            core_page_id = Page.objects.filter(slug=slug).first().id
            interactive_page = InteractivePage.objects.filter(page_ptr_id=core_page_id).first()

            data = {
                'from': user,
                'text': interactive_page.trigger_string + '_' + current_lang
            }
            
            RapidProApiService().send_message(data=data, slug=slug)
    
    def post(self, request, slug):
        form = MessageSendForm(request.POST)
        interactive_page_url = request.META.get('HTTP_REFERER')
        
        if form.is_valid():
            user = RapidProApiService().get_user_identifier(request)

            data = {
                'from': user,
                'text': form.cleaned_data['text']
            }
            
            RapidProApiService().send_message(data=data, slug=slug)
            return redirect('interactive:interactive_game', slug=slug)
        else:
            # Handle invalid form
            return redirect(interactive_page_url)