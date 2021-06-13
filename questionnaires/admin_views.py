import csv
from collections import OrderedDict

from django.http.response import HttpResponse
from django.shortcuts import get_object_or_404, render
from django.views.generic.edit import FormView

from questionnaires.models import Poll


class PollResultsAdminView(FormView):
    def get(self, request, *args, **kwargs):
        parent = kwargs["parent"]
        poll = get_object_or_404(Poll, pk=parent)

        data_headings = ["Submission Date", "Answer", "User"]
        data_rows = []

        votes = poll.choicevote_set.all()

        for vote in votes:
            data_rows.append(
                OrderedDict(
                    {
                        "submission_date": vote.submission_date,
                        "answer": vote.answer,
                        "user": vote.user,
                    }
                )
            )

        action = request.GET.get("action")
        if action == "download":
            return self.send_csv(poll.title, data_headings, data_rows)

        context = {
            "page_title": poll.title,
            "data_headings": ["Submission Date", "Answer", "User"],
            "data_rows": data_rows,
        }

        return render(request, "poll/admin-results.html", context)

    def send_csv(self, poll_title, data_headings, data_rows):
        response = HttpResponse(content_type="text/csv")
        response[
            "Content-Disposition"
        ] = 'attachment;filename="poll-{0}-results.csv"'.format(poll_title)

        writer = csv.writer(response)
        writer.writerow(data_headings)

        for item in data_rows:
            writer.writerow(item.values())

        return response
