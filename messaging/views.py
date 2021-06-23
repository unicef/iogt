from django.contrib.auth import get_user_model
from django.http import HttpResponseRedirect
from django.shortcuts import render, redirect
from django.urls import reverse_lazy, reverse
from django.utils.decorators import method_decorator
from django.views import View
from django.views.generic import (
    DeleteView,
    TemplateView,
    UpdateView,
)

from .chat import ChatManager
from .forms import MessageReplyForm, NewMessageForm
from .models import Thread

from django.contrib.auth.decorators import login_required

User = get_user_model()


@method_decorator(login_required, name='dispatch')
class InboxView(TemplateView):
    """
    View inbox thread list.
    """
    template_name = "messaging/inbox.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        folder = self.kwargs.get('deleted', 'inbox')
        if folder == 'deleted':
            threads = Thread.thread_objects.of_user(self.request.user).deleted().order_by_latest()
        else:
            threads = Thread.thread_objects.of_user(self.request.user).inbox().order_by_latest()

        context.update({
            "folder": folder,
            "threads": threads,
            "unread_threads": Thread.thread_objects.of_user(self.request.user).unread().order_by_latest(),
        })
        return context


@method_decorator(login_required, name='dispatch')
class ThreadView(UpdateView):
    """
    View a single Thread or POST a reply.
    """
    model = Thread
    queryset = Thread.thread_objects
    form_class = MessageReplyForm
    context_object_name = "thread"
    template_name = "messaging/thread_detail.html"
    success_url = reverse_lazy("messaging:inbox")

    def get_queryset(self):
        qs = super().get_queryset()
        qs = qs.of_user(self.request.user).distinct()
        return qs

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs.update({
            "user": self.request.user,
            "thread": self.object
        })
        return kwargs

    def get(self, request, *args, **kwargs):
        response = super().get(request, *args, **kwargs)
        self.object.user_threads.filter(user=request.user).update(is_read=True)
        return response


@method_decorator(login_required, name='dispatch')
class MessageCreateView(View):
    """
    Create a new thread message.
    """
    template_name = "messaging/message_create.html"

    def get(self, request):
        return render(request, 'messaging/message_create.html', context={
            'form': NewMessageForm(),
        })

    def post(self, request):
        form = NewMessageForm(data=request.POST)
        if form.is_valid():
            user = request.user
            data = form.cleaned_data
            ChatManager.initiate_thread(
                sender=user, recipients=[], chatbot=data['chatbot'], subject=data['subject'], text=data['content'])

            return redirect('messaging:inbox')
        return render(request, 'messaging/message_create.html', context={
            'form': form,
        })


@method_decorator(login_required, name='dispatch')
class ThreadDeleteView(DeleteView):
    """
    Delete a thread.
    """
    model = Thread
    template_name = "messaging/thread_confirm_delete.html"

    def delete(self, request, *args, **kwargs):
        self.get_object().user_threads.filter(user=request.user).update(is_active=False)
        return HttpResponseRedirect(reverse("messaging:inbox"))
