from django.shortcuts import render

from django.views.generic import TemplateView


# class CrankyUncleHomeView(TemplateView):
#     template_name = 'cranky_uncle/cranky_uncle.html'
#
#     def get(self, request, *args, **kwargs):
#         return render(self.template_name)

def cranky_uncle_home(request):
    template_name = 'cranky_uncle/cranky_uncle.html'
    return render(template_name)
