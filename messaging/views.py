from django.contrib import messages
from django.contrib.auth import get_user_model
from django.http import HttpResponseRedirect
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.utils.decorators import method_decorator
from django.views import View
from django.views.generic import (DeleteView, TemplateView, )

from .chat import ChatManager
from .forms import MessageReplyForm, NewMessageForm
from .models import Thread, UserThread

from django.contrib.auth.decorators import login_required

User = get_user_model()


@method_decorator(login_required, name='dispatch')
class InboxIndexView(TemplateView):
    template_name = 'messaging/inbox_index.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        folder = self.kwargs.get('deleted', 'inbox')
        if folder == 'deleted':
            threads = Thread.thread_objects.of_user(self.request.user).deleted().order_by_latest()
        else:
            threads = Thread.thread_objects.of_user(self.request.user).inbox().order_by_latest()

        context.update({
            "folder": folder,
            "threads": threads.prefetch_related('messages'),
            "user_threads": UserThread.objects.filter(user=self.request.user, is_active=True).order_by(
                '-thread__last_message_at'),
            "unread_threads": Thread.thread_objects.of_user(self.request.user).unread().order_by_latest(),
        })
        return context


@method_decorator(login_required, name='dispatch')
class ThreadView(View):

    def get_context(self, thread):
        last_message = thread.messages.last()
        return {
            'thread': thread,
            'last_message_id': last_message.id if last_message else None,
            'user': self.request.user
        }

    def get(self, request, thread_id):
        thread = get_object_or_404(Thread, pk=thread_id)
        thread.mark_read(request.user)
        return render(request, 'messaging/message_detail.html', context=self.get_context(thread))

    def post(self, request, thread_id):
        thread = get_object_or_404(Thread, pk=thread_id)
        form = MessageReplyForm(data=request.POST)
        if form.is_valid():
            text = form.cleaned_data['text']

            chat_manager = ChatManager(thread)
            chat_manager.record_reply(text=text, sender=request.user, mark_unread=False)

            return redirect(reverse('messaging:thread', kwargs={'thread_id': thread.pk}))
        else:
            return render(request, 'messaging/message_detail.html', context=self.get_context(thread, form))


@method_decorator(login_required, name='dispatch')
class MessageCreateView(View):
    """
    Create a new thread message.
    """

    def post(self, request):
        form = NewMessageForm(data=request.POST)
        if form.is_valid():
            user = request.user
            data = form.cleaned_data
            ChatManager.initiate_thread(
                sender=user, recipients=[], chatbot=data['chatbot'], subject=data['subject'], text=data['text'])

            return redirect('messaging:inbox')

        messages.add_message(request, messages.ERROR, 'Can\'t connect with bot.')
        return redirect(request.META.get('HTTP_REFERER'))


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
