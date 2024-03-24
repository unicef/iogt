from time import sleep
from django.shortcuts import redirect, render
from django.views.generic import TemplateView
from wagtail.core.models import Page
from interactive.forms import MessageSendForm
from interactive.models import InteractivePage, Message
from interactive.services import RapidProApiService
import re

class InteractiveView(TemplateView):
    template_name = 'interactive/interactive_game.html'

    def get(self, request, *args, **kwargs):
        context = super().get_context_data()
        slug = self.kwargs['slug']
        
        user = RapidProApiService().get_user_identifier(request)
        
        if not user:
            return redirect('/')
        
        referer_lang = request.META.get('HTTP_REFERER').split('/')[3]
        current_lang = self.request.build_absolute_uri().split('/')[3]
        
        if(referer_lang != current_lang):
            core_page_id = Page.objects.filter(slug=slug).first().id
            interactive_page = InteractivePage.objects.filter(page_ptr_id=core_page_id).first()

            data = {
                'from': user,
                'text': interactive_page.trigger_string + '_' + current_lang
            }
            
            RapidProApiService().send_message(data=data, slug=slug)
        
        context['db_data'] = self.get_message_from_db(user=user)
        context['slug'] = slug
        
        
        return render(request, self.template_name, context)

    def get_message_from_db(self, user):
        # wait a second to receive new message from rapidpro
        sleep(1)

        # Retrieve the latest chat for the user
        chat = Message.objects.filter(to=user).order_by('-created_at').first()

        if not chat:
            return None

        text = chat.text.strip()

        # Check if the message has a next message indicator, then sleep for 3 seconds
        if text.endswith('[CONTINUE]'):
            sleep(3)
            chat = Message.objects.filter(to=user).order_by('-created_at').first()
            text = chat.text.strip()

        # Extract content between [MESSAGE] and [/MESSAGE]
        message_match = re.search(r'\[MESSAGE](.*?)\[\/MESSAGE]', text)
        message_content = message_match.group(1) if message_match else ''

        # Extract content between [POINT] and [/POINT]
        point_match = re.search(r'\[POINT](.*?)\[\/POINT]', text)
        point_content = point_match.group(1) if point_match else ''

        return {
            'message': text,
            'point': point_content,
            'buttons': chat.quick_replies
        }
    
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