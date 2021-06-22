from django.http import HttpResponseRedirect
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.views.generic import (
    CreateView,
    DeleteView,
    TemplateView,
    UpdateView,
)
from rest_framework.response import Response
from rest_framework.views import APIView

from .chat import ChatManager
from .forms import MessageReplyForm, NewMessageForm, NewMessageFormMultiple
from .models import Thread
from .serializers import RapidProMessageSerializer
from django.contrib.auth.decorators import login_required


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
        self.object.user_threads.filter(user=request.user).update(unread=False)
        return response


@method_decorator(login_required, name='dispatch')
class MessageCreateView(CreateView):
    """
    Create a new thread message.
    """
    template_name = "messaging/message_create.html"

    def get_form_class(self):
        if self.form_class is None:
            if self.kwargs.get("multiple", False):
                return NewMessageFormMultiple
        return NewMessageForm

    def get_initial(self):
        user_id = self.kwargs.get("user_id", None)
        if user_id is not None:
            user_id = [int(user_id)]
        elif "to_user" in self.request.GET and self.request.GET["to_user"].isdigit():
            user_id = map(int, self.request.GET.getlist("to_user"))
        if not self.kwargs.get("multiple", False) and user_id:
            user_id = user_id[0]
        return {"to_user": user_id}

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs.update({
            "user": self.request.user,
        })
        return kwargs


@method_decorator(login_required, name='dispatch')
class ThreadDeleteView(DeleteView):
    """
    Delete a thread.
    """
    model = Thread
    success_url = reverse_lazy("messaging:inbox")
    template_name = "messaging/thread_confirm_delete.html"

    def delete(self, request, *args, **kwargs):
        self.get_object().filter(user=request.user).user_threads.update(deleted=True)
        return HttpResponseRedirect(self.get_success_url())


class RapidProWebhook(APIView):
    # TODO: Add basic authentication in authentication_classes
    def post(self, request):
        serializer = RapidProMessageSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        thread_uuid = serializer.validated_data['to']
        content = serializer.validated_data['content']

        thread = Thread.objects.get(uuid=thread_uuid)
        # TODO: Decide how to treat each of these potential errors:
        # - Invalid thread UUID
        # - channel UUID mismatch

        # TODO: Stitch Messages
        # TODO: Extract attachments from messages.

        chat_manager = ChatManager(thread)
        chat_manager.create_reply(text=content)

        return Response(status=200)
