from django.shortcuts import render
from django.urls import reverse
from django.views.generic import TemplateView

class TestView(TemplateView):
    template_name = "home/test.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data()
        context["id"] = "lorem ipsum"
        return context
        
class ServiceWorkerView(TemplateView):
    template_name = 'sw.js'
    content_type = 'application/javascript'
    name = 'sw.js'

    def get_context_data(self, **kwargs):
        return {
            'test_url': reverse('test'),
        }
