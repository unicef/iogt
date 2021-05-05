from django.contrib import messages
from django.contrib.auth import get_user_model, update_session_auth_hash
from django.contrib.auth.forms import UserChangeForm
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect, render
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.views.decorators.cache import never_cache
from django.views.decorators.debug import sensitive_post_parameters
from django.views.generic import TemplateView
from django.views.generic.edit import UpdateView

from .forms import UserUpdateForm


class UserProfileView(LoginRequiredMixin, TemplateView):
    template_name = "accounts/profile.html"


class UserUpdateView(LoginRequiredMixin, UpdateView):
    form_class = UserUpdateForm
    template_name = "accounts/user_update.html"
    success_url = reverse_lazy("accounts:update")

    @method_decorator(sensitive_post_parameters())
    @method_decorator(never_cache)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

    def get_object(self, queryset=None):
        return self.request.user

    def form_valid(self, form):
        user = form.save()
        if form.changed_data:
            messages.success(self.request, "Your account details has been changed successfully!")
            update_session_auth_hash(self.request, user)
        return redirect(self.success_url)
