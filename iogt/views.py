from django.urls import reverse
from django.views.generic import TemplateView


def check_user_session(request):
    if request.method == "POST":
        request.session["first_time_user"] = False


def create_final_external_link(next_page):
    transition_page = reverse("external-link")
    return f"{transition_page}?next={next_page}"


class TransitionPageView(TemplateView):
    template_name = "transition-page.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data()
        context["next"] = self.request.GET.get("next", "/")
        context["prev"] = self.request.META.get("HTTP_REFERER", "/")
        return context
