import uuid
from django.contrib.auth import get_user_model
import requests
from wagtail.core.models import Page

from interactive.models import InteractivePage


class RapidProApiService(object):
    def get_user_identifier(self, request):
        if not request.session.session_key:
            request.session.save()

        user_uuid = request.session.setdefault('interactive_uuid', str(uuid.uuid4()))
 
        # Get the authenticated user
        user = request.user

        # If the user is authenticated and has no 'interactive_uuid' set, update it
        if user.is_authenticated and not user.interactive_uuid:
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