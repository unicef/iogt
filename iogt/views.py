from wagtail.core.models import Page
from django.template.response import TemplateResponse

def home(request):
    model = {
        'title': 'Hello',
        'message': 'This is a meaningless message'
    }
    return TemplateResponse(request, 'home.html', model)
