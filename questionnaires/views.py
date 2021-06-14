from django.db.models import F
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404, render
from django.urls import reverse
from django.views import generic
from django.views.generic import FormView

from .forms import VoteForm
from .models import Choice, ChoiceVote, Poll


class IndexView(generic.ListView):
    template_name = "poll/index.html"
    context_object_name = "latest_poll_list"

    def get_queryset(self):
        return Poll.objects.order_by("-last_published_at")[:10]


class DetailView(generic.DetailView):
    model = Poll
    template_name = "poll/poll.html"


def poll_results(request, poll_id):
    poll = get_object_or_404(Poll, pk=poll_id)
    choices = Choice.objects.live().child_of(poll)

    answers = list(choices)
    total_votes = sum(answer.votes for answer in answers)

    for choice in answers:
        vote_in_percentage = 0
        if choice.votes > 0:
            vote_in_percentage = int(choice.votes * 100 / total_votes)
        choice.percentage = vote_in_percentage

    context = {
        "poll": poll,
        "total_votes": total_votes,
        "answers": sorted(
            [answer for answer in answers], key=lambda a: a.percentage, reverse=True
        ),
    }
    return render(
        request,
        "poll/results.html",
        context,
    )


class VoteFormView(FormView):
    template_name = "poll/poll.html"
    form_class = VoteForm

    # TODO: vote after login doesn't work

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        poll_id = self.kwargs.get("poll_id")
        poll = get_object_or_404(Poll, pk=poll_id)
        context.update({"poll": poll})
        return context

    def form_valid(self, form):
        poll_id = self.kwargs.get("poll_id")
        poll = get_object_or_404(Poll, pk=poll_id)
        if self.request.user.is_authenticated:
            user = self.request.user
            obj, created = ChoiceVote.objects.get_or_create(poll=poll, user=user)
        else:
            obj = ChoiceVote.objects.create(poll=poll, user=None)

        if obj:
            selected_choice = form.cleaned_data["choice"]
            for choice_pk in selected_choice:
                Choice.objects.filter(pk=choice_pk).update(votes=F("votes") + 1)
                choice = Choice.objects.get(pk=choice_pk)
                obj.choice.add(choice)
                choice.choice_votes.add(obj)
                choice.save()
        return HttpResponseRedirect(reverse("results", args=(poll_id,)))
