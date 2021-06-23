from django.contrib.auth import get_user_model
from django.http import HttpResponseRedirect
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.utils.decorators import method_decorator
from django.views import View
from django.views.generic import (
    DeleteView,
    TemplateView,
    DetailView,
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
class ThreadView(View):
    model = Thread
    context_object_name = 'thread'

    def get_context(self, thread, form=None):
        return {
            'thread': thread,
            'form': form or MessageReplyForm(initial={
                'thread': thread,
                'user': self.request.user,
            })}

    def get(self, request, pk):
        thread = get_object_or_404(Thread, pk=pk)
        return render(request, 'messaging/thread_detail.html', context=self.get_context(thread))

    def post(self, request, pk):
        thread = get_object_or_404(Thread, pk=pk)
        form = MessageReplyForm(data=request.POST)
        if form.is_valid():
            content = form.cleaned_data['content']

            chat_manager = ChatManager(thread)
            chat_manager.record_reply(text=content, sender=request.user, mark_unread=False)

            return redirect(reverse('messaging:thread_view', kwargs={'pk': thread.pk}))
        else:
            return render(request, 'messaging/thread_detail.html', context=self.get_context(thread, form))


@method_decorator(login_required, name='dispatch')
class MessageCreateView(View):
    """
    Create a new thread message.
    """

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
