import re
import uuid
from datetime import datetime
from time import sleep

from django.shortcuts import redirect, get_object_or_404
from django.views.generic import TemplateView

from django.urls import reverse
import requests

from rest_framework.views import APIView

from rest_framework import permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from wagtail.core.models import Page


from .services import RapidProApiService
from .models import RapidPro, CrankyUncle
from .forms import CrankySendMessageForm
from .models import RapidPro
from .serializers import RapidProSerializer


class CrankyUncleQuizView(TemplateView):
    template_name = 'cranky_uncle/cranky_uncle_quiz.html'

    def get_context_data(self, slug, **kwargs):
        # return HttpResponse('hello')
        context = super().get_context_data()
        context['db_data'] = self.get_message_from_db(self.request)
        context['slug'] = slug
        return context

    def get_user_identifier(self, request):
        if not request.session.session_key:
            request.session.save()

        session = request.session
        session_uid = session.setdefault('session-uid', str(uuid.uuid4()))
        user = request.user.username if request.user.is_authenticated else session_uid

        return user

    def get_message_from_db(self, request):
        # Log the message
        print('showing message: ', datetime.now())
        sleep(1)

        # Get the current user or session ID
        user = RapidProApiService().get_user_identifier(request)

        # Retrieve the latest chat for the user
        chat = RapidPro.objects.filter(to=user).order_by('-created_at').first()

        if not chat:
            return None

        text = chat.text.strip()

        # Check if the message has a next message indicator, then sleep for 3 seconds
        if text.endswith('[CONTINUE]'):
            sleep(3)
            chat = RapidPro.objects.filter(to=user).order_by('-created_at').first()
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

    # def get_url_parts(self, request, *args, **kwargs):
    #     page_url = super().get_urls_parts(request=request)
    #     page_url['cranky_page'] = Page.get_url(request)
    #     return page_url
    
    def post(self, request, slug):
        # return HttpResponse(6)
        form = CrankySendMessageForm(request.POST)
        # page = get_object_or_404(Page, slug=slug)
        # cranky_page_url = Page.objects.filter(slug=slug).first().url
        cranky_page_url = request.META.get('HTTP_REFERER')
        # cranky_page_url = self.get_url_parts(request=request)
        # return HttpResponse(cranky_page_url)

        if form.is_valid():
            user = RapidProApiService().get_user_identifier(request)

            data = {
                'from': user,
                'text': form.cleaned_data['text']
            }
            
            response = RapidProApiService().send_message(data=data, slug=slug)
            # form.save()
            # return redirect(reverse('cranky:cranky-quiz'))
            return redirect('cranky:cranky-quiz', slug=slug)
            # return redirect(reverse('cranky:cranky-quiz', kwargs={'slug': slug}))
        else:
            # Handle invalid form
            # return redirect(reverse('cranky:cranky-home'))
            return redirect(cranky_page_url)


