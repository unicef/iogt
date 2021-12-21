from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.shortcuts import redirect
from django.urls import reverse
from django.utils.decorators import method_decorator
from django.views.generic import UpdateView, TemplateView


@method_decorator(login_required, name='dispatch')
class UserDetailView(TemplateView):
    template_name = 'profile.html'

    def get_context_data(self, **kwargs):
        return {'user': self.request.user}


@method_decorator(login_required, name='dispatch')
class UserDetailEditView(UpdateView):
    model = User
    fields = ('first_name', 'last_name', 'email')
    template_name = 'profile_edit.html'

    def get_success_url(self):
        return reverse('user_profile_edit')

    def get_object(self, queryset=None):
        return self.request.user