class RapidProMessageHook(APIView):
    queryset = RapidPro.objects.all()
    serializer_class = RapidProSerializer
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        data = request.data
        '''
            {
                "id": "4796",
                "text": "[POINT] 0 [/POINT] [CONTINUE]",
                "to": "admin@admin.com",
                "to_no_plus": "admin@admin.com",
                "from": "cranky_uncle",
                "from_no_plus": "cranky_uncle",
                "channel": "2d18d133-46b2-4a9c-bc70-35f373c6b445",
                "quick_replies": [
                ]
            }
        '''

        rapidpro_id = data.get('id')
        text = data.get('text')
        to = data.get('to')
        from_field = data.get('from')
        channel = data.get('channel')
        quick_replies = data.get('quick_replies')

        prev_msg = RapidPro.objects.filter(to=to).order_by('-created_at').first()

        if prev_msg:
            prev_msg_text = prev_msg.text.strip()

            if prev_msg_text.endswith('[CONTINUE]'):
                text = prev_msg_text + text
            else:
                text = text

            dic = {'rapidpro_id': rapidpro_id, 'text': text, 'quick_replies': quick_replies}
            RapidPro.objects.filter(rapidpro_id=prev_msg.rapidpro_id).update(**dic)
        else:
            RapidPro.objects.create(
                rapidpro_id=rapidpro_id,
                text=text,
                quick_replies=quick_replies,
                to=to,
                from_field=from_field,
                channel=channel,
                created_at=datetime.now(),
                updated_at=datetime.now(),
            )

        # return JsonResponse(data)

        return Response('ok', status=status.HTTP_201_CREATED)

        #TODO: add serializer check
        # serializer = self.serializer_class(data=data)
        # if serializer.is_valid():
        #     serializer.save()
        #     return Response('ok', status=status.HTTP_201_CREATED)
        # return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class DenialQuizView(TemplateView):
    template_name = 'cranky_uncle/cranky_uncle_denial.html'
    
    def get_context_data(self, slug, **kwargs):
        # return HttpResponse('hello')
        
        denial_data = [
            {
                "id": 1,
                "Name": "Fake experts",
                "trigger_string": "fake_experts",
                "fallacyOrder": 1,
                "IconUrl": "https://assets.crankyuncle.info/uploads/99cc36b4d488429bbe76aea48bb9d604.svg",
                "ParentFallacyId": False,
                "childs": []
            },
            {
                "id": 2,
                "Name": "Logical fallacies",
                "trigger_string": "logical_fallacies",
                "fallacyOrder": 2,
                "IconUrl": "https://assets.crankyuncle.info/uploads/2d5f676e64bd4d91855065e06fdf3630.svg",
                "ParentFallacyId": False,
                "childs": [
                    {
                        "id": 10,
                        "Name": "Ad Hominem",
                        "trigger_string": "fake_experts",
                        "fallacyOrder": 1,
                        "IconUrl": "https://assets.crankyuncle.info/uploads/cc23f9e75be1477cb9ad68a66e6dc6b4.svg",
                    },
                    {
                        "id": 11,
                        "Name": "Ambiguity",
                        "trigger_string": "fake_experts",
                        "fallacyOrder": 1,
                        "IconUrl": "https://assets.crankyuncle.info/uploads/f59577d9dd2e49de9646841dc8bb7ab6.svg",
                    }
                ]
            },
            {
            "id": 3,
            "Name": "Impossible expectations",
            "trigger_string": "impossible_expectations",
            "fallacyOrder": 3,
            "IconUrl": "https://assets.crankyuncle.info/uploads/8861fb3ee4634007affd479d0dcbc96c.svg",
            "ParentFallacyId": False
        },
        ]
        
        id_list = [data['id'] for data in denial_data]
        user_completed_denial_list = [1, 3]
        all_exist = all(id_value in user_completed_denial_list for id_value in id_list)
        
        context = {
            'denial_data': denial_data, 
            'slug': slug,
            'user_completed_denial': user_completed_denial_list,
            'is_all_parent_denial_completed': all_exist,
        }
        
        
        return context

class DenialQuizSendMessageView(TemplateView):
    
    def get(self, request, slug, trigger_string):
        # return HttpResponse(slug)
        core_page_id = Page.objects.filter(slug=slug).first().id
        uncle_page = CrankyUncle.objects.filter(page_ptr_id=core_page_id).first()
        url = uncle_page.channel.request_url
        # return HttpResponse(url)
        if not request.session.session_key:
            request.session.save()
        session_id = request.session.session_key
        
        user = request.user.username if request.user.is_authenticated else session_id
        
        data = {
            'from': user,
            'text': trigger_string
        }
        
        # return HttpResponse(slug)

        # rapidapi = RapidAPI()  # Initialize your RapidAPI class
        requests.post(url, data=data)

        return redirect('cranky:cranky-quiz', slug=slug)
